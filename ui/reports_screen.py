"""
Reports Screen - Sales reports and data exports
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QTableWidget, QTableWidgetItem, QFrame,
    QDateEdit, QTabWidget, QMessageBox, QFileDialog,
    QHeaderView, QAbstractItemView, QGroupBox, QStyle
)
from PyQt6.QtCore import Qt, QDate, QSize
from datetime import date, datetime, timedelta

from services.report_service import report_service
from services.backup_service import backup_service
from services.auth_service import auth_service
from repositories.sales_repo import sales_repo
from ui.components.custom_calendar import YearDropdownCalendarWidget


class ReportsScreen(QWidget):
    """Reports and export screen"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cashier_filter = None
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("Reports & Backup")
        title.setObjectName("titleLabel")
        header_layout.addWidget(title)
        
        layout.addLayout(header_layout)
        
        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.setIconSize(QSize(24, 24))
        
        # Daily Sales Tab
        daily_tab = self._create_daily_tab()
        self.tabs.addTab(daily_tab, self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView), "Daily Sales")
        
        # Monthly Summary Tab
        monthly_tab = self._create_monthly_tab()
        self.tabs.addTab(monthly_tab, self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogInfoView), "Monthly Summary")
        
        # Transaction History Tab
        history_tab = self._create_history_tab()
        self.tabs.addTab(history_tab, self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogListView), "Transaction History")
        
        # Low Stock Tab
        stock_tab = self._create_stock_tab()
        self.tabs.addTab(stock_tab, self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxWarning), "Low Stock Alert")
        
        # Expiry Tab
        expiry_tab = self._create_expiry_tab()
        self.tabs.addTab(expiry_tab, self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxCritical), "Expiry Report")
        
        # Data Management (Backup) Tab
        backup_tab = self._create_backup_tab()
        self.tabs.addTab(backup_tab, self.style().standardIcon(QStyle.StandardPixmap.SP_DriveHDIcon), "Data Management")
        
        layout.addWidget(self.tabs, 1)
        
        self.apply_permissions()

    def apply_permissions(self):
        """Apply role-based tab visibility and filtering"""
        user = auth_service.get_current_user()
        if user and user.role == 'cashier':
            self.cashier_filter = user.username
            
            # Hide Monthly Summary (index 1)
            self.tabs.setTabVisible(1, False)
            
            # Hide Data Management (index 5)
            self.tabs.setTabVisible(5, False)
        else:
            self.cashier_filter = None
            self.tabs.setTabVisible(1, True)
            self.tabs.setTabVisible(5, True)

    def _create_backup_tab(self) -> QWidget:
        """Create data management tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Backup Section
        backup_group = QGroupBox("Database Backup")
        group_layout = QVBoxLayout(backup_group)
        group_layout.setSpacing(15)
        
        info_label = QLabel(
            "Create a full backup of your pharmacy database. "
            "Regular backups are recommended to prevent data loss."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #B0B0B0; font-style: italic;")
        group_layout.addWidget(info_label)
        
        btn_layout = QHBoxLayout()
        backup_btn = QPushButton("🔒 Create New Backup")
        backup_btn.setObjectName("primaryButton")
        backup_btn.setMinimumHeight(50)
        backup_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        backup_btn.clicked.connect(self.create_backup)
        btn_layout.addWidget(backup_btn)
        btn_layout.addStretch()
        
        group_layout.addLayout(btn_layout)
        
        layout.addWidget(backup_group)
        layout.addStretch()
        
        return widget

    def _create_summary_card(self, title: str, value: str) -> QFrame:
        """Create a summary card widget"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #1E1E1E;
                border: 1px solid #333333;
                border-radius: 0px;
                border-left: 4px solid #03DAC6;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout(frame)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #B3B3B3; font-size: 13px; font-weight: 500; background: transparent;")
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setObjectName(f"card_{title.replace(' ', '_').lower()}")
        value_label.setStyleSheet("color: #FFFFFF; font-size: 24px; font-weight: bold; background: transparent;")
        layout.addWidget(value_label)
        
        return frame
    
    def _create_daily_tab(self) -> QWidget:
        """Create daily sales report tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Date selector
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Select Date:"))
        
        self.daily_date = QDateEdit()
        self.daily_date.setCalendarPopup(True)
        self.daily_date.setCalendarWidget(YearDropdownCalendarWidget())
        self.daily_date.setDate(QDate.currentDate())
        date_layout.addWidget(self.daily_date)
        
        load_btn = QPushButton("Load Report")
        load_btn.clicked.connect(self.load_daily_report)
        date_layout.addWidget(load_btn)
        
        date_layout.addStretch()
        
        export_btn = QPushButton("Export to CSV")
        export_btn.clicked.connect(self.export_daily_csv)
        date_layout.addWidget(export_btn)
        
        layout.addLayout(date_layout)
        
        # Summary cards
        summary_layout = QHBoxLayout()
        
        self.daily_transactions = self._create_summary_card("Transactions", "0")
        summary_layout.addWidget(self.daily_transactions)
        
        self.daily_sales = self._create_summary_card("Total Sales", "₱0.00")
        summary_layout.addWidget(self.daily_sales)
        
        self.daily_voided = self._create_summary_card("Voided", "0")
        summary_layout.addWidget(self.daily_voided)
        
        layout.addLayout(summary_layout)
        
        # Sales table
        self.daily_table = QTableWidget()
        self.daily_table.setColumnCount(6)
        self.daily_table.setHorizontalHeaderLabels(["ID", "Time", "Products", "Total", "Status", "Cashier"])
        self.daily_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.daily_table.setAlternatingRowColors(True)
        self.daily_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.daily_table, 1)
        
        # Load today's report
        self.load_daily_report()
        
        return widget
    
    def _create_monthly_tab(self) -> QWidget:
        """Create monthly summary tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Month selector
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Month:"))
        
        self.monthly_date = QDateEdit()
        self.monthly_date.setCalendarPopup(True)
        self.monthly_date.setCalendarWidget(YearDropdownCalendarWidget())
        self.monthly_date.setDisplayFormat("MMMM yyyy")
        self.monthly_date.setMinimumWidth(200)
        self.monthly_date.setDate(QDate.currentDate())
        date_layout.addWidget(self.monthly_date)
        
        load_btn = QPushButton("Load Report")
        load_btn.clicked.connect(self.load_monthly_report)
        date_layout.addWidget(load_btn)
        
        date_layout.addStretch()
        
        layout.addLayout(date_layout)
        
        # Summary
        summary_layout = QHBoxLayout()
        
        self.monthly_transactions = self._create_summary_card("Total Transactions", "0")
        summary_layout.addWidget(self.monthly_transactions)
        
        self.monthly_sales_total = self._create_summary_card("Total Sales", "₱0.00")
        summary_layout.addWidget(self.monthly_sales_total)
        
        self.monthly_voided = self._create_summary_card("Voided Sales", "0")
        summary_layout.addWidget(self.monthly_voided)
        
        layout.addLayout(summary_layout)
        
        # Daily breakdown
        self.monthly_table = QTableWidget()
        self.monthly_table.setColumnCount(4)
        self.monthly_table.setHorizontalHeaderLabels(["Date", "Transactions", "Sales", "Voided"])
        self.monthly_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.monthly_table.setAlternatingRowColors(True)
        self.monthly_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.monthly_table, 1)
        
        return widget
    
    def _create_history_tab(self) -> QWidget:
        """Create transaction history tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Controls
        controls = QHBoxLayout()
        
        controls.addWidget(QLabel("From:"))
        self.history_start = QDateEdit()
        self.history_start.setCalendarPopup(True)
        self.history_start.setCalendarWidget(YearDropdownCalendarWidget())
        self.history_start.setDate(QDate.currentDate().addDays(-7))
        controls.addWidget(self.history_start)
        
        controls.addWidget(QLabel("To:"))
        self.history_end = QDateEdit()
        self.history_end.setCalendarPopup(True)
        self.history_end.setCalendarWidget(YearDropdownCalendarWidget())
        self.history_end.setDate(QDate.currentDate())
        controls.addWidget(self.history_end)
        
        load_btn = QPushButton("Load")
        load_btn.clicked.connect(self.load_transaction_history)
        controls.addWidget(load_btn)
        
        controls.addStretch()
        
        export_btn = QPushButton("Export to Excel")
        export_btn.clicked.connect(self.export_history_excel)
        controls.addWidget(export_btn)
        
        layout.addLayout(controls)
        
        # Table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels([
            "ID", "Date/Time", "Items", "Total", "Status", "Cashier"
        ])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.history_table.setAlternatingRowColors(True)
        self.history_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.history_table, 1)
        
        return widget
    
    def _create_stock_tab(self) -> QWidget:
        """Create low stock alert tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Controls
        controls = QHBoxLayout()
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_low_stock)
        controls.addWidget(refresh_btn)
        
        controls.addStretch()
        
        export_btn = QPushButton("Export to CSV")
        export_btn.clicked.connect(self.export_low_stock)
        controls.addWidget(export_btn)
        
        layout.addLayout(controls)
        
        # Table
        self.stock_table = QTableWidget()
        self.stock_table.setColumnCount(5)
        self.stock_table.setHorizontalHeaderLabels([
            "Barcode", "Product Name", "Current Stock", "Min Level", "Reorder Qty"
        ])
        self.stock_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.stock_table.setAlternatingRowColors(True)
        self.stock_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.stock_table, 1)
        
        # Load data
        self.load_low_stock()
        
        return widget
    
    def _create_expiry_tab(self) -> QWidget:
        """Create expiry report tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Controls
        controls = QHBoxLayout()
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_expiry_report)
        controls.addWidget(refresh_btn)
        
        controls.addStretch()
        
        layout.addLayout(controls)
        
        # Expired products
        expired_group = QGroupBox("Expired Products")
        expired_layout = QVBoxLayout(expired_group)
        
        self.expired_table = QTableWidget()
        self.expired_table.setColumnCount(4)
        self.expired_table.setHorizontalHeaderLabels(["Barcode", "Product", "Expiry Date", "Stock"])
        self.expired_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.expired_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        expired_layout.addWidget(self.expired_table)
        
        layout.addWidget(expired_group)
        
        # Expiring soon
        expiring_group = QGroupBox("Expiring Within 30 Days")
        expiring_layout = QVBoxLayout(expiring_group)
        
        self.expiring_table = QTableWidget()
        self.expiring_table.setColumnCount(5)
        self.expiring_table.setHorizontalHeaderLabels([
            "Barcode", "Product", "Expiry Date", "Days Left", "Stock"
        ])
        self.expiring_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.expiring_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        expiring_layout.addWidget(self.expiring_table)
        
        layout.addWidget(expiring_group)
        
        # Load data
        self.load_expiry_report()
        
        return widget
    

    
    def load_daily_report(self):
        """Load daily sales report"""
        qdate = self.daily_date.date()
        report_date = date(qdate.year(), qdate.month(), qdate.day())
        
        report = report_service.get_daily_report(report_date, self.cashier_filter)
        
        # Update summary
        summary = report['summary']
        self.daily_transactions.findChild(QLabel, "card_transactions").setText(
            str(summary['total_transactions'])
        )
        self.daily_sales.findChild(QLabel, "card_total_sales").setText(
            f"₱{summary['total_sales']:.2f}"
        )
        self.daily_voided.findChild(QLabel, "card_voided").setText(
            str(summary['voided_count'])
        )
        
        # Populate table
        sales = report['sales']
        self.daily_table.setRowCount(len(sales))
        
        for row, sale in enumerate(sales):
            self.daily_table.setItem(row, 0, QTableWidgetItem(str(sale.id)))
            self.daily_table.setItem(row, 1, QTableWidgetItem(str(sale.sale_date)))
            
            # Products
            items_str = ""
            if hasattr(sale, 'items') and sale.items:
                items_str = ", ".join([f"{i.product_name} ({i.quantity})" for i in sale.items])
            self.daily_table.setItem(row, 2, QTableWidgetItem(items_str))
            
            self.daily_table.setItem(row, 3, QTableWidgetItem(f"₱{sale.total_amount:.2f}"))
            
            status_item = QTableWidgetItem(sale.status.upper())
            if sale.status == 'voided':
                status_item.setForeground(Qt.GlobalColor.red)
            self.daily_table.setItem(row, 4, status_item)
            
            self.daily_table.setItem(row, 5, QTableWidgetItem(sale.cashier_name or "N/A"))
    
    def load_monthly_report(self):
        """Load monthly summary"""
        qdate = self.monthly_date.date()
        report = report_service.get_monthly_report(qdate.year(), qdate.month())
        
        # Update summary
        summary = report['summary']
        self.monthly_transactions.findChild(QLabel, "card_total_transactions").setText(
            str(summary['total_transactions'])
        )
        self.monthly_sales_total.findChild(QLabel, "card_total_sales").setText(
            f"₱{summary['total_sales']:.2f}"
        )
        self.monthly_voided.findChild(QLabel, "card_voided_sales").setText(
            str(summary['voided_count'])
        )
        
        # Populate table
        daily = report['daily_breakdown']
        self.monthly_table.setRowCount(len(daily))
        
        for row, day in enumerate(daily):
            self.monthly_table.setItem(row, 0, QTableWidgetItem(str(day['date'])))
            self.monthly_table.setItem(row, 1, QTableWidgetItem(str(day['total_transactions'])))
            self.monthly_table.setItem(row, 2, QTableWidgetItem(f"₱{day['total_sales']:.2f}"))
            self.monthly_table.setItem(row, 3, QTableWidgetItem(str(day['voided_count'])))
    
    def load_transaction_history(self):
        """Load transaction history"""
        start_qdate = self.history_start.date()
        end_qdate = self.history_end.date()
        
        start_date = date(start_qdate.year(), start_qdate.month(), start_qdate.day())
        end_date = date(end_qdate.year(), end_qdate.month(), end_qdate.day())
        
        sales = sales_repo.get_sales_by_date_range(start_date, end_date, self.cashier_filter)
        
        self.history_table.setRowCount(len(sales))
        
        for row, sale in enumerate(sales):
            items = sales_repo.get_sale_items(sale.id)
            
            self.history_table.setItem(row, 0, QTableWidgetItem(str(sale.id)))
            self.history_table.setItem(row, 1, QTableWidgetItem(str(sale.sale_date)))
            self.history_table.setItem(row, 2, QTableWidgetItem(str(len(items))))
            self.history_table.setItem(row, 3, QTableWidgetItem(f"₱{sale.total_amount:.2f}"))
            self.history_table.setItem(row, 4, QTableWidgetItem(sale.status.upper()))
            self.history_table.setItem(row, 5, QTableWidgetItem(sale.cashier_name or "N/A"))
    
    def load_low_stock(self):
        """Load low stock products"""
        report = report_service.get_low_stock_report()
        products = report['products']
        
        self.stock_table.setRowCount(len(products))
        
        for row, p in enumerate(products):
            self.stock_table.setItem(row, 0, QTableWidgetItem(p.barcode))
            self.stock_table.setItem(row, 1, QTableWidgetItem(p.name))
            self.stock_table.setItem(row, 2, QTableWidgetItem(str(p.stock_quantity)))
            self.stock_table.setItem(row, 3, QTableWidgetItem(str(p.min_stock_level)))
            reorder = max(0, p.min_stock_level * 2 - p.stock_quantity)
            self.stock_table.setItem(row, 4, QTableWidgetItem(str(reorder)))
    
    def load_expiry_report(self):
        """Load expiry report"""
        report = report_service.get_expiry_report()
        
        # Expired
        expired = report['expired_products']
        self.expired_table.setRowCount(len(expired))
        
        for row, p in enumerate(expired):
            self.expired_table.setItem(row, 0, QTableWidgetItem(p.barcode))
            self.expired_table.setItem(row, 1, QTableWidgetItem(p.name))
            self.expired_table.setItem(row, 2, QTableWidgetItem(str(p.expiry_date)))
            self.expired_table.setItem(row, 3, QTableWidgetItem(str(p.stock_quantity)))
        
        # Expiring soon
        expiring = report['expiring_soon']
        self.expiring_table.setRowCount(len(expiring))
        
        for row, p in enumerate(expiring):
            days_left = (p.expiry_date - date.today()).days
            self.expiring_table.setItem(row, 0, QTableWidgetItem(p.barcode))
            self.expiring_table.setItem(row, 1, QTableWidgetItem(p.name))
            self.expiring_table.setItem(row, 2, QTableWidgetItem(str(p.expiry_date)))
            self.expiring_table.setItem(row, 3, QTableWidgetItem(str(days_left)))
            self.expiring_table.setItem(row, 4, QTableWidgetItem(str(p.stock_quantity)))
    
    def export_daily_csv(self):
        """Export daily report to CSV"""
        qdate = self.daily_date.date()
        report_date = date(qdate.year(), qdate.month(), qdate.day())
        
        filepath = report_service.export_sales_to_csv(report_date, report_date, self.cashier_filter)
        QMessageBox.information(self, "Export Complete", f"Report saved to:\n{filepath}")
    
    def export_history_excel(self):
        """Export history to Excel"""
        start_qdate = self.history_start.date()
        end_qdate = self.history_end.date()
        
        start_date = date(start_qdate.year(), start_qdate.month(), start_qdate.day())
        end_date = date(end_qdate.year(), end_qdate.month(), end_qdate.day())
        
        filepath = report_service.export_sales_to_csv(start_date, end_date, self.cashier_filter)
        QMessageBox.information(self, "Export Complete", f"Report saved to:\n{filepath}")
    
    def export_low_stock(self):
        """Export low stock to CSV"""
        filepath = report_service.export_inventory_to_csv()
        QMessageBox.information(self, "Export Complete", f"Report saved to:\n{filepath}")
    
    def create_backup(self):
        """Create database backup"""
        success, message, path = backup_service.create_backup()
        
        if success:
            QMessageBox.information(
                self, "Backup Complete",
                f"Database backup created successfully!\n\nSaved to:\n{path}"
            )
        else:
            QMessageBox.warning(self, "Backup Failed", message)
