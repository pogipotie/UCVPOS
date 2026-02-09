"""
MySQL Database Schema
Creates all required tables with proper indexing and MySQL-specific data types
"""
from database.connection import db

SCHEMA_SQL = """
-- Products table with pharmacy-specific fields
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    barcode VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    stock_quantity INT DEFAULT 0,
    min_stock_level INT DEFAULT 10,
    batch_number VARCHAR(100),
    expiry_date DATE,
    prescription_required TINYINT(1) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Sales header table
CREATE TABLE IF NOT EXISTS sales (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) DEFAULT 'completed',
    cashier_name VARCHAR(255),
    voided_at TIMESTAMP NULL,
    void_reason TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Sale line items
CREATE TABLE IF NOT EXISTS sale_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sale_id INT NOT NULL,
    product_id INT NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    subtotal DECIMAL(10, 2) NOT NULL,
    batch_number VARCHAR(100),
    FOREIGN KEY (sale_id) REFERENCES sales(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Payment records
CREATE TABLE IF NOT EXISTS payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sale_id INT NOT NULL,
    amount_tendered DECIMAL(10, 2) NOT NULL,
    change_given DECIMAL(10, 2) NOT NULL,
    payment_method VARCHAR(50) DEFAULT 'cash',
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sale_id) REFERENCES sales(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Audit trail for all actions
CREATE TABLE IF NOT EXISTS audit_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100) NOT NULL,
    entity_id INT,
    details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Void-specific logs (non-editable)
CREATE TABLE IF NOT EXISTS void_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sale_id INT NOT NULL,
    reason TEXT NOT NULL,
    voided_by VARCHAR(255),
    voided_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    original_total DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (sale_id) REFERENCES sales(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Users table for authentication
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'cashier',
    full_name VARCHAR(255),
    is_active TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Settings table for application configuration
CREATE TABLE IF NOT EXISTS settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

INDEX_SQL = """
-- Performance indexes
-- Note: MySQL creates indexes for foreign keys automatically, but we add others manually
CREATE INDEX idx_products_barcode ON products(barcode);
CREATE INDEX idx_products_expiry ON products(expiry_date);
CREATE INDEX idx_products_stock ON products(stock_quantity);
CREATE INDEX idx_sales_date ON sales(sale_date);
CREATE INDEX idx_sales_status ON sales(status);
CREATE INDEX idx_audit_timestamp ON audit_logs(timestamp);
"""

def initialize_mysql_database():
    """Create all tables and indexes if they don't exist"""
    # Create tables
    # Split by semicolon but ignore semicolons inside statements if any (simple split works here for DDL)
    statements = [s.strip() for s in SCHEMA_SQL.split(';') if s.strip()]
    for statement in statements:
        db.execute(statement)
    
    # Create indexes
    statements = [s.strip() for s in INDEX_SQL.split(';') if s.strip()]
    for statement in statements:
        try:
            db.execute(statement)
        except Exception as e:
            # Check for error code 1061: Duplicate key name
            error_code = None
            if hasattr(e, 'args') and len(e.args) > 0:
                if isinstance(e.args[0], int):
                    error_code = e.args[0]
                elif hasattr(e.args[0], 'errno'):
                    error_code = e.args[0].errno
            
            if error_code != 1061:
                print(f"Index creation warning: {e}")
    
    # ---------------------------------------------------------
    # MIGRATIONS (Auto-add new columns if missing)
    # ---------------------------------------------------------
    # Try to add cost_price to products (ignore if exists - error 1060)
    try:
        db.execute("ALTER TABLE products ADD COLUMN cost_price DECIMAL(10, 2) DEFAULT 0.00 AFTER price")
        print("Migrating: Added 'cost_price' to products table.")
    except Exception as e:
        if '1060' in str(e):  # Duplicate column name
            pass
        else:
            print(f"Migration note (cost_price): {e}")
    
    # Try to add original_cost to sale_items (ignore if exists - error 1060)
    try:
        db.execute("ALTER TABLE sale_items ADD COLUMN original_cost DECIMAL(10, 2) DEFAULT 0.00 AFTER unit_price")
        print("Migrating: Added 'original_cost' to sale_items table.")
    except Exception as e:
        if '1060' in str(e):  # Duplicate column name
            pass
        else:
            print(f"Migration note (original_cost): {e}")
    
    db.commit()
    print("MySQL Database initialized successfully")
