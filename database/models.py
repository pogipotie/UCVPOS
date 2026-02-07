"""
Data Models - Dataclasses for all database entities
"""
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, List


@dataclass
class Product:
    """Product/Medicine model"""
    id: Optional[int] = None
    barcode: str = ""
    name: str = ""
    price: float = 0.0
    cost_price: float = 0.0
    stock_quantity: int = 0
    min_stock_level: int = 10
    batch_number: Optional[str] = None
    expiry_date: Optional[date] = None
    prescription_required: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @property
    def is_expired(self) -> bool:
        """Check if product is expired"""
        if self.expiry_date is None:
            return False
        return self.expiry_date < date.today()
    
    @property
    def is_low_stock(self) -> bool:
        """Check if stock is below minimum level"""
        return self.stock_quantity <= self.min_stock_level
    
    @property
    def is_out_of_stock(self) -> bool:
        """Check if product is out of stock"""
        return self.stock_quantity <= 0


@dataclass
class CartItem:
    """Item in the shopping cart"""
    product: Product
    quantity: int = 1
    
    @property
    def subtotal(self) -> float:
        """Calculate line item subtotal"""
        return self.product.price * self.quantity


@dataclass
class Sale:
    """Sale transaction model"""
    id: Optional[int] = None
    sale_date: Optional[datetime] = None
    total_amount: float = 0.0
    status: str = "completed"
    cashier_name: Optional[str] = None
    voided_at: Optional[datetime] = None
    void_reason: Optional[str] = None
    items: List['SaleItem'] = field(default_factory=list)
    
    @property
    def is_voided(self) -> bool:
        return self.status == "voided"


@dataclass
class SaleItem:
    """Line item in a sale"""
    id: Optional[int] = None
    sale_id: Optional[int] = None
    product_id: int = 0
    product_name: str = ""
    quantity: int = 1
    unit_price: float = 0.0
    original_cost: float = 0.0
    subtotal: float = 0.0
    batch_number: Optional[str] = None


@dataclass
class Payment:
    """Payment record"""
    id: Optional[int] = None
    sale_id: int = 0
    amount_tendered: float = 0.0
    change_given: float = 0.0
    payment_method: str = "cash"
    payment_date: Optional[datetime] = None


@dataclass
class AuditLog:
    """Audit trail entry"""
    id: Optional[int] = None
    action: str = ""
    entity_type: str = ""
    entity_id: Optional[int] = None
    details: Optional[str] = None
    timestamp: Optional[datetime] = None


@dataclass
class VoidLog:
    """Void transaction log"""
    id: Optional[int] = None
    sale_id: int = 0
    reason: str = ""
    voided_by: Optional[str] = None
    voided_at: Optional[datetime] = None
    original_total: float = 0.0


@dataclass
class User:
    """User entity for authentication"""
    id: Optional[int] = None
    username: str = ""
    password_hash: str = ""
    role: str = "cashier"
    full_name: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    @property
    def is_admin(self) -> bool:
        return self.role == "admin"
