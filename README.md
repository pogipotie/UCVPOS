# Pharmacy POS - Offline Desktop Application

A production-ready, offline-first Point of Sale system for small-to-medium pharmacies.

## Quick Start

### Development Mode
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### Build Standalone .exe
```bash
# Install PyInstaller
pip install pyinstaller

# Build using spec file
pyinstaller pharmacy_pos.spec

# OR build with simple command
pyinstaller --onefile --windowed --name PharmacyPOS main.py
```

The executable will be in the `dist/` folder.

## Deployment

Copy these files to any Windows PC:
- `PharmacyPOS.exe` (from dist folder)
- `pos.db` (will be created automatically on first run)

No installation required!

## Features

- **Fast Checkout**: USB barcode scanner support (<50ms lookup)
- **Inventory Management**: Full CRUD with expiry tracking
- **Compliance**: Expired product blocking, prescription flags
- **Reports**: Daily/monthly sales, low stock alerts, exports
- **Backup**: One-click database backup

## Keyboard Shortcuts (Cashier Screen)

| Key | Action |
|-----|--------|
| F1 | New Sale |
| F12 | Checkout |
| Delete | Remove Selected Item |
| Escape | Clear Status Message |

## Technology Stack

- Python 3.10+
- PyQt6 (Desktop UI)
- SQLite (Local Database)
- PyInstaller (Packaging)

## Project Structure

```
UCVPOS/
├── main.py              # Entry point
├── config.py            # Configuration
├── database/            # Database layer
├── repositories/        # Data access
├── services/            # Business logic
└── ui/                  # User interface
```

## License

Proprietary - All rights reserved.
