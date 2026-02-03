"""
Compliance Service - Pharmacy-specific safety rules
Expiry checking, prescription flags, and FIFO enforcement
"""
from typing import Tuple, Optional
from datetime import date
from database.models import Product


class ComplianceService:
    """Business logic for pharmacy compliance rules"""
    
    def check_product_sellable(self, product: Product) -> Tuple[bool, str, str]:
        """
        Check if a product can be sold
        Returns: (can_sell, warning_type, message)
        
        Warning types:
        - 'expired': Product is expired (BLOCK)
        - 'out_of_stock': No stock available (BLOCK)
        - 'prescription': Requires prescription (WARN - requires acknowledgment)
        - 'low_stock': Stock is low (INFO only)
        - 'expiring_soon': Will expire soon (INFO only)
        - None: All clear
        """
        # Check expiry - BLOCKING
        if product.is_expired:
            return False, 'expired', f"BLOCKED: {product.name} is EXPIRED (Exp: {product.expiry_date})"
        
        # Check stock - BLOCKING
        if product.is_out_of_stock:
            return False, 'out_of_stock', f"BLOCKED: {product.name} is OUT OF STOCK"
        
        # Check prescription requirement - WARNING (requires acknowledgment)
        if product.prescription_required:
            return True, 'prescription', f"WARNING: {product.name} requires a PRESCRIPTION. Proceed with sale?"
        
        # Check low stock - INFO
        if product.is_low_stock:
            return True, 'low_stock', f"INFO: {product.name} is running low (Stock: {product.stock_quantity})"
        
        # Check expiring soon (within 30 days)
        if product.expiry_date:
            days_until_expiry = (product.expiry_date - date.today()).days
            if 0 < days_until_expiry <= 30:
                return True, 'expiring_soon', f"INFO: {product.name} expires in {days_until_expiry} days"
        
        # All clear
        return True, None, ""
    
    def validate_sale_item(self, product: Product, quantity: int) -> Tuple[bool, str]:
        """
        Validate a specific sale item
        Returns: (is_valid, message)
        """
        # Check if product exists
        if not product:
            return False, "Product not found"
        
        # Check expiry
        if product.is_expired:
            return False, f"Cannot sell expired product: {product.name}"
        
        # Check stock
        if product.stock_quantity < quantity:
            return False, f"Insufficient stock. Available: {product.stock_quantity}, Requested: {quantity}"
        
        return True, ""
    
    def get_batch_for_sale(self, product: Product) -> Optional[str]:
        """
        Get the batch number to use for sale (FIFO - earliest expiry first)
        In this implementation, we assume one batch per product record.
        For more complex scenarios, this would query a batches table.
        """
        # Simple implementation: return product's batch number
        return product.batch_number
    
    def format_compliance_message(self, warning_type: str, message: str) -> dict:
        """Format compliance message for UI display"""
        severity_map = {
            'expired': 'error',
            'out_of_stock': 'error',
            'prescription': 'warning',
            'low_stock': 'info',
            'expiring_soon': 'info'
        }
        
        return {
            'type': warning_type,
            'severity': severity_map.get(warning_type, 'info'),
            'message': message,
            'requires_action': warning_type in ['expired', 'out_of_stock', 'prescription']
        }


# Global service instance
compliance_service = ComplianceService()
