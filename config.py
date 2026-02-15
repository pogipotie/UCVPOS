"""
Pharmacy POS Configuration Constants
"""
import os
import sys

# Application Info
APP_NAME = "DoubleA POS"
APP_VERSION = "1.0.0"

# Database Configuration
if getattr(sys, 'frozen', False):
    # If compiled, use %LOCALAPPDATA% to hide it from user
    # e.g. C:\Users\Name\AppData\Local\DoubleA_POS\
    local_app_data = os.getenv('LOCALAPPDATA', os.path.expanduser('~\\AppData\\Local'))
    BASE_DIR = os.path.join(local_app_data, APP_NAME.replace(" ", "_"))
    # Ensure directory exists
    os.makedirs(BASE_DIR, exist_ok=True)
else:
    # If running from source, use the directory of this file
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

# Database Type: 'sqlite' or 'mysql'
DB_TYPE = 'mysql'

# MySQL Configuration
DB_CONFIG_FILE = os.path.join(BASE_DIR, "db_config.json")

# Default Config
MYSQL_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '',
    'database': 'ucvpos_db',
    'raise_on_warnings': True
}

# Try to load from file
# Config Encryption Helpers
import base64
import json

CONFIG_KEY = "UCVPOS_SECURE_KEY"  # Simple key for obfuscation

def _xor_cipher(text: str, key: str) -> str:
    return "".join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(text))

def save_config(config_data: dict, filepath: str = DB_CONFIG_FILE):
    """Save config with encryption"""
    try:
        json_str = json.dumps(config_data)
        # 1. XOR
        encrypted = _xor_cipher(json_str, CONFIG_KEY)
        # 2. Base64
        b64_encoded = base64.b64encode(encrypted.encode()).decode()
        
        with open(filepath, 'w') as f:
            f.write(b64_encoded)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False

def load_config(filepath: str = DB_CONFIG_FILE) -> dict:
    """Load encrypted config"""
    if not os.path.exists(filepath):
        return {}
        
    try:
        with open(filepath, 'r') as f:
            content = f.read().strip()
            
        # Try loading as plain JSON first (migration / backward compatibility)
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Not JSON, try decrypting
            pass
            
        # Decrypt
        encrypted = base64.b64decode(content).decode()
        json_str = _xor_cipher(encrypted, CONFIG_KEY)
        return json.loads(json_str)
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}

# Try to load from file
saved_config = load_config()
if saved_config:
    MYSQL_CONFIG.update(saved_config)

import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
