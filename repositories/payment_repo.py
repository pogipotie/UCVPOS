"""
Payment Repository - Payment records management
"""
from typing import Optional, List
from datetime import date
from database.connection import db
from database.models import Payment


class PaymentRepository:
    """Data access layer for payment records"""
    
    def create(self, payment: Payment) -> int:
        """Record a new payment"""
        cursor = db.execute(
            """INSERT INTO payments 
               (sale_id, amount_tendered, change_given, payment_method)
               VALUES (?, ?, ?, ?)""",
            (
                payment.sale_id,
                payment.amount_tendered,
                payment.change_given,
                payment.payment_method
            )
        )
        db.commit()
        return cursor.lastrowid
    
    def get_by_sale_id(self, sale_id: int) -> Optional[Payment]:
        """Get payment for a specific sale"""
        cursor = db.execute(
            "SELECT * FROM payments WHERE sale_id = ?",
            (sale_id,)
        )
        row = cursor.fetchone()
        return self._row_to_payment(row) if row else None
    
    def get_payments_by_date(self, date: date) -> List[Payment]:
        """Get all payments for a date"""
        start = f"{date.isoformat()} 00:00:00"
        end = f"{date.isoformat()} 23:59:59"
        cursor = db.execute(
            """SELECT * FROM payments 
               WHERE payment_date BETWEEN ? AND ?
               ORDER BY payment_date DESC""",
            (start, end)
        )
        return [self._row_to_payment(row) for row in cursor.fetchall()]
    
    def _row_to_payment(self, row) -> Payment:
        """Convert database row to Payment object"""
        return Payment(
            id=row['id'],
            sale_id=row['sale_id'],
            amount_tendered=row['amount_tendered'],
            change_given=row['change_given'],
            payment_method=row['payment_method'],
            payment_date=row['payment_date']
        )


# Global repository instance
payment_repo = PaymentRepository()
