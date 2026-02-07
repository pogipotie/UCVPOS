"""
Product Repository - CRUD operations for products
Optimized for fast barcode lookup (<50ms)
"""
from typing import List, Optional
from datetime import date
from database.connection import db
from database.models import Product


class ProductRepository:
    """Data access layer for products"""
    
    def get_by_barcode(self, barcode: str) -> Optional[Product]:
        """
        Fast barcode lookup using indexed query
        Target: <50ms response time
        """
        cursor = db.execute(
            "SELECT * FROM products WHERE barcode = ?",
            (barcode,)
        )
        row = cursor.fetchone()
        return self._row_to_product(row) if row else None
    
    def get_by_id(self, product_id: int) -> Optional[Product]:
        """Get product by ID"""
        cursor = db.execute(
            "SELECT * FROM products WHERE id = ?",
            (product_id,)
        )
        row = cursor.fetchone()
        return self._row_to_product(row) if row else None
    
    def get_all(self, limit: int = 1000, offset: int = 0) -> List[Product]:
        """Get all products with pagination"""
        cursor = db.execute(
            "SELECT * FROM products ORDER BY name LIMIT ? OFFSET ?",
            (limit, offset)
        )
        return [self._row_to_product(row) for row in cursor.fetchall()]
    
    def search(self, query: str, limit: int = 50) -> List[Product]:
        """Search products by name or barcode"""
        search_term = f"%{query}%"
        cursor = db.execute(
            """SELECT * FROM products 
               WHERE name LIKE ? OR barcode LIKE ?
               ORDER BY name LIMIT ?""",
            (search_term, search_term, limit)
        )
        return [self._row_to_product(row) for row in cursor.fetchall()]
    
    def get_low_stock(self) -> List[Product]:
        """Get products below minimum stock level"""
        cursor = db.execute(
            """SELECT * FROM products 
               WHERE stock_quantity <= min_stock_level
               ORDER BY stock_quantity ASC"""
        )
        return [self._row_to_product(row) for row in cursor.fetchall()]
    
    def get_expired(self) -> List[Product]:
        """Get expired products"""
        today = date.today().isoformat()
        cursor = db.execute(
            """SELECT * FROM products 
               WHERE expiry_date IS NOT NULL AND expiry_date < ?
               ORDER BY expiry_date ASC""",
            (today,)
        )
        return [self._row_to_product(row) for row in cursor.fetchall()]
    
    def get_expiring_soon(self, days: int = 30) -> List[Product]:
        """Get products expiring within specified days"""
        from datetime import timedelta
        today = date.today()
        future_date = (today + timedelta(days=days)).isoformat()
        cursor = db.execute(
            """SELECT * FROM products 
               WHERE expiry_date IS NOT NULL 
               AND expiry_date >= ? AND expiry_date <= ?
               ORDER BY expiry_date ASC""",
            (today.isoformat(), future_date)
        )
        return [self._row_to_product(row) for row in cursor.fetchall()]
    
    def create(self, product: Product) -> int:
        """Create a new product, returns the new ID"""
        cursor = db.execute(
            """INSERT INTO products 
               (barcode, name, price, cost_price, stock_quantity, min_stock_level, 
                batch_number, expiry_date, prescription_required)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                product.barcode,
                product.name,
                product.price,
                product.cost_price,
                product.stock_quantity,
                product.min_stock_level,
                product.batch_number,
                product.expiry_date.isoformat() if product.expiry_date else None,
                1 if product.prescription_required else 0
            )
        )
        db.commit()
        return cursor.lastrowid
    
    def update(self, product: Product) -> bool:
        """Update an existing product"""
        if not product.id:
            return False
        db.execute(
            """UPDATE products SET
               barcode = ?, name = ?, price = ?, cost_price = ?, stock_quantity = ?,
               min_stock_level = ?, batch_number = ?, expiry_date = ?,
               prescription_required = ?, updated_at = CURRENT_TIMESTAMP
               WHERE id = ?""",
            (
                product.barcode,
                product.name,
                product.price,
                product.cost_price,
                product.stock_quantity,
                product.min_stock_level,
                product.batch_number,
                product.expiry_date.isoformat() if product.expiry_date else None,
                1 if product.prescription_required else 0,
                product.id
            )
        )
        db.commit()
        return True
    
    def update_stock(self, product_id: int, quantity_change: int) -> bool:
        """Update stock quantity (positive to add, negative to deduct)"""
        db.execute(
            """UPDATE products SET 
               stock_quantity = stock_quantity + ?,
               updated_at = CURRENT_TIMESTAMP
               WHERE id = ?""",
            (quantity_change, product_id)
        )
        db.commit()
        return True
    
    def delete(self, product_id: int) -> bool:
        """Delete a product (use with caution)"""
        db.execute("DELETE FROM products WHERE id = ?", (product_id,))
        db.commit()
        return True
    
    def count(self) -> int:
        """Get total product count"""
        cursor = db.execute("SELECT COUNT(*) as count FROM products")
        return cursor.fetchone()['count']
    
    def _row_to_product(self, row) -> Product:
        """Convert database row to Product object"""
        expiry = None
        if row['expiry_date']:
            try:
                # MySQL returns date/datetime objects directly, SQLite returns strings
                if isinstance(row['expiry_date'], date):
                    expiry = row['expiry_date']
                else:
                    expiry = date.fromisoformat(str(row['expiry_date']))
            except (ValueError, TypeError):
                pass
        
        return Product(
            id=row['id'],
            barcode=row['barcode'],
            name=row['name'],
            price=float(row['price']),  # Ensure float for MySQL Decimal
            cost_price=float(row.get('cost_price', 0.0) or 0.0), # Safer fetch
            stock_quantity=row['stock_quantity'],
            min_stock_level=row['min_stock_level'],
            batch_number=row['batch_number'],
            expiry_date=expiry,
            prescription_required=bool(row['prescription_required']),
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )


# Global repository instance
product_repo = ProductRepository()
