"""
Sales Service - Complete sales flow management
Handles cart operations, checkout, and transaction safety
"""
from typing import List, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime
from database.models import Product, CartItem, Sale, SaleItem, Payment
from repositories.product_repo import product_repo
from repositories.sales_repo import sales_repo
from repositories.payment_repo import payment_repo
from repositories.audit_repo import audit_repo, void_log_repo
from services.inventory_service import inventory_service
from services.compliance_service import compliance_service
from database.models import VoidLog


@dataclass
class SaleSession:
    """Represents an active sale session"""
    cart: List[CartItem] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)
    cashier_name: Optional[str] = None
    discount_type: Optional[str] = None  # 'SC', 'PWD', or None
    discount_id: Optional[str] = None    # SC/PWD ID number
    
    @property
    def total(self) -> float:
        """Calculate cart total (VAT-inclusive, prices already include VAT)"""
        return sum(item.subtotal for item in self.cart)
    
    @property
    def is_discounted(self) -> bool:
        """Check if SC/PWD discount is applied"""
        return self.discount_type in ('SC', 'PWD')
    
    @property
    def vat_exempt_total(self) -> float:
        """VAT-exempt price (for SC/PWD: remove VAT first)"""
        return self.total / 1.12
    
    @property
    def sc_pwd_discount(self) -> float:
        """20% SC/PWD discount amount (applied to VAT-exempt price)"""
        if not self.is_discounted:
            return 0.0
        return self.vat_exempt_total * 0.20
    
    @property
    def final_total(self) -> float:
        """Final amount to pay after SC/PWD discount"""
        if self.is_discounted:
            return self.vat_exempt_total - self.sc_pwd_discount
        return self.total
    
    @property
    def vat_amount(self) -> float:
        """Extract VAT from total (VAT-inclusive calculation)
        For SC/PWD: VAT is exempt (returns 0)
        """
        if self.is_discounted:
            return 0.0  # VAT exempt for SC/PWD
        from services.settings_service import settings_service
        tax_rate = settings_service.get('financial', 'tax_rate') or 12.0
        if tax_rate <= 0:
            return 0.0
        return self.total - (self.total / (1 + tax_rate / 100))
    
    @property
    def net_amount(self) -> float:
        """Amount without VAT (for receipt display)"""
        return self.total - self.vat_amount
    
    @property
    def item_count(self) -> int:
        """Get total number of items"""
        return sum(item.quantity for item in self.cart)
    
    def find_cart_item(self, product_id: int) -> Optional[CartItem]:
        """Find item in cart by product ID"""
        for item in self.cart:
            if item.product.id == product_id:
                return item
        return None


