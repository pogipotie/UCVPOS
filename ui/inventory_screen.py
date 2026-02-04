"""
Inventory Screen - Product management interface
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QTableWidget, QTableWidgetItem, QLineEdit,
    QMessageBox, QHeaderView, QAbstractItemView, QFrame, QStyle
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor

from ui.components.barcode_input import BarcodeInput
from ui.components.product_form import ProductFormDialog
from services.inventory_service import inventory_service
from services.auth_service import auth_service
from database.models import Product
from ui.styles import LOW_STOCK_STYLE, EXPIRED_STYLE, OUT_OF_STOCK_STYLE


class InventoryScreen(QWidget):
    """Inventory management screen"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_page = 0
        self.page_size = 50
        self.setup_ui()
        self.load_products()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(24)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_block = QVBoxLayout()
        title = QLabel("Inventory Management")
        title.setObjectName("titleLabel")
        subtitle = QLabel("Manage products, stock levels, and pricing")
        subtitle.setObjectName("subtitleLabel")
        title_block.addWidget(title)
        title_block.addWidget(subtitle)
        header_layout.addLayout(title_block)
        
        header_layout.addStretch()
        
        # Product count
        self.count_label = QLabel("0 products")
        self.count_label.setStyleSheet("color: #B0B0B0; margin-right: 15px;")
        header_layout.addWidget(self.count_label)
        
        # Add Product Button
        self.add_btn = QPushButton("✚ Add New Product")
        self.add_btn.setObjectName("primaryButton")
        self.add_btn.setMinimumHeight(45)
        self.add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_btn.clicked.connect(self.add_product)
        header_layout.addWidget(self.add_btn)
        
        layout.addLayout(header_layout)
        
        # Control Card (Search & Filter)
        control_card = QFrame()
        control_card.setObjectName("cardFrame")
        control_layout = QHBoxLayout(control_card)
        control_layout.setContentsMargins(20, 20, 20, 20)
        control_layout.setSpacing(20)
        
        # Search Box
        search_layout = QVBoxLayout()
        search_layout.setSpacing(4)
        search_label = QLabel("Search Products")
        search_label.setStyleSheet("color: #B3B3B3; font-size: 11px; font-weight: bold; text-transform: uppercase;")
        search_layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Scan barcode or type name...")
        self.search_input.setMinimumWidth(300)
        self.search_input.textChanged.connect(self.on_search)
        search_layout.addWidget(self.search_input)
        
        control_layout.addLayout(search_layout)
        
        # Filter (Buttons converted to nice layout)
        filter_layout = QVBoxLayout()
        filter_layout.setSpacing(4)
        filter_label = QLabel("Filter View")
        filter_label.setStyleSheet("color: #B3B3B3; font-size: 11px; font-weight: bold; text-transform: uppercase;")
        filter_layout.addWidget(filter_label)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        
        self.filter_all_btn = QPushButton("All")
        self.filter_all_btn.setCheckable(True)
        self.filter_all_btn.setChecked(True)
        self.filter_all_btn.clicked.connect(lambda: self.apply_filter("all"))
        btn_layout.addWidget(self.filter_all_btn)
        
        self.filter_low_btn = QPushButton("Low Stock")
        self.filter_low_btn.setCheckable(True)
        self.filter_low_btn.clicked.connect(lambda: self.apply_filter("low_stock"))
        btn_layout.addWidget(self.filter_low_btn)
        
        self.filter_expired_btn = QPushButton("Expired")
        self.filter_expired_btn.setCheckable(True)
        self.filter_expired_btn.setObjectName("dangerButton") # Style expired button red
        self.filter_expired_btn.clicked.connect(lambda: self.apply_filter("expired"))
        btn_layout.addWidget(self.filter_expired_btn)
        
        filter_layout.addLayout(btn_layout)
        control_layout.addLayout(filter_layout)
        
        control_layout.addStretch()
        
        # Pagination info
        page_layout = QVBoxLayout()
        page_layout.setSpacing(4)
        page_label = QLabel("Navigation")
        page_label.setStyleSheet("color: #B3B3B3; font-size: 11px; font-weight: bold; text-transform: uppercase;")
        page_layout.addWidget(page_label)
        
        nav_controls = QHBoxLayout()
        
        # Navigation Button Style
        nav_btn_style = """
            QPushButton {
                padding: 0px;
                background-color: #2D3A5A;
                border: 1px solid #3D4A6A;
                color: #FFFFFF;
                font-size: 18px;
                border-radius: 4px;
                font-family: Arial;
            }
            QPushButton:hover {
                background-color: #3D4A6A;
                border-color: #4D5A7A;
            }
            QPushButton:disabled {
                background-color: #1A1A1A;
                color: #444;
                border: 1px solid #222;
            }
        """
        
        self.prev_btn = QPushButton("◀")
        self.prev_btn.setFixedSize(32, 32)
        self.prev_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.prev_btn.setStyleSheet(nav_btn_style)
        self.prev_btn.clicked.connect(self.prev_page)
        
        self.page_label = QLabel("Page 1")
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.page_label.setFixedWidth(80)
        self.page_label.setStyleSheet("color: #FFFFFF; font-weight: bold;")
        
        self.next_btn = QPushButton("▶")
        self.next_btn.setFixedSize(32, 32)
        self.next_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.next_btn.setStyleSheet(nav_btn_style)
        self.next_btn.clicked.connect(self.next_page)
        
        nav_controls.addWidget(self.prev_btn)
        nav_controls.addWidget(self.page_label)
        nav_controls.addWidget(self.next_btn)
        
        page_layout.addLayout(nav_controls)
        control_layout.addLayout(page_layout)
        
        layout.addWidget(control_card)
        
        # Product Table
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "Barcode", "Name", "Price", "Stock", "Min", 
            "Batch", "Expiry", "Rx", "Actions"
        ])
        
        # Modern Table Styles
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setFrameShape(QFrame.Shape.NoFrame)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        
        # Column sizing
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch) # Name
        self.table.setColumnWidth(0, 140)
        self.table.setColumnWidth(2, 90)
        self.table.setColumnWidth(3, 70)
        self.table.setColumnWidth(4, 70)
        self.table.setColumnWidth(7, 50) # Rx
        self.table.setColumnWidth(8, 160) # Actions
        
        # Row height
        self.table.verticalHeader().setDefaultSectionSize(50)
        
        layout.addWidget(self.table, 1)
        
        self.apply_permissions()
        
    def apply_permissions(self):
        """Apply role-based restrictions"""
        user = auth_service.get_current_user()
        if user and user.role == "cashier":
            # Hide Add Button
            self.add_btn.hide()
            
            # Hide Actions Column (Last column = 8)
            self.table.setColumnHidden(8, True)
    
    def load_products(self, filter_type: str = "all"):
        """Load products into the table"""
        if filter_type == "low_stock":
            products = inventory_service.get_low_stock_products()
        elif filter_type == "expired":
            products = inventory_service.get_expired_products()
        else:
            products = inventory_service.get_all_products(
                limit=self.page_size,
                offset=self.current_page * self.page_size
            )
        
        self.table.setRowCount(len(products))
        
        for row, product in enumerate(products):
            self._add_product_row(row, product)
        
        # Update count
        total = inventory_service.get_product_count()
        self.count_label.setText(f"{total} products total")
        
        # Update pagination
        self.page_label.setText(f"Page {self.current_page + 1}")
        self.prev_btn.setEnabled(self.current_page > 0)
        self.next_btn.setEnabled(len(products) == self.page_size)
    
    def _add_product_row(self, row: int, product: Product):
        """Add a product row to the table"""
        # Barcode
        barcode_item = QTableWidgetItem(product.barcode)
        barcode_item.setData(Qt.ItemDataRole.UserRole, product.id)
        barcode_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.table.setItem(row, 0, barcode_item)
        
        # Name
        name_item = QTableWidgetItem(product.name)
        name_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.table.setItem(row, 1, name_item)
        
        # Price
        price_item = QTableWidgetItem(f"₱{product.price:.2f}")
        price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.table.setItem(row, 2, price_item)
        
        # Stock
        stock_item = QTableWidgetItem(str(product.stock_quantity))
        stock_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, 3, stock_item)
        
        # Min Stock
        min_stock_item = QTableWidgetItem(str(product.min_stock_level))
        min_stock_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, 4, min_stock_item)
        
        # Batch
        batch_item = QTableWidgetItem(product.batch_number or "-")
        self.table.setItem(row, 5, batch_item)
        
        # Expiry
        if product.expiry_date:
            expiry_item = QTableWidgetItem(product.expiry_date.isoformat())
        else:
            expiry_item = QTableWidgetItem("-")
        self.table.setItem(row, 6, expiry_item)
        
        # Prescription
        rx_item = QTableWidgetItem("Rx" if product.prescription_required else "")
        rx_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        if product.prescription_required:
            rx_item.setForeground(QColor("#FFB800"))
        self.table.setItem(row, 7, rx_item)
        
        # Actions
        actions_widget = QWidget()
        actions_widget.setStyleSheet("background: transparent;")
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setContentsMargins(4, 2, 4, 2)
        actions_layout.setSpacing(6)
        
        edit_btn = QPushButton(" Edit")
        edit_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogContentsView))
        edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        edit_btn.setFixedHeight(28)
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #03DAC6;
                color: #03DAC6;
                border-radius: 4px;
                padding: 4px 8px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: rgba(3, 218, 198, 0.1);
            }
        """)
        edit_btn.clicked.connect(lambda checked, p=product: self.edit_product(p))
        actions_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("")
        delete_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_TrashIcon))
        delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        delete_btn.setFixedSize(28, 28)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #CF6679;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: rgba(207, 102, 121, 0.1);
            }
        """)
        delete_btn.clicked.connect(lambda checked, p=product: self.delete_product(p))
        actions_layout.addWidget(delete_btn)
        
        self.table.setCellWidget(row, 8, actions_widget)
        
        # Apply row styling based on status
        if product.is_expired:
            for col in range(8):
                item = self.table.item(row, col)
                if item:
                    item.setBackground(QColor("#3D1A1A"))
                    item.setForeground(QColor("#FF4757"))
        elif product.is_out_of_stock:
            for col in range(8):
                item = self.table.item(row, col)
                if item:
                    item.setBackground(QColor("#2D2D2D"))
                    item.setForeground(QColor("#888888"))
        elif product.is_low_stock:
            for col in range(8):
                item = self.table.item(row, col)
                if item:
                    item.setBackground(QColor("#3D2E00"))
                    item.setForeground(QColor("#FFB800"))
    
    def on_search(self, text: str):
        """Handle search input"""
        if len(text) < 2:
            self.load_products()
            return
        
        products = inventory_service.search_products(text)
        self.table.setRowCount(len(products))
        
        for row, product in enumerate(products):
            self._add_product_row(row, product)
    
    def apply_filter(self, filter_type: str):
        """Apply a filter to the product list"""
        # Update button states
        self.filter_all_btn.setChecked(filter_type == "all")
        self.filter_low_btn.setChecked(filter_type == "low_stock")
        self.filter_expired_btn.setChecked(filter_type == "expired")
        
        self.current_page = 0
        self.load_products(filter_type)
    
    def add_product(self):
        """Open dialog to add a new product"""
        dialog = ProductFormDialog(self)
        
        if dialog.exec():
            product = dialog.get_product()
            success, message, product_id = inventory_service.add_product(product)
            
            if success:
                QMessageBox.information(self, "Success", message)
                self.load_products()
            else:
                QMessageBox.warning(self, "Error", message)
    
    def edit_product(self, product: Product):
        """Open dialog to edit a product"""
        dialog = ProductFormDialog(self, product)
        
        if dialog.exec():
            updated_product = dialog.get_product()
            success, message = inventory_service.update_product(updated_product)
            
            if success:
                QMessageBox.information(self, "Success", message)
                self.load_products()
            else:
                QMessageBox.warning(self, "Error", message)
    
    def delete_product(self, product: Product):
        """Delete a product"""
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete '{product.name}'?\n"
            f"This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success, message = inventory_service.delete_product(product.id)
            
            if success:
                QMessageBox.information(self, "Success", message)
                self.load_products()
            else:
                QMessageBox.warning(self, "Error", message)
    
    def prev_page(self):
        """Go to previous page"""
        if self.current_page > 0:
            self.current_page -= 1
            self.load_products()
    
    def next_page(self):
        """Go to next page"""
        self.current_page += 1
        self.load_products()
    
    def refresh(self):
        """Refresh the product list"""
        self.load_products()
