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
from services.sales_service import sales_service
from services.settings_service import settings_service
from repositories.sales_repo import sales_repo
from repositories.audit_repo import audit_repo
from ui.components.custom_calendar import YearDropdownCalendarWidget
from PyQt6.QtGui import QColor, QIcon


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
        
        # Icon paths
        import os
        assets_path = os.path.join(os.path.dirname(__file__), "..", "assets", "Reports&Backup assets")
        
        # Daily Sales Tab
        daily_tab = self._create_daily_tab()
        self.tabs.addTab(daily_tab, QIcon(os.path.join(assets_path, "dailysales.png")), "Daily Sales")
        
        # Monthly Summary Tab
        monthly_tab = self._create_monthly_tab()
        self.tabs.addTab(monthly_tab, QIcon(os.path.join(assets_path, "monthlysale.png")), "Monthly Summary")
        
        # Transaction History Tab
        history_tab = self._create_history_tab()
        self.tabs.addTab(history_tab, QIcon(os.path.join(assets_path, "Transactionhistory.png")), "Transaction History")
        
        # Low Stock Tab
        stock_tab = self._create_stock_tab()
        self.tabs.addTab(stock_tab, QIcon(os.path.join(assets_path, "lowstock.png")), "Low Stock Alert")
        
        # Expiry Tab
        expiry_tab = self._create_expiry_tab()
        self.tabs.addTab(expiry_tab, QIcon(os.path.join(assets_path, "Expiryreport.png")), "Expiry Report")
        
        # Data Management (Backup) Tab
        backup_tab = self._create_backup_tab()
        self.tabs.addTab(backup_tab, QIcon(os.path.join(assets_path, "datamanagement.png")), "Data Management")
        
        # Audit Logs Tab (Admin only)
        audit_tab = self._create_audit_tab()
        self.tabs.addTab(audit_tab, QIcon(os.path.join(assets_path, "Auditlogs.png")), "Audit Logs")
        
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
            
            # Hide Audit Logs (index 6) - Admin only
            self.tabs.setTabVisible(6, False)
        else:
            self.cashier_filter = None
            self.tabs.setTabVisible(1, True)
            self.tabs.setTabVisible(5, True)
            self.tabs.setTabVisible(6, True)

    def _create_audit_tab(self) -> QWidget:
        """Create audit logs tab (admin only)"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Controls
        controls = QHBoxLayout()
        
        controls.addWidget(QLabel("From:"))
        self.audit_start = QDateEdit()
        self.audit_start.setCalendarPopup(True)
        self.audit_start.setCalendarWidget(YearDropdownCalendarWidget())
        self.audit_start.setDate(QDate.currentDate().addDays(-7))
        controls.addWidget(self.audit_start)
        
        controls.addWidget(QLabel("To:"))
        self.audit_end = QDateEdit()
        self.audit_end.setCalendarPopup(True)
        self.audit_end.setCalendarWidget(YearDropdownCalendarWidget())
        self.audit_end.setDate(QDate.currentDate())
        controls.addWidget(self.audit_end)
        
        load_btn = QPushButton("Load Logs")
        load_btn.clicked.connect(self.load_audit_logs)
        controls.addWidget(load_btn)
        
        controls.addStretch()
        
        layout.addLayout(controls)
        
        # Table
        self.audit_table = QTableWidget()
        self.audit_table.setColumnCount(5)
        self.audit_table.setHorizontalHeaderLabels([
            "Timestamp", "Action", "Entity", "Entity ID", "Details"
        ])
        header = self.audit_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.audit_table.setColumnWidth(0, 150)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.audit_table.setColumnWidth(3, 80)
        self.audit_table.verticalHeader().setDefaultSectionSize(35)
        self.audit_table.setAlternatingRowColors(True)
        self.audit_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.audit_table, 1)
        
        return widget
    
    def load_audit_logs(self):
        """Load audit logs for the selected date range"""
        start_qdate = self.audit_start.date()
        end_qdate = self.audit_end.date()
        
        start_date = date(start_qdate.year(), start_qdate.month(), start_qdate.day())
        end_date = date(end_qdate.year(), end_qdate.month(), end_qdate.day())
        
        logs = audit_repo.get_logs_by_date_range(start_date, end_date)
        
        self.audit_table.setRowCount(len(logs))
        
        for row, log in enumerate(logs):
            # Timestamp
            timestamp_item = QTableWidgetItem(str(log.timestamp))
            timestamp_item.setForeground(QColor("#888888"))
            self.audit_table.setItem(row, 0, timestamp_item)
            
            # Action with color coding
            action_item = QTableWidgetItem(log.action)
            if "VOID" in log.action:
                action_item.setForeground(QColor("#CF6679"))  # Red
            elif "CREATE" in log.action or "ADD" in log.action:
                action_item.setForeground(QColor("#03DAC6"))  # Teal
            elif "UPDATE" in log.action or "EDIT" in log.action:
                action_item.setForeground(QColor("#FFB800"))  # Yellow
            elif "DELETE" in log.action:
                action_item.setForeground(QColor("#FF4757"))  # Red
            else:
                action_item.setForeground(QColor("#FFFFFF"))
            self.audit_table.setItem(row, 1, action_item)
            
            # Entity type
            self.audit_table.setItem(row, 2, QTableWidgetItem(log.entity_type or "—"))
            
            # Entity ID
            entity_id = str(log.entity_id) if log.entity_id else "—"
            self.audit_table.setItem(row, 3, QTableWidgetItem(entity_id))
            
            # Details
            self.audit_table.setItem(row, 4, QTableWidgetItem(log.details or "—"))

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
        self.history_table.setColumnCount(7)
        self.history_table.setHorizontalHeaderLabels([
            "ID", "Date/Time", "Items", "Total", "Status", "Cashier", "Actions"
        ])
        header = self.history_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)  # Actions column
        self.history_table.setColumnWidth(6, 100)  # Button column
        self.history_table.verticalHeader().setDefaultSectionSize(35)  # Row height
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
        
        if not sales:
            self.history_table.setRowCount(0)
            from ui.components.custom_message_box import CustomErrorDialog
            dialog = CustomErrorDialog(self, "No Records Found", "No transactions found for the selected date range.")
            dialog.exec()
            return

        self.history_table.setRowCount(len(sales))
        
        for row, sale in enumerate(sales):
            items = sales_repo.get_sale_items(sale.id)
            
            self.history_table.setItem(row, 0, QTableWidgetItem(str(sale.id)))
            self.history_table.setItem(row, 1, QTableWidgetItem(str(sale.sale_date)))
            self.history_table.setItem(row, 2, QTableWidgetItem(str(len(items))))
            self.history_table.setItem(row, 3, QTableWidgetItem(f"₱{sale.total_amount:.2f}"))
            
            # Status with color and tooltip for voided sales
            status_item = QTableWidgetItem(sale.status.upper())
            if sale.status == 'voided':
                status_item.setForeground(QColor("#CF6679"))  # Red for voided
                # Show void reason as tooltip
                reason = getattr(sale, 'void_reason', None) or "No reason provided"
                status_item.setToolTip(f"Reason: {reason}")
            else:
                status_item.setForeground(QColor("#03DAC6"))  # Teal for completed
            self.history_table.setItem(row, 4, status_item)
            
            self.history_table.setItem(row, 5, QTableWidgetItem(sale.cashier_name or "N/A"))
            
            # Void button (only for completed sales)
            if sale.status == 'completed':
                void_btn = QPushButton("Void")
                void_btn.setFixedHeight(22)
                void_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #CF6679;
                        color: white;
                        border: none;
                        border-radius: 3px;
                        font-size: 10px;
                        font-weight: bold;
                        padding: 2px 10px;
                    }
                    QPushButton:hover {
                        background-color: #E57388;
                    }
                """)
                void_btn.clicked.connect(lambda checked, s=sale: self.void_sale(s))
                self.history_table.setCellWidget(row, 6, void_btn)
            else:
                # View button for voided sales - shows reason
                view_btn = QPushButton("View")
                view_btn.setFixedHeight(22)
                view_btn.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        color: #888888;
                        border: 1px solid #555555;
                        border-radius: 3px;
                        font-size: 10px;
                        padding: 2px 10px;
                    }
                    QPushButton:hover {
                        background-color: #333333;
                        color: white;
                    }
                """)
                view_btn.clicked.connect(lambda checked, s=sale: self.show_void_details(s))
                self.history_table.setCellWidget(row, 6, view_btn)
    
    def void_sale(self, sale):
        """Void a sale with custom styled dialog"""
        from ui.components.void_sale_dialog import VoidSaleDialog
        from ui.components.action_success_dialog import ActionSuccessDialog
        
        dialog = VoidSaleDialog(sale, self)
        
        if dialog.exec() == VoidSaleDialog.DialogCode.Accepted:
            # Get current user
            user = auth_service.get_current_user()
            voided_by = user.username if user else "Unknown"
            reason = dialog.get_reason()
            
            success, message = sales_service.void_sale(sale.id, reason, voided_by)
            
            if success:
                # Show success dialog
                success_dialog = ActionSuccessDialog(
                    title="Sale Voided",
                    message=f"Sale #{sale.id} has been voided.\nStock has been restored to inventory.",
                    parent=self
                )
                success_dialog.exec()
                self.load_transaction_history()  # Refresh table
            else:
                QMessageBox.warning(self, "Error", message)
    
    def show_void_details(self, sale):
        """Show void details for a voided sale"""
        from ui.components.void_details_dialog import VoidDetailsDialog
        
        dialog = VoidDetailsDialog(sale, self)
        dialog.exec()
    
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
        
        # Get default path
        default_dir = settings_service.get("system", "reports_path") or os.path.expanduser("~/Documents")
        default_filename = f"daily_sales_{report_date.isoformat()}.csv"
        
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Save Report", os.path.join(default_dir, default_filename), "CSV Files (*.csv)"
        )
        
        if filepath:
            saved_path = report_service.export_sales_to_csv(report_date, report_date, self.cashier_filter, output_path=filepath)
            QMessageBox.information(self, "Export Complete", f"Report saved to:\n{saved_path}")
    
    def export_history_excel(self):
        """Export history to Excel"""
        start_qdate = self.history_start.date()
        end_qdate = self.history_end.date()
        
        start_date = date(start_qdate.year(), start_qdate.month(), start_qdate.day())
        end_date = date(end_qdate.year(), end_qdate.month(), end_qdate.day())
        
        # Get default path
        default_dir = settings_service.get("system", "reports_path") or os.path.expanduser("~/Documents")
        default_filename = f"sales_history_{start_date.isoformat()}_to_{end_date.isoformat()}.xlsx"
        
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Save Report", os.path.join(default_dir, default_filename), "Excel Files (*.xlsx)"
        )
        
        if filepath:
            # Use new export_sales_to_excel method (need to add to service)
            # Or fallback to CSV if Excel not supported yet
            try:
                saved_path = report_service.export_sales_to_excel(start_date, end_date, self.cashier_filter, output_path=filepath)
                QMessageBox.information(self, "Export Complete", f"Report saved to:\n{saved_path}")
            except AttributeError:
                # Fallback implementation if method missing
                saved_path = report_service.export_sales_to_csv(start_date, end_date, self.cashier_filter, output_path=filepath.replace('.xlsx', '.csv'))
                QMessageBox.information(self, "Export Complete", f"Report saved (as CSV) to:\n{saved_path}")
    
    def export_low_stock(self):
        """Export low stock to CSV"""
        # Get default path
        default_dir = settings_service.get("system", "reports_path") or os.path.expanduser("~/Documents")
        default_filename = f"low_stock_{date.today().isoformat()}.csv"
        
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Save Report", os.path.join(default_dir, default_filename), "CSV Files (*.csv)"
        )
        
        if filepath:
            saved_path = report_service.export_inventory_to_csv(output_path=filepath)
            QMessageBox.information(self, "Export Complete", f"Report saved to:\n{saved_path}")
    
    def create_backup(self):
        """Create database backup with password protection"""
        from ui.components.backup_password_dialog import BackupPasswordDialog
        from ui.components.action_success_dialog import ActionSuccessDialog
        
        # Show password dialog
        dialog = BackupPasswordDialog(self)
        
        if dialog.exec() == BackupPasswordDialog.DialogCode.Accepted:
            # Create secure backup with the provided password
            zip_password = dialog.get_backup_password()
            
            success, message, path = backup_service.create_secure_backup(zip_password)
            
            if success:
                # Show success dialog
                success_dialog = ActionSuccessDialog(
                    title="Backup Complete",
                    message=f"Secure backup created!\n\nSaved to:\n{path}",
                    parent=self
                )
                success_dialog.exec()
            else:
                QMessageBox.warning(self, "Backup Failed", message)
