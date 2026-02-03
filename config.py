"""
Pharmacy POS Configuration Constants
"""
import os

# Application Info
APP_NAME = "DoubleA POS"
APP_VERSION = "1.0.0"

# Database Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "pos.db")
BACKUP_DIR = os.path.join(BASE_DIR, "backups")

# Performance Settings
BARCODE_LOOKUP_TIMEOUT_MS = 50
DB_BUSY_TIMEOUT_MS = 5000

# UI Settings
CART_COLUMNS = ["Product", "Qty", "Unit Price", "Subtotal"]
DEFAULT_WINDOW_WIDTH = 1200
DEFAULT_WINDOW_HEIGHT = 800

# Business Rules
MIN_STOCK_WARNING_LEVEL = 10
ALLOW_NEGATIVE_STOCK = False
