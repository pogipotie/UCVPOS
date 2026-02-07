# UCVPOS - Modern Pharmacy Point of Sale System

A robust, offline-first Point of Sale (POS) system designed for pharmacies, built with Python (PyQt6) and powered by MySQL.

## 🚀 Key Features

### 🛒 Point of Sale (Cashier)
- **Fast Checkout**: Ultra-low latency barcode scanning support.
- **Cart Management**: Add, remove, update quantities, and clear cart with ease.
- **Smart Hardware Integration**: Supports USB barcode scanners and receipt printers.
- **Compliance Ready**: Built-in support for **Senior Citizen (SC) / PWD Discounts** (20% + VAT Exemption) as per RA 9994/10754.
- **Modern UI**: Dark-themed, touch-friendly interface with custom modal dialogs.

### 📦 Inventory Management
- **Detailed Product Tracking**: Track stock levels, expiry dates, and batch numbers.
- **Reorder Alerts**: Visual indicators for low-stock items.
- **Expiry Management**: Dedicated tracking for perishable goods.
- **Search & Filter**: Rapidly find products by name, barcode, or category.

### 📊 Dashboard & Analytics
- **Live Sales Tracking**: Real-time sales charts and daily totals.
- **Top Performers**: Identify best-selling products instantly.
- **Audit Trails**: Complete log of all sensitive actions (voids, returns, logins).

### ⚙️ Administration
- **User Roles**: Secure access with Admin and Cashier roles.
- **Configurable Settings**: Customize VAT rates, printer headers, and store details.
- **Database Backup**: Integrated backup scheduling.

---

## 🛠️ Technology Stack

- **Frontend**: Python 3.10+ with PyQt6 (Desert/Dark Theme)
- **Backend Database**: MySQL 8.0+ (via XAMPP or dedicated server)
- **Reporting**: Matplotlib for charts, ReportLab for PDF generation
- **ORM**: Custom repository pattern with MySQL Connector

---

## 📥 Installation Guide

### Prerequisites
1.  **Python 3.10 or higher** installed.
2.  **MySQL Server** (we recommend [XAMPP](https://www.apachefriends.org/) for local deployments).

### Step 1: Database Setup
1.  Start MySQL (via XAMPP Control Panel).
2.  Create a new empty database named `pharmacy_pos` (or your preferred name).
    ```sql
    CREATE DATABASE pharmacy_pos;
    ```
3.  The application will automatically create all tables and indexes on first run.

### Step 2: Application Setup
1.  Clone the repository:
    ```bash
    git clone https://github.com/your-repo/UCVPOS.git
    cd UCVPOS
    ```
2.  Create a virtual environment (recommended):
    ```bash
    python -m venv .venv
    # Windows:
    .venv\Scripts\activate
    # Mac/Linux:
    source .venv/bin/activate
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Step 3: Configuration
1.  Open `config.py`.
2.  Update the `MYSQL_CONFIG` dictionary with your database credentials:
    ```python
    MYSQL_CONFIG = {
        'host': 'localhost',
        'user': 'root',      # Default XAMPP user
        'password': '',      # Default XAMPP password is empty
        'database': 'pharmacy_pos',
        'port': 3306
    }
    ```

### Step 4: Run the App
```bash
python main.py
```
*Login with default credentials:*
- **Username**: `admin`
- **Password**: `admin123`

---

## ⌨️ Keyboard Shortcuts

| Key | Context | Action |
| :--- | :--- | :--- |
| **F1** | Cashier | Start New Sale |
| **F12** | Cashier | Process Payment / Checkout |
| **Del** | Cashier | Remove Selected Item |
| **Esc** | Global | Cancel / Close Dialog |
| **Ctrl+S** | Forms | Save |
| **F2** | Global | Go to Inventory |
| **F3** | Global | Go to Sales History |
| **F4** | Global | Go to Reports |

---

## 📂 Project Structure

```
UCVPOS/
├── main.py              # Application Entry Point
├── config.py            # Database & App Configuration
├── database/            # Database Layer
│   ├── connection.py    # MySQL Connection Handler
│   ├── schema_mysql.py  # DDL Scripts (Tables/Indexes)
│   └── models.py        # Data Classes (ORM)
├── repositories/        # Data Access Object (DAO) Layer
│   ├── product_repo.py
│   ├── sales_repo.py
│   └── ...
├── services/            # Business Logic Layer
│   ├── sales_service.py # Complex Sales Logic
│   └── auth_service.py  # Authentication
├── ui/                  # User Interface (PyQt6)
│   ├── main_window.py   # Main Application Container
│   ├── cashier_screen.py# POS Interface
│   └── components/      # Reusable Widgets (Dialogs, Cards)
└── assets/              # Icons and Images
```

## ⚠️ Troubleshooting

**"Duplicate key name" warnings on startup?**
- These are harmless. The app checks if indexes exist to ensure optimal performance. You can ignore them.

**"MySQL Connection Error"?**
- Ensure XAMPP (MySQL) is running.
- Verify credentials in `config.py`.

**"Printer Not Found"?**
- Check USB connection.
- Verify the printer name in Settings matches your Windows printer name exactly.

---

## 📜 License

Private proprietary software. All rights reserved.
