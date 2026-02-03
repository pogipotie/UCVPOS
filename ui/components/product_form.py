"""
Product Form Component - Add/Edit product dialog
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QDoubleSpinBox, QSpinBox, QDateEdit,
    QCheckBox, QPushButton, QLabel, QMessageBox, QGroupBox
)
from PyQt6.QtCore import Qt, QDate
from database.models import Product
from datetime import date
from ui.components.custom_calendar import YearDropdownCalendarWidget


class ProductFormDialog(QDialog):
    """Dialog for adding or editing a product"""
    
    def __init__(self, parent=None, product: Product = None):
        super().__init__(parent)
        self.product = product or Product()
        self.is_edit_mode = product is not None and product.id is not None
        self.setup_ui()
        
        if self.is_edit_mode:
            self.populate_form()
    
    def setup_ui(self):
        self.setWindowTitle("Manage Product")
        self.setMinimumWidth(600)
        self.setModal(True)
        
        # Main Layout
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Header
        header_title = QLabel("Edit Product" if self.is_edit_mode else "Add New Product")
        header_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFFFFF;")
        layout.addWidget(header_title)
        
        # Content Layout (Grid-like)
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)
        
        # Column 1: Basic Info & Pricing
        col1 = QVBoxLayout()
        col1.setSpacing(15)
        
        # Basic Info Group
        basic_group = QGroupBox("Basic Information")
        basic_layout = QFormLayout(basic_group)
        basic_layout.setSpacing(10)
        
        self.barcode_input = QLineEdit()
        self.barcode_input.setPlaceholderText("Scan or enter barcode")
        basic_layout.addRow("Barcode *:", self.barcode_input)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Product name")
        basic_layout.addRow("Name *:", self.name_input)
        
        col1.addWidget(basic_group)
        
        # Pricing Group
        price_group = QGroupBox("Pricing & Stock")
        price_layout = QFormLayout(price_group)
        price_layout.setSpacing(10)
        
        self.price_input = QDoubleSpinBox()
        self.price_input.setPrefix("₱ ")
        self.price_input.setDecimals(2)
        self.price_input.setMaximum(999999.99)
        self.price_input.setMinimum(0)
        price_layout.addRow("Price *:", self.price_input)
        
        self.stock_input = QSpinBox()
        self.stock_input.setMaximum(999999)
        self.stock_input.setMinimum(0)
        price_layout.addRow("Quantity:", self.stock_input)
        
        self.min_stock_input = QSpinBox()
        self.min_stock_input.setMaximum(999999)
        self.min_stock_input.setMinimum(0)
        self.min_stock_input.setValue(10)
        price_layout.addRow("Min Stock:", self.min_stock_input)
        
        col1.addWidget(price_group)
        content_layout.addLayout(col1)
        
        # Column 2: Compliance & Details
        col2 = QVBoxLayout()
        col2.setSpacing(15)
        
        comp_group = QGroupBox("Compliance & Details")
        comp_layout = QVBoxLayout(comp_group)
        comp_layout.setSpacing(15)
        
        # Batch
        batch_layout = QVBoxLayout()
        batch_lbl = QLabel("Batch Number:")
        self.batch_input = QLineEdit()
        self.batch_input.setPlaceholderText("Optional")
        batch_layout.addWidget(batch_lbl)
        batch_layout.addWidget(self.batch_input)
        comp_layout.addLayout(batch_layout)
        
        # Expiry
        expiry_layout = QVBoxLayout()
        
        check_layout = QHBoxLayout()
        self.has_expiry_checkbox = QCheckBox("Has Expiry Date")
        self.has_expiry_checkbox.stateChanged.connect(self.toggle_expiry)
        check_layout.addWidget(self.has_expiry_checkbox)
        check_layout.addStretch()
        expiry_layout.addLayout(check_layout)
        
        self.expiry_input = QDateEdit()
        self.expiry_input.setCalendarPopup(True)
        self.expiry_input.setCalendarWidget(YearDropdownCalendarWidget())
        self.expiry_input.setDisplayFormat("yyyy-MM-dd")
        self.expiry_input.setDate(QDate.currentDate().addYears(1))
        self.expiry_input.setEnabled(False)
        expiry_layout.addWidget(self.expiry_input)
        
        comp_layout.addLayout(expiry_layout)
        
        # Prescription
        self.prescription_checkbox = QCheckBox("Requires Prescription")
        self.prescription_checkbox.setStyleSheet("color: #FFB800; font-weight: bold;")
        comp_layout.addWidget(self.prescription_checkbox)
        
        comp_layout.addStretch()
        col2.addWidget(comp_group)
        
        content_layout.addLayout(col2)
        layout.addLayout(content_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setMinimumHeight(40)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save Product")
        save_btn.setObjectName("primaryButton")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setMinimumHeight(40)
        save_btn.clicked.connect(self.save_product)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
    
    def toggle_expiry(self, state):
        """Enable/disable expiry date input"""
        self.expiry_input.setEnabled(state == Qt.CheckState.Checked.value)
    
    def populate_form(self):
        """Fill form with existing product data"""
        self.barcode_input.setText(self.product.barcode)
        self.name_input.setText(self.product.name)
        self.price_input.setValue(self.product.price)
        self.stock_input.setValue(self.product.stock_quantity)
        self.min_stock_input.setValue(self.product.min_stock_level)
        self.batch_input.setText(self.product.batch_number or "")
        self.prescription_checkbox.setChecked(self.product.prescription_required)
        
        if self.product.expiry_date:
            self.has_expiry_checkbox.setChecked(True)
            self.expiry_input.setDate(QDate(
                self.product.expiry_date.year,
                self.product.expiry_date.month,
                self.product.expiry_date.day
            ))
    
    def validate_form(self) -> bool:
        """Validate form inputs"""
        if not self.barcode_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Barcode is required.")
            self.barcode_input.setFocus()
            return False
        
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Product name is required.")
            self.name_input.setFocus()
            return False
        
        if self.price_input.value() <= 0:
            QMessageBox.warning(self, "Validation Error", "Price must be greater than 0.")
            self.price_input.setFocus()
            return False
        
        return True
    
    def save_product(self):
        """Validate and save the product"""
        if not self.validate_form():
            return
        
        self.product.barcode = self.barcode_input.text().strip()
        self.product.name = self.name_input.text().strip()
        self.product.price = self.price_input.value()
        self.product.stock_quantity = self.stock_input.value()
        self.product.min_stock_level = self.min_stock_input.value()
        self.product.batch_number = self.batch_input.text().strip() or None
        self.product.prescription_required = self.prescription_checkbox.isChecked()
        
        if self.has_expiry_checkbox.isChecked():
            qdate = self.expiry_input.date()
            self.product.expiry_date = date(qdate.year(), qdate.month(), qdate.day())
        else:
            self.product.expiry_date = None
        
        self.accept()
    
    def get_product(self) -> Product:
        """Get the product data from the form"""
        return self.product
