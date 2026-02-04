"""
Sales Repository - CRUD operations for sales and sale items
"""
from typing import List, Optional, Tuple
from datetime import datetime, date
from database.connection import db
from database.models import Sale, SaleItem


class SalesRepository:
    """Data access layer for sales transactions"""
    
    def create_sale(self, sale: Sale, items: List[SaleItem]) -> int:
        """
        Create a new sale with items in a transaction
        Returns the new sale ID
        """
        try:
            # Insert sale header
            cursor = db.execute(
                """INSERT INTO sales (total_amount, status, cashier_name)
                   VALUES (?, ?, ?)""",
                (sale.total_amount, sale.status, sale.cashier_name)
            )
            sale_id = cursor.lastrowid
            
            # Insert sale items
            for item in items:
                db.execute(
                    """INSERT INTO sale_items 
                       (sale_id, product_id, product_name, quantity, 
                        unit_price, subtotal, batch_number)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (
                        sale_id,
                        item.product_id,
                        item.product_name,
                        item.quantity,
                        item.unit_price,
                        item.subtotal,
                        item.batch_number
                    )
                )
            
            db.commit()
            return sale_id
        except Exception as e:
            db.rollback()
            raise e
    
    def get_by_id(self, sale_id: int) -> Optional[Sale]:
        """Get a sale by ID with its items"""
        cursor = db.execute(
            "SELECT * FROM sales WHERE id = ?",
            (sale_id,)
        )
        row = cursor.fetchone()
        if not row:
            return None
        
        sale = self._row_to_sale(row)
        sale.items = self.get_sale_items(sale_id)
        return sale
    
    def get_sale_items(self, sale_id: int) -> List[SaleItem]:
        """Get all items for a sale"""
        cursor = db.execute(
            "SELECT * FROM sale_items WHERE sale_id = ?",
            (sale_id,)
        )
        return [self._row_to_sale_item(row) for row in cursor.fetchall()]
    
    def get_sales_by_date(self, date: date, cashier_name: str = None) -> List[Sale]:
        """Get all sales for a specific date, optionally filtered by cashier"""
        start = f"{date.isoformat()} 00:00:00"
        end = f"{date.isoformat()} 23:59:59"
        
        query = "SELECT * FROM sales WHERE sale_date BETWEEN ? AND ?"
        params = [start, end]
        
        if cashier_name:
            query += " AND cashier_name = ?"
            params.append(cashier_name)
            
        query += " ORDER BY sale_date DESC"
        
        cursor = db.execute(query, tuple(params))
        return [self._row_to_sale(row) for row in cursor.fetchall()]
    
    def get_sales_by_date_range(self, start_date: date, end_date: date, cashier_name: str = None) -> List[Sale]:
        """Get sales within a date range, optionally filtered by cashier"""
        start = f"{start_date.isoformat()} 00:00:00"
        end = f"{end_date.isoformat()} 23:59:59"
        
        query = "SELECT * FROM sales WHERE sale_date BETWEEN ? AND ?"
        params = [start, end]
        
        if cashier_name:
            query += " AND cashier_name = ?"
            params.append(cashier_name)
            
        query += " ORDER BY sale_date DESC"
        
        cursor = db.execute(query, tuple(params))
        return [self._row_to_sale(row) for row in cursor.fetchall()]
    
    def get_recent_sales(self, limit: int = 50) -> List[Sale]:
        """Get most recent sales"""
        cursor = db.execute(
            "SELECT * FROM sales ORDER BY sale_date DESC LIMIT ?",
            (limit,)
        )
        return [self._row_to_sale(row) for row in cursor.fetchall()]
    
    def get_daily_summary(self, date: date, cashier_name: str = None) -> dict:
        """Get daily sales summary, optionally filtered by cashier"""
        start = f"{date.isoformat()} 00:00:00"
        end = f"{date.isoformat()} 23:59:59"
        
        query = """SELECT 
               COUNT(*) as total_transactions,
               SUM(CASE WHEN status = 'completed' THEN total_amount ELSE 0 END) as total_sales,
               SUM(CASE WHEN status = 'voided' THEN 1 ELSE 0 END) as voided_count
               FROM sales 
               WHERE sale_date BETWEEN ? AND ?"""
        params = [start, end]
        
        if cashier_name:
            query += " AND cashier_name = ?"
            params.append(cashier_name)
            
        cursor = db.execute(query, tuple(params))
        row = cursor.fetchone()
        
        return {
            'date': date,
            'total_transactions': row['total_transactions'] or 0,
            'total_sales': row['total_sales'] or 0.0,
            'voided_count': row['voided_count'] or 0
        }
    
    def get_monthly_summary(self, year: int, month: int) -> dict:
        """Get monthly sales summary"""
        # Get first and last day of month
        from calendar import monthrange
        last_day = monthrange(year, month)[1]
        start = f"{year}-{month:02d}-01 00:00:00"
        end = f"{year}-{month:02d}-{last_day} 23:59:59"
        
        cursor = db.execute(
            """SELECT 
               COUNT(*) as total_transactions,
               SUM(CASE WHEN status = 'completed' THEN total_amount ELSE 0 END) as total_sales,
               SUM(CASE WHEN status = 'voided' THEN 1 ELSE 0 END) as voided_count
               FROM sales 
               WHERE sale_date BETWEEN ? AND ?""",
            (start, end)
        )
        row = cursor.fetchone()
        return {
            'year': year,
            'month': month,
            'total_transactions': row['total_transactions'] or 0,
            'total_sales': row['total_sales'] or 0.0,
            'voided_count': row['voided_count'] or 0
        }

    def get_sales_trend(self, days: int = 7) -> List[dict]:
        """Get sales total for the last n days"""
        # SQLite usage: date('now', '-7 days')
        cursor = db.execute(
            """SELECT DATE(sale_date) as day, 
               SUM(total_amount) as total 
               FROM sales 
               WHERE status = 'completed' 
               AND sale_date >= date('now', ?) 
               GROUP BY day 
               ORDER BY day ASC""",
            (f'-{days} days',)
        )
        return [{'date': row['day'], 'total': row['total']} for row in cursor.fetchall()]

    def get_top_products(self, limit: int = 5) -> List[dict]:
        """Get best selling products"""
        cursor = db.execute(
            """SELECT product_name, SUM(quantity) as qty
               FROM sale_items
               JOIN sales ON sale_items.sale_id = sales.id
               WHERE sales.status = 'completed'
               GROUP BY product_name
               ORDER BY qty DESC
               LIMIT ?""",
            (limit,)
        )
        return [{'name': row['product_name'], 'quantity': row['qty']} for row in cursor.fetchall()]
    
    def void_sale(self, sale_id: int, reason: str, voided_by: str = None) -> bool:
        """
        Void a sale (does not delete, just marks as voided)
        """
        try:
            db.execute(
                """UPDATE sales SET 
                   status = 'voided',
                   voided_at = CURRENT_TIMESTAMP,
                   void_reason = ?
                   WHERE id = ?""",
                (reason, sale_id)
            )
            db.commit()
            return True
        except Exception:
            db.rollback()
            return False
    
    def _row_to_sale(self, row) -> Sale:
        """Convert database row to Sale object"""
        return Sale(
            id=row['id'],
            sale_date=row['sale_date'],
            total_amount=row['total_amount'],
            status=row['status'],
            cashier_name=row['cashier_name'],
            voided_at=row['voided_at'],
            void_reason=row['void_reason']
        )
    
    def _row_to_sale_item(self, row) -> SaleItem:
        """Convert database row to SaleItem object"""
        return SaleItem(
            id=row['id'],
            sale_id=row['sale_id'],
            product_id=row['product_id'],
            product_name=row['product_name'],
            quantity=row['quantity'],
            unit_price=row['unit_price'],
            subtotal=row['subtotal'],
            batch_number=row['batch_number']
        )


# Global repository instance
sales_repo = SalesRepository()
