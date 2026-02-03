from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, 
    QPushButton, QHBoxLayout, QSpinBox, QFrame, QWidget
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor
from typing import List
from database.models import Product

class ProductSelectionDialog(QDialog):
    """Custom dialog for selecting a product from multiple matches"""
    
    def __init__(self, products: List[Product], parent=None):
        super().__init__(parent)
        self.products = products
        self.selected_product = None
        self.selected_quantity = 1
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Select Product")
        self.setMinimumSize(600, 500)
        self.setStyleSheet("""
            QDialog {
                background-color: #1E1E1E;
                color: #FFFFFF;
            }
            QLabel { color: #FFFFFF; }
            QSpinBox {
                background-color: #2C2C2C;
                border: 1px solid #333333;
                color: #FFFFFF;
                padding: 6px;
                font-size: 16px;
                border-radius: 4px;
            }
            QSpinBox:focus { border: 1px solid #03DAC6; }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        title = QLabel("Multiple Products Found")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #03DAC6;")
        layout.addWidget(title)
        
        subtitle = QLabel("Please select the correct product from the list below:")
        subtitle.setStyleSheet("color: #B0B0B0; font-size: 14px;")
        layout.addWidget(subtitle)
        
        # List
        self.list_widget = QListWidget()
        self.list_widget.installEventFilter(self) # Intercept keys
        self.list_widget.setWordWrap(True) # Prevent text compression/cutoff
        self.list_widget.setStyleSheet("""
            QListWidget {
                background-color: #2C2C2C;
                border: 1px solid #333333;
                border-radius: 4px;
                padding: 5px;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #333333;
            }
            QListWidget::item:selected {
                background-color: #03DAC6;
                color: #000000;
            }
            QListWidget::item:hover:!selected {
                background-color: #333333;
            }
        """)
        
        for product in self.products:
            item = QListWidgetItem(f"{product.name}")
            # Display: Name \n Barcode • Stock • Price
            stock_str = f"{product.stock_quantity} units"
            display_text = (
                f"{product.name}\n"
                f"Barcode: {product.barcode}  •  "
                f"Stock: {stock_str}  •  "
                f"Price: ₱{product.price:.2f}"
            )
            item.setText(display_text)
            item.setData(Qt.ItemDataRole.UserRole, product)
            # Make item taller to fit text comfortably
            item.setSizeHint(QSize(0, 85))
            
            # Optional: Low stock warning color
            if product.is_low_stock:
                item.setForeground(QColor("#FFB800"))
            elif product.is_out_of_stock:
                item.setForeground(QColor("#CF6679"))
                
            self.list_widget.addItem(item)
            
        # Connect Selection Changed to update UI
        self.list_widget.itemSelectionChanged.connect(self.on_selection_changed)
        self.list_widget.itemDoubleClicked.connect(self.accept_selection)
        layout.addWidget(self.list_widget)
        
        # Quantity and Stock Info
        control_panel = QFrame()
        control_panel.setStyleSheet("background-color: #252525; border-radius: 6px; padding: 10px;")
        control_layout = QHBoxLayout(control_panel)
        control_layout.setContentsMargins(10, 5, 10, 5)
        
        qty_label = QLabel("Quantity:")
        qty_label.setStyleSheet("font-weight: bold; color: #B0B0B0;")
        control_layout.addWidget(qty_label)
        
        # Quantity Widget Container
        qty_widget = QWidget()
        qty_layout = QHBoxLayout(qty_widget)
        qty_layout.setContentsMargins(0, 0, 0, 0)
        qty_layout.setSpacing(5)
        
        # Minus Button
        self.minus_btn = QPushButton("-")
        self.minus_btn.setFixedSize(36, 36)
        self.minus_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.minus_btn.setStyleSheet("""
            QPushButton {
                background-color: #2D3A5A;
                color: #FFFFFF;
                border: 1px solid #3D4A6A;
                border-radius: 4px;
                font-family: Arial;
                font-size: 18px;
                font-weight: bold;
                padding: 0px;
            }
            QPushButton:hover { background-color: #3D4A6A; }
            QPushButton:disabled { background-color: #1A1A1A; border: none; color: #555; }
        """)
        self.minus_btn.clicked.connect(self.decrement_qty)
        qty_layout.addWidget(self.minus_btn)
        
        # SpinBox (Hidden buttons)
        self.qty_spinbox = QSpinBox()
        self.qty_spinbox.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self.qty_spinbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.qty_spinbox.setMinimum(1)
        self.qty_spinbox.setMaximum(999)
        self.qty_spinbox.setValue(1)
        self.qty_spinbox.setFixedSize(50, 36)
        self.qty_spinbox.setEnabled(False) 
        self.qty_spinbox.setStyleSheet("""
            QSpinBox {
                background-color: #2C2C2C;
                border: 1px solid #333333;
                color: #FFFFFF;
                font-size: 16px;
                font-weight: bold;
                border-radius: 4px;
            }
            QSpinBox:disabled { color: #555; background-color: #1A1A1A; }
        """)
        qty_layout.addWidget(self.qty_spinbox)
        
        # Plus Button
        self.plus_btn = QPushButton("+")
        self.plus_btn.setFixedSize(36, 36)
        self.plus_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.plus_btn.setStyleSheet("""
            QPushButton {
                background-color: #03DAC6;
                color: #000000;
                border: none;
                border-radius: 4px;
                font-family: Arial;
                font-size: 18px;
                font-weight: bold;
                padding: 0px;
            }
            QPushButton:hover { background-color: #05E5D0; }
            QPushButton:disabled { background-color: #333; color: #555; }
        """)
        self.plus_btn.clicked.connect(self.increment_qty)
        qty_layout.addWidget(self.plus_btn)
        
        self.minus_btn.setEnabled(False)
        self.plus_btn.setEnabled(False)
        
        control_layout.addWidget(qty_widget)
        
        control_layout.addSpacing(20)
        
        # Total Price Label
        self.total_label = QLabel("Total: ₱0.00")
        self.total_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #03DAC6;")
        control_layout.addWidget(self.total_label)
        
        control_layout.addSpacing(20)
        
        self.stock_info_label = QLabel("Select a product...")
        self.stock_info_label.setStyleSheet("color: #888; font-style: italic;")
        control_layout.addWidget(self.stock_info_label)
        
        control_layout.addStretch()
        layout.addWidget(control_panel)
        
        # Connect signals
        self.qty_spinbox.valueChanged.connect(self.update_total_price)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #CF6679;
                color: #CF6679;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: rgba(207, 102, 121, 0.1); }
        """)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        
        self.select_btn = QPushButton("Add to Cart")
        self.select_btn.setObjectName("successButton")
        self.select_btn.setStyleSheet("""
            QPushButton {
                background-color: #03DAC6;
                color: #000000;
                border: none;
                padding: 10px 24px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #05E5D0; }
            QPushButton:disabled { background-color: #333; color: #555; }
        """)
        self.select_btn.clicked.connect(self.accept_selection)
        self.select_btn.setEnabled(False)
        btn_layout.addWidget(self.select_btn)
        
        layout.addLayout(btn_layout)
        
    def decrement_qty(self):
        """Decrease quantity"""
        self.qty_spinbox.stepDown()
        
    def increment_qty(self):
        """Increase quantity"""
        self.qty_spinbox.stepUp()
        
    def update_total_price(self):
        """Update the total price label based on qty"""
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            self.total_label.setText("Total: ₱0.00")
            return
            
        product = selected_items[0].data(Qt.ItemDataRole.UserRole)
        qty = self.qty_spinbox.value()
        total = product.price * qty
        self.total_label.setText(f"Total: ₱{total:,.2f}")

    def on_selection_changed(self):
        """Update UI based on selection"""
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            self.qty_spinbox.setEnabled(False)
            self.minus_btn.setEnabled(False)
            self.plus_btn.setEnabled(False)
            self.select_btn.setEnabled(False)
            self.stock_info_label.setText("Select a product...")
            self.total_label.setText("Total: ₱0.00")
            return
            
        product = selected_items[0].data(Qt.ItemDataRole.UserRole)
        self.qty_spinbox.setEnabled(True)
        self.select_btn.setEnabled(True)
        
        # Update styling based on stock
        if product.stock_quantity > 0:
            self.stock_info_label.setText(f"Available: {product.stock_quantity}")
            self.stock_info_label.setStyleSheet("color: #03DAC6; font-weight: bold;")
            self.qty_spinbox.setMaximum(product.stock_quantity)
            if self.qty_spinbox.value() > product.stock_quantity:
                self.qty_spinbox.setValue(product.stock_quantity)
            else:
                # Re-trigger calculation if value didn't change (e.g. was 1 and stays 1)
                self.update_total_price()
                
            self.minus_btn.setEnabled(True)
            self.plus_btn.setEnabled(True)
            self.select_btn.setText("Add to Cart")
        else:
            self.stock_info_label.setText("Out of Stock")
            self.stock_info_label.setStyleSheet("color: #CF6679; font-weight: bold;")
            self.qty_spinbox.setEnabled(False)
            self.minus_btn.setEnabled(False)
            self.plus_btn.setEnabled(False)
            self.select_btn.setEnabled(False)
            self.select_btn.setText("Out of Stock")
            self.total_label.setText("Total: ₱0.00")

    def accept_selection(self):
        """Handle selection"""
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            return
            
        self.selected_product = selected_items[0].data(Qt.ItemDataRole.UserRole)
        self.selected_quantity = self.qty_spinbox.value()
        self.accept()
        
    def eventFilter(self, source, event):
        """Intercept keys from list widget"""
        if source == self.list_widget and event.type() == event.Type.KeyPress:
            if event.text() == "+" or event.key() == Qt.Key.Key_Plus:
                if self.qty_spinbox.isEnabled():
                    self.increment_qty()
                    return True
            elif event.text() == "-" or event.key() == Qt.Key.Key_Minus:
                if self.qty_spinbox.isEnabled():
                    self.decrement_qty()
                    return True
            # Also allow '=' as plus without shift
            elif event.key() == Qt.Key.Key_Equal:
                 if self.qty_spinbox.isEnabled():
                    self.increment_qty()
                    return True
                    
        return super().eventFilter(source, event)

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts (fallback)"""
        # ... logic ...
        if event.text() == "+" or event.key() == Qt.Key.Key_Plus:
            if self.qty_spinbox.isEnabled():
                self.increment_qty()
        elif event.text() == "-" or event.key() == Qt.Key.Key_Minus:
            if self.qty_spinbox.isEnabled():
                self.decrement_qty()
        elif event.key() == Qt.Key.Key_Equal:
             if self.qty_spinbox.isEnabled():
                self.increment_qty()
        elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if self.select_btn.isEnabled():
                self.accept_selection()
        elif event.key() == Qt.Key.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)

    def showEvent(self, event):
        """Auto-focus list on show"""
        super().showEvent(event)
        self.list_widget.setFocus()
        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)
        
    def get_selected_product(self) -> Product:
        return self.selected_product

    def get_selected_quantity(self) -> int:
        return self.selected_quantity