class SalesService:
    """Business logic for sales operations"""
    
    def __init__(self):
        self.current_session: Optional[SaleSession] = None
    
    def start_new_sale(self, cashier_name: str = None) -> SaleSession:
        """Start a new sale session"""
        self.current_session = SaleSession(cashier_name=cashier_name)
        return self.current_session
    
    def get_current_session(self) -> Optional[SaleSession]:
        """Get the current sale session"""
        return self.current_session
    
    def add_by_barcode(self, barcode: str, quantity: int = 1) -> Tuple[bool, str, Optional[dict]]:
        """
        Add product to cart by barcode scan
        Returns: (success, message, compliance_warning)
        """
        if not self.current_session:
            self.start_new_sale()
        
        # Fast lookup
        product = product_repo.get_by_barcode(barcode)
        if not product:
            return False, f"Product not found: {barcode}", None
        
        # Check compliance
        can_sell, warning_type, warning_msg = compliance_service.check_product_sellable(product)
        
        # If trying to add multiple, check stock first
        if quantity > product.stock_quantity:
             return False, f"Insufficient stock. Available: {product.stock_quantity}", None
        
        compliance_warning = None
        if warning_type:
            compliance_warning = compliance_service.format_compliance_message(
                warning_type, warning_msg
            )
        
        # Block if cannot sell
        if not can_sell:
            return False, warning_msg, compliance_warning
        
        # Check if already in cart
        existing = self.current_session.find_cart_item(product.id)
        if existing:
            # Check if we have enough stock for additional quantity
            new_qty = existing.quantity + quantity
            if new_qty > product.stock_quantity:
                return False, f"Cannot add more. Stock limit: {product.stock_quantity}", None
            existing.quantity = new_qty
        else:
            # Add new item
            self.current_session.cart.append(CartItem(product=product, quantity=quantity))
        
        msg = f"Added: {product.name}"
        if quantity > 1:
            msg += f" (x{quantity})"
            
        return True, msg, compliance_warning
    
    def update_quantity(self, product_id: int, new_quantity: int) -> Tuple[bool, str]:
        """Update quantity of an item in cart"""
        if not self.current_session:
            return False, "No active sale"
        
        if new_quantity < 1:
            return self.remove_item(product_id)
        
        item = self.current_session.find_cart_item(product_id)
        if not item:
            return False, "Item not in cart"
        
        # Validate stock
        if new_quantity > item.product.stock_quantity:
            return False, f"Cannot exceed stock. Available: {item.product.stock_quantity}"
        
        item.quantity = new_quantity
        return True, f"Quantity updated to {new_quantity}"
    
    def remove_item(self, product_id: int) -> Tuple[bool, str]:
        """Remove an item from cart"""
        if not self.current_session:
            return False, "No active sale"
        
        for i, item in enumerate(self.current_session.cart):
            if item.product.id == product_id:
                removed = self.current_session.cart.pop(i)
                return True, f"Removed: {removed.product.name}"
        
        return False, "Item not in cart"
    
    def clear_cart(self) -> Tuple[bool, str]:
        """Clear all items from cart"""
        if not self.current_session:
            return False, "No active sale"
        
        self.current_session.cart.clear()
        return True, "Cart cleared"
    
    def calculate_change(self, amount_tendered: float) -> float:
        """Calculate change for cash payment"""
        if not self.current_session:
            return 0.0
        return amount_tendered - self.current_session.total
    
    def complete_sale(self, amount_tendered: float) -> Tuple[bool, str, Optional[int]]:
        """
        Complete the sale and save to database
        Stock is deducted only after successful save
        Returns: (success, message, sale_id)
        """
        if not self.current_session:
            return False, "No active sale", None
        
        if not self.current_session.cart:
            return False, "Cart is empty", None
        
        if amount_tendered < self.current_session.total:
            return False, "Insufficient payment amount", None
        
        try:
            # Prepare sale record
            sale = Sale(
                total_amount=self.current_session.total,
                status="completed",
                cashier_name=self.current_session.cashier_name
            )
            
            # Prepare sale items
            sale_items = []
            for cart_item in self.current_session.cart:
                sale_item = SaleItem(
                    product_id=cart_item.product.id,
                    product_name=cart_item.product.name,
                    quantity=cart_item.quantity,
                    unit_price=cart_item.product.price,
                    subtotal=cart_item.subtotal,
                    batch_number=compliance_service.get_batch_for_sale(cart_item.product)
                )
                sale_items.append(sale_item)
            
            # Save sale (transactional)
            sale_id = sales_repo.create_sale(sale, sale_items)
            
            # Record payment
            change = amount_tendered - self.current_session.total
            payment = Payment(
                sale_id=sale_id,
                amount_tendered=amount_tendered,
                change_given=change,
                payment_method="cash"
            )
            payment_repo.create(payment)
            
            # Deduct stock (only after successful save)
            for cart_item in self.current_session.cart:
                inventory_service.deduct_stock(cart_item.product.id, cart_item.quantity)
            
            # Log the sale
            audit_repo.log_action(
                action="SALE_COMPLETE",
                entity_type="sale",
                entity_id=sale_id,
                details=f"Sale completed. Total: {self.current_session.total:.2f}, Items: {len(sale_items)}"
            )
            
            # Clear the session
            self.current_session = None
            
            return True, "Sale completed successfully", sale_id
            
        except Exception as e:
            return False, f"Error completing sale: {str(e)}", None
    
    def void_sale(self, sale_id: int, reason: str, voided_by: str = None) -> Tuple[bool, str]:
        """
        Void a completed sale
        Restores stock and creates void log
        """
        sale = sales_repo.get_by_id(sale_id)
        if not sale:
            return False, "Sale not found"
        
        if sale.is_voided:
            return False, "Sale is already voided"
        
        try:
            # Create void log (immutable record)
            void_log = VoidLog(
                sale_id=sale_id,
                reason=reason,
                voided_by=voided_by,
                original_total=sale.total_amount
            )
            void_log_repo.create(void_log)
            
            # Mark sale as voided
            sales_repo.void_sale(sale_id, reason, voided_by)
            
            # Restore stock
            for item in sale.items:
                inventory_service.restore_stock(item.product_id, item.quantity)
            
            # Audit log
            audit_repo.log_action(
                action="SALE_VOID",
                entity_type="sale",
                entity_id=sale_id,
                details=f"Sale voided. Reason: {reason}"
            )
            
            return True, "Sale voided successfully"
            
        except Exception as e:
            return False, f"Error voiding sale: {str(e)}"
    
    def get_sale_history(self, limit: int = 50) -> List[Sale]:
        """Get recent sales"""
        return sales_repo.get_recent_sales(limit)
    
    def cancel_current_sale(self) -> Tuple[bool, str]:
        """Cancel the current sale without saving"""
        if not self.current_session:
            return False, "No active sale"
        
        self.current_session = None
        return True, "Sale cancelled"


# Global service instance
sales_service = SalesService()
