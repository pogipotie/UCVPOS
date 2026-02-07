"""
Product Form Component - Add/Edit product dialog
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QDoubleSpinBox, QSpinBox, QDateEdit,
    QCheckBox, QPushButton, QLabel, QMessageBox, QFrame,
    QGraphicsDropShadowEffect, QWidget
)
from PyQt6.QtCore import Qt, QDate, QPoint
from PyQt6.QtGui import QColor, QFont, QDoubleValidator, QIntValidator
from database.models import Product
from datetime import date
from ui.components.custom_calendar import YearDropdownCalendarWidget


class ProductFormDialog(QDialog):
    """Dialog for adding or editing a product"""
    
    def __init__(self, parent=None, product: Product = None):
        super().__init__(parent)
        self.product = product or Product()
        self.is_edit_mode = product is not None and product.id is not None
        
        # Window Setup
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(700, 550)
        
        # Dragging state
        self.old_pos = None
        
        self.setup_ui()
        
        if self.is_edit_mode:
            self.populate_form()
            
    def setup_ui(self):
        # Main Layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Container
        self.container = QFrame()
        self.container.setStyleSheet("""
            QFrame {
                background-color: #1E1E1E;
                border: 1px solid #333333;
                border-radius: 0px;
            }
        """)
        
        # Drop Shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 8)
        self.container.setGraphicsEffect(shadow)
        
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        # --- Header ---
        header = QFrame()
        header.setStyleSheet("""
            background-color: #252525;
            border-bottom: 1px solid #333333;
            border-radius: 0px;
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 15, 20, 15)
        
        title_text = "Edit Product" if self.is_edit_mode else "Add New Product"
        title_lbl = QLabel(title_text)
        title_lbl.setStyleSheet("color: #03DAC6; font-size: 18px; font-weight: bold; border: none;")
        header_layout.addWidget(title_lbl)
        
        header_layout.addStretch()
        
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #B3B3B3;
                border: none;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #FFFFFF;
                background-color: #CF6679;
                border-radius: 0px;
            }
        """)
        close_btn.clicked.connect(self.reject)
        header_layout.addWidget(close_btn)
        
        container_layout.addWidget(header)
        
        # --- Content ---
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(25, 25, 25, 25)
        content_layout.setSpacing(30)
        
        # Left Column (Essential)
        left_col = QVBoxLayout()
        left_col.setSpacing(20)
        
        # Barcode
        barcode_group = self._create_input_group("Barcode *", "Scan or enter barcode")
        self.barcode_input = barcode_group.findChild(QLineEdit)
        self.barcode_input.setObjectName("barcodeInput") # Use special style
        left_col.addWidget(barcode_group)
        
        # Name
        name_group = self._create_input_group("Product Name *", "e.g. Paracetamol 500mg")
        self.name_input = name_group.findChild(QLineEdit)
        left_col.addWidget(name_group)
        
        # Price Row
        price_row = QHBoxLayout()
        
        # Price
        price_group = self._create_input_group("Selling Price (₱)", "Required")
        self.price_input = price_group.findChild(QLineEdit)
        self.price_input.setValidator(QDoubleValidator(0.00, 999999.99, 2))
        price_row.addWidget(price_group)
        
        # Cost Price
        cost_group = self._create_input_group("Cost Price (₱)", "Required")
        self.cost_input = cost_group.findChild(QLineEdit)
        self.cost_input.setValidator(QDoubleValidator(0.00, 999999.99, 2))
        price_row.addWidget(cost_group)
        
        left_col.addLayout(price_row)
        
        content_layout.addLayout(left_col, 1)
        
        # Right Column (Details)
        right_col = QVBoxLayout()
        right_col.setSpacing(20)
        
        # Details Row
        details_row = QHBoxLayout()
        
        stock_group = self._create_input_group("Stock Qty", "Required")
        self.stock_input = stock_group.findChild(QLineEdit)
        self.stock_input.setValidator(QIntValidator(0, 999999))
        details_row.addWidget(stock_group)
        
        min_stock_group = self._create_input_group("Min Limit", "Required")
        self.min_stock_input = min_stock_group.findChild(QLineEdit)
        self.min_stock_input.setValidator(QIntValidator(0, 999999))
        details_row.addWidget(min_stock_group)
        
        batch_group = self._create_input_group("Batch No.", "Optional")
        self.batch_input = batch_group.findChild(QLineEdit)
        details_row.addWidget(batch_group)
        
        right_col.addLayout(details_row)
        
        # Expiry Section
        expiry_container = QFrame()
        expiry_container.setStyleSheet("background-color: #252525; border-radius: 0px; padding: 10px;")
        expiry_layout = QVBoxLayout(expiry_container)
        
        self.has_expiry_checkbox = QCheckBox("Track Expiry Date")
        self.has_expiry_checkbox.setStyleSheet("color: white; font-weight: bold;")
        self.has_expiry_checkbox.stateChanged.connect(self.toggle_expiry)
        expiry_layout.addWidget(self.has_expiry_checkbox)
        
        self.expiry_input = QDateEdit()
        self.expiry_input.setCalendarPopup(True)
        self.expiry_input.setCalendarWidget(YearDropdownCalendarWidget())
        self.expiry_input.setDisplayFormat("yyyy-MM-dd")
        self.expiry_input.setDate(QDate.currentDate().addYears(1))
        self.expiry_input.setEnabled(False)
        self.expiry_input.setStyleSheet("color: white; padding: 5px; background-color: #1E1E1E;")
        expiry_layout.addWidget(self.expiry_input)
        
        right_col.addWidget(expiry_container)
        
        # Prescription Checkbox (Large)
        self.prescription_checkbox = QCheckBox("Rx Prescription Required")
        self.prescription_checkbox.setCursor(Qt.CursorShape.PointingHandCursor)
        self.prescription_checkbox.setStyleSheet("""
            QCheckBox {
                color: #B3B3B3; font-size: 14px; padding: 10px;
                border: 1px dashed #444; border-radius: 0px;
            }
            QCheckBox::indicator { width: 20px; height: 20px; }
            QCheckBox:checked {
                color: #FFB800; border-color: #FFB800; background-color: rgba(255, 184, 0, 0.1);
            }
        """)
        right_col.addWidget(self.prescription_checkbox)
        
        right_col.addStretch()
        content_layout.addLayout(right_col, 1)
        
        container_layout.addWidget(content_widget)
        
        # --- Footer ---
        footer = QFrame()
        footer.setStyleSheet("""
            background-color: #252525;
            border-top: 1px solid #333333;
            border-radius: 0px;
        """)
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(20, 15, 20, 15)
        footer_layout.setSpacing(15)
        
        footer_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setFixedSize(100, 40)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent; border: 1px solid #444; 
                color: #B3B3B3; border-radius: 0px; font-weight: 600;
            }
            QPushButton:hover { background-color: #333; color: white; }
        """)
        cancel_btn.clicked.connect(self.reject)
        footer_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save Product")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setFixedSize(140, 40)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #03DAC6; border: none; 
                color: black; border-radius: 0px; font-weight: bold; font-size: 14px;
            }
            QPushButton:hover { background-color: #05E5D0; }
            QPushButton:pressed { background-color: #018786; }
        """)
        save_btn.clicked.connect(self.save_product)
        footer_layout.addWidget(save_btn)
        
        container_layout.addWidget(footer)
        
        main_layout.addWidget(self.container)

    def _create_input_group(self, label_text, placeholder=""):
        group = QFrame()
        group.setStyleSheet("border: none; background: transparent;")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        
        lbl = QLabel(label_text)
        lbl.setStyleSheet("color: #B3B3B3; font-size: 12px; font-weight: 600; text-transform: uppercase;")
        layout.addWidget(lbl)
        
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder)
        line_edit.setStyleSheet("""
            QLineEdit {
                background-color: #2C2C2C; border: 1px solid #333333;
                border-radius: 0px; padding: 8px; color: white; font-size: 14px;
            }
            QLineEdit:focus { border: 1px solid #03DAC6; background-color: #333; }
        """)
        layout.addWidget(line_edit)
        
        return group

    def populate_form(self):
        """Fill form with existing product data"""
        self.barcode_input.setText(self.product.barcode)
        self.name_input.setText(self.product.name)
        # Convert numbers to string for LineEdits
        self.price_input.setText(f"{self.product.price:.2f}" if self.product.price else "")
        self.cost_input.setText(f"{self.product.cost_price:.2f}" if self.product.cost_price else "")
        self.stock_input.setText(str(self.product.stock_quantity))
        self.min_stock_input.setText(str(self.product.min_stock_level))
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
            self._show_error("Barcode is required.")
            self.barcode_input.setFocus()
            return False
        
        if not self.name_input.text().strip():
            self._show_error("Product name is required.")
            self.name_input.setFocus()
            return False
        
        try:
            price = float(self.price_input.text() or 0)
            if price <= 0:
                self._show_error("Price must be greater than 0.")
                self.price_input.setFocus()
                return False
        except ValueError:
            self._show_error("Invalid price format.")
            self.price_input.setFocus()
            return False
        
        return True
    
    # ... (show_error remains same)

    def save_product(self):
        """Validate and save the product"""
        if not self.validate_form():
            return
        
        try:
            self.product.barcode = self.barcode_input.text().strip()
            self.product.name = self.name_input.text().strip()
            self.product.price = float(self.price_input.text() or 0.0)
            self.product.cost_price = float(self.cost_input.text() or 0.0)  # Add cost_price
            self.product.stock_quantity = int(self.stock_input.text() or 0)
            self.product.min_stock_level = int(self.min_stock_input.text() or 0)
            self.product.batch_number = self.batch_input.text().strip() or None
            self.product.prescription_required = self.prescription_checkbox.isChecked()
            
            if self.has_expiry_checkbox.isChecked():
                qdate = self.expiry_input.date()
                self.product.expiry_date = date(qdate.year(), qdate.month(), qdate.day())
            else:
                self.product.expiry_date = None
            
            self.accept()
        except ValueError:
             self._show_error("Please check your numeric inputs.")
             return
    
    def get_product(self) -> Product:
        """Get the product data from the form"""
        return self.product

    def toggle_expiry(self, state):
        """Enable/Disable expiry date input"""
        is_checked = (state == Qt.CheckState.Checked.value or state == 2)
        self.expiry_input.setEnabled(is_checked)
        
        if is_checked:
            self.expiry_input.setStyleSheet("color: white; padding: 5px; background-color: #1E1E1E; border: 1px solid #03DAC6;")
        else:
            self.expiry_input.setStyleSheet("color: #777; padding: 5px; background-color: #1E1E1E; border: 1px solid #333;")

    def _show_error(self, message):
        """Show error toast or message box"""
        QMessageBox.warning(self, "Validation Error", message)

    # --- Dragging Logic ---
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.pos() + delta)
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.old_pos = None
