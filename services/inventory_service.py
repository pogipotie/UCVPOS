"""
Inventory Service - Stock management and product operations
Includes FIFO batch handling and expiry checking
"""
from typing import List, Optional, Tuple
from datetime import date
from database.models import Product
from repositories.product_repo import product_repo
from repositories.audit_repo import audit_repo


class InventoryService:
    """Business logic for inventory management"""
    
    def add_product(self, product: Product) -> Tuple[bool, str, int]:
        """
        Add a new product to inventory
        Returns: (success, message, product_id)
        """
        # Validate barcode uniqueness
        existing = product_repo.get_by_barcode(product.barcode)
        if existing:
            return False, f"Barcode '{product.barcode}' already exists", 0
        
        # Validate required fields
        if not product.barcode or not product.name:
            return False, "Barcode and name are required", 0
        
        if product.price < 0:
            return False, "Price cannot be negative", 0
        
        try:
            product_id = product_repo.create(product)
            audit_repo.log_action(
                action="CREATE",
                entity_type="product",
                entity_id=product_id,
                details=f"Added product: {product.name} (Barcode: {product.barcode})"
            )
            return True, "Product added successfully", product_id
        except Exception as e:
            return False, f"Error adding product: {str(e)}", 0
    
    def update_product(self, product: Product) -> Tuple[bool, str]:
        """Update an existing product"""
        if not product.id:
            return False, "Product ID is required"
        
        # Check barcode uniqueness (excluding current product)
        existing = product_repo.get_by_barcode(product.barcode)
        if existing and existing.id != product.id:
            return False, f"Barcode '{product.barcode}' is used by another product"
        
        try:
            product_repo.update(product)
            audit_repo.log_action(
                action="UPDATE",
                entity_type="product",
                entity_id=product.id,
                details=f"Updated product: {product.name}"
            )
            return True, "Product updated successfully"
        except Exception as e:
            return False, f"Error updating product: {str(e)}"
    
    def delete_product(self, product_id: int) -> Tuple[bool, str]:
        """Delete a product from inventory"""
        product = product_repo.get_by_id(product_id)
        if not product:
            return False, "Product not found"
        
        try:
            product_repo.delete(product_id)
            audit_repo.log_action(
                action="DELETE",
                entity_type="product",
                entity_id=product_id,
                details=f"Deleted product: {product.name}"
            )
            return True, "Product deleted successfully"
        except Exception as e:
            error_msg = str(e)
            # Check for foreign key constraint (product has sales history)
            if '1451' in error_msg or 'foreign key constraint' in error_msg.lower():
                return False, f"Cannot delete '{product.name}' - it has sales history.\nProducts with transactions cannot be deleted to preserve records."
            return False, f"Error deleting product: {error_msg}"
    
    def adjust_stock(self, product_id: int, new_quantity: int, 
                     reason: str = None) -> Tuple[bool, str]:
        """Manually adjust stock quantity"""
        product = product_repo.get_by_id(product_id)
        if not product:
            return False, "Product not found"
        
        old_quantity = product.stock_quantity
        change = new_quantity - old_quantity
        
        try:
            product.stock_quantity = new_quantity
            product_repo.update(product)
            audit_repo.log_action(
                action="STOCK_ADJUST",
                entity_type="product",
                entity_id=product_id,
                details=f"Stock adjusted from {old_quantity} to {new_quantity}. Reason: {reason or 'Not specified'}"
            )
            return True, f"Stock adjusted from {old_quantity} to {new_quantity}"
        except Exception as e:
            return False, f"Error adjusting stock: {str(e)}"
    
    def deduct_stock(self, product_id: int, quantity: int) -> Tuple[bool, str]:
        """Deduct stock after a sale"""
        product = product_repo.get_by_id(product_id)
        if not product:
            return False, "Product not found"
        
        if product.stock_quantity < quantity:
            return False, f"Insufficient stock. Available: {product.stock_quantity}"
        
        try:
            product_repo.update_stock(product_id, -quantity)
            return True, "Stock deducted"
        except Exception as e:
            return False, f"Error deducting stock: {str(e)}"
    
    def restore_stock(self, product_id: int, quantity: int) -> Tuple[bool, str]:
        """Restore stock (e.g., after void)"""
        try:
            product_repo.update_stock(product_id, quantity)
            return True, "Stock restored"
        except Exception as e:
            return False, f"Error restoring stock: {str(e)}"
    
    def lookup_by_barcode(self, barcode: str) -> Optional[Product]:
        """Fast barcode lookup for POS"""
        return product_repo.get_by_barcode(barcode)
    
    def search_products(self, query: str) -> List[Product]:
        """Search products by name or barcode"""
        return product_repo.search(query)
    
    def get_all_products(self, limit: int = 1000, offset: int = 0) -> List[Product]:
        """Get all products with pagination"""
        return product_repo.get_all(limit, offset)
    
    def get_low_stock_products(self) -> List[Product]:
        """Get products that need restocking"""
        return product_repo.get_low_stock()
    
    def get_expired_products(self) -> List[Product]:
        """Get all expired products"""
        return product_repo.get_expired()
    
    def get_expiring_soon(self, days: int = 30) -> List[Product]:
        """Get products expiring within days"""
        return product_repo.get_expiring_soon(days)
    
    def get_product_count(self) -> int:
        """Get total product count"""
        return product_repo.count()

    def get_all_search_terms(self) -> List[str]:
        """Get all product names and barcodes for autocomplete"""
        products = product_repo.get_all(limit=10000)
        terms = [p.name for p in products]
        terms.extend([p.barcode for p in products if p.barcode])
        return terms


# Global service instance
inventory_service = InventoryService()
