"""
Database Schema and Migrations
Creates all required tables with proper indexing
"""
from database.connection import db


SCHEMA_SQL = """
-- Products table with pharmacy-specific fields
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    barcode TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    stock_quantity INTEGER DEFAULT 0,
    min_stock_level INTEGER DEFAULT 10,
    batch_number TEXT,
    expiry_date DATE,
    prescription_required INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sales header table
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount REAL NOT NULL,
    status TEXT DEFAULT 'completed',
    cashier_name TEXT,
    voided_at TIMESTAMP,
    void_reason TEXT
);

-- Sale line items
CREATE TABLE IF NOT EXISTS sale_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sale_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    product_name TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    subtotal REAL NOT NULL,
    batch_number TEXT,
    FOREIGN KEY (sale_id) REFERENCES sales(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Payment records
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sale_id INTEGER NOT NULL,
    amount_tendered REAL NOT NULL,
    change_given REAL NOT NULL,
    payment_method TEXT DEFAULT 'cash',
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sale_id) REFERENCES sales(id)
);

-- Audit trail for all actions
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id INTEGER,
    details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Void-specific logs (non-editable)
CREATE TABLE IF NOT EXISTS void_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sale_id INTEGER NOT NULL,
    reason TEXT NOT NULL,
    voided_by TEXT,
    voided_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    original_total REAL NOT NULL,
    FOREIGN KEY (sale_id) REFERENCES sales(id)
);

-- Users table for authentication
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'cashier',
    full_name TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);
"""

INDEX_SQL = """
-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_products_barcode ON products(barcode);
CREATE INDEX IF NOT EXISTS idx_products_expiry ON products(expiry_date);
CREATE INDEX IF NOT EXISTS idx_products_stock ON products(stock_quantity);
CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(sale_date);
CREATE INDEX IF NOT EXISTS idx_sales_status ON sales(status);
CREATE INDEX IF NOT EXISTS idx_sale_items_sale ON sale_items(sale_id);
CREATE INDEX IF NOT EXISTS idx_payments_sale ON payments(sale_id);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs(timestamp);
"""


def initialize_database():
    """Create all tables and indexes if they don't exist"""
    # Create tables
    for statement in SCHEMA_SQL.split(';'):
        statement = statement.strip()
        if statement:
            db.execute(statement)
    
    # Create indexes
    for statement in INDEX_SQL.split(';'):
        statement = statement.strip()
        if statement:
            db.execute(statement)
    
    db.commit()
    print("Database initialized successfully")


def reset_database():
    """Drop all tables and recreate (for development only)"""
    tables = ['void_logs', 'audit_logs', 'payments', 'sale_items', 'sales', 'products']
    for table in tables:
        db.execute(f"DROP TABLE IF EXISTS {table}")
    db.commit()
    initialize_database()
