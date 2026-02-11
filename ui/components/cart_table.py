"""
Cart Table Component - Shopping cart display with quantity controls
"""
from PyQt6.QtWidgets import (
    QTableWidget, QTableWidgetItem, QWidget, QVBoxLayout, 
    QHBoxLayout, QPushButton, QLabel, QHeaderView, QAbstractItemView, QFrame, QStyle
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QColor, QFont
from typing import List
from database.models import CartItem


class CartTable(QWidget):
    """Shopping cart table with edit functionality"""
    
    quantity_changed = pyqtSignal(int, int)  # product_id, new_quantity
    item_removed = pyqtSignal(int)  # product_id
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.cart_items: List[CartItem] = []
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Shopping Cart")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFFFFF;")
        header_layout.addWidget(title)
        
        self.item_count_label = QLabel("0 items")
        self.item_count_label.setStyleSheet("color: #B0B0B0;")
        header_layout.addStretch()
        header_layout.addWidget(self.item_count_label)
        
        layout.addLayout(header_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Product", "Price", "Qty", "Subtotal", ""])
        
        # Align headers
        header_item = self.table.horizontalHeaderItem(0)
        if header_item:
            header_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        # Modern Column sizing
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)          # Product Name
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents) # Price
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)            # Qty
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents) # Subtotal
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)            # Remove
        
        self.table.setColumnWidth(2, 110) # Qty Width
        self.table.setColumnWidth(4, 50)  # Remove Width
        
        # Styling
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(64) # Taller rows
        self.table.setShowGrid(False)
        self.table.setFrameShape(QFrame.Shape.NoFrame)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: transparent;
                selection-background-color: #2D3A5A;
                selection-color: #FFFFFF;
            }
            QTableWidget::item {
                padding: 5px;
                border-bottom: 1px solid #2D2D2D;
            }
        """)
        
        layout.addWidget(self.table, 1)
        
        # Total section with VAT breakdown
        total_frame = QWidget()
        total_frame.setObjectName("highlightFrame")
        total_frame.setStyleSheet("""
            QWidget#highlightFrame {
                background-color: #1F2B47;
                border: 2px solid #0D7377;
                border-radius: 0px;
                padding: 10px;
            }
        """)
        total_layout = QVBoxLayout(total_frame)
        total_layout.setSpacing(5)
        
        # Net Amount (without VAT)
        net_row = QHBoxLayout()
        net_text = QLabel("Net Amount:")
        net_text.setStyleSheet("font-size: 14px; color: #B0B0B0;")
        net_row.addWidget(net_text)
        net_row.addStretch()
        self.net_label = QLabel("₱0.00")
        self.net_label.setStyleSheet("font-size: 14px; color: #B0B0B0;")
        net_row.addWidget(self.net_label)
        total_layout.addLayout(net_row)
        
        # VAT Amount
        vat_row = QHBoxLayout()
        vat_text = QLabel("VAT (12%):")
        vat_text.setStyleSheet("font-size: 14px; color: #B0B0B0;")
        vat_row.addWidget(vat_text)
        vat_row.addStretch()
        self.vat_label = QLabel("₱0.00")
        self.vat_label.setStyleSheet("font-size: 14px; color: #B0B0B0;")
        vat_row.addWidget(self.vat_label)
        total_layout.addLayout(vat_row)
        
        # Total (VAT-inclusive)
        total_row = QHBoxLayout()
        total_text = QLabel("TOTAL:")
        total_text.setStyleSheet("font-size: 20px; font-weight: bold;")
        total_row.addWidget(total_text)
        total_row.addStretch()
        self.total_label = QLabel("₱0.00")
        self.total_label.setObjectName("totalLabel")
        total_row.addWidget(self.total_label)
        total_layout.addLayout(total_row)
        
        layout.addWidget(total_frame)
    
    def update_cart(self, items: List[CartItem], discount_type: str = None, is_discounted: bool = False):
        """Update the cart display with new items"""
        self.cart_items = items
        self.table.setRowCount(len(items))
        
        total = 0.0
        
        for row, item in enumerate(items):
            # Product name
            name_item = QTableWidgetItem(item.product.name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            name_item.setData(Qt.ItemDataRole.UserRole, item.product.id)
            name_item.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            self.table.setItem(row, 0, name_item)
            
            # Unit price
            price_item = QTableWidgetItem(f"₱{item.product.price:.2f}")
            price_item.setFlags(price_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            price_item.setFont(QFont("Segoe UI", 12))
            self.table.setItem(row, 1, price_item)
            
            # Quantity with controls
            qty_widget = self._create_quantity_widget(item.product.id, item.quantity)
            self.table.setCellWidget(row, 2, qty_widget)
            
            # Subtotal
            subtotal = item.subtotal
            total += subtotal
            subtotal_item = QTableWidgetItem(f"₱{subtotal:.2f}")
            subtotal_item.setFlags(subtotal_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            subtotal_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            subtotal_item.setForeground(QColor("#03DAC6"))
            subtotal_item.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
            self.table.setItem(row, 3, subtotal_item)
            
            # Remove button
            remove_btn = QPushButton()
            remove_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_TrashIcon))
            remove_btn.setFixedSize(36, 36)
            remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            remove_btn.setToolTip("Remove Item")
            remove_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: 1px solid #E94560;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #E94560;
                    border: none;
                }
            """)
            remove_btn.clicked.connect(lambda checked, pid=item.product.id: self.item_removed.emit(pid))
            
            # Center the button
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            btn_layout.addWidget(remove_btn)
            
            self.table.setCellWidget(row, 4, btn_widget)
        
        # Update totals based on discount status
        if is_discounted:
            # SC/PWD: VAT exempt + 20% discount
            vat_exempt_total = total / 1.12
            sc_pwd_discount = vat_exempt_total * 0.20
            final_total = vat_exempt_total - sc_pwd_discount
            
            # Show VAT-exempt amount as "Net"
            self.net_label.setText(f"₱{vat_exempt_total:,.2f}")
            # Show discount amount (VAT saved + 20%)
            discount_label = "SC" if discount_type == 'SC' else "PWD"
            self.vat_label.setText(f"-₱{sc_pwd_discount:,.2f} ({discount_label} 20%)")
            self.vat_label.setStyleSheet("font-size: 14px; color: #FFB800; font-weight: bold;")
            self.total_label.setText(f"₱{final_total:,.2f}")
        else:
            # Normal: Show VAT breakdown
            from services.settings_service import settings_service
            tax_rate = settings_service.get('financial', 'tax_rate') or 12.0
            
            vat_amount = total - (total / (1 + tax_rate / 100)) if tax_rate > 0 else 0
            net_amount = total - vat_amount
            
            self.net_label.setText(f"₱{net_amount:,.2f}")
            self.vat_label.setText(f"₱{vat_amount:,.2f}")
            self.vat_label.setStyleSheet("font-size: 14px; color: #B0B0B0;")
            self.total_label.setText(f"₱{total:,.2f}")
        
        self.item_count_label.setText(f"{sum(i.quantity for i in items)} items")
        
        # Auto-select the last item for convenience
        if self.table.rowCount() > 0:
            self.table.selectRow(self.table.rowCount() - 1)
            # Ensure visible
            self.table.scrollToBottom()
    
    def _create_quantity_widget(self, product_id: int, quantity: int) -> QWidget:
        """Create quantity adjustment widget"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Minus button
        minus_btn = QPushButton("-")
        minus_btn.setFixedSize(32, 32)
        minus_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        minus_btn.setStyleSheet("""
            QPushButton {
                background-color: #2D3A5A;
                color: #FFFFFF;
                border: 1px solid #3D4A6A;
                border-radius: 4px;
                font-family: Arial;
                font-size: 18px;
                font-weight: bold;
                padding: 0px;
                margin: 0px;
            }
            QPushButton:hover {
                background-color: #3D4A6A;
                border-color: #4D5A7A;
            }
        """)
        minus_btn.clicked.connect(lambda: self.quantity_changed.emit(product_id, quantity - 1))
        layout.addWidget(minus_btn)
        
        # Quantity label
        qty_label = QLabel(str(quantity))
        qty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        qty_label.setMinimumWidth(30)
        qty_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #FFFFFF;")
        layout.addWidget(qty_label)
        
        # Plus button
        plus_btn = QPushButton("+")
        plus_btn.setFixedSize(32, 32)
        plus_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        plus_btn.setStyleSheet("""
            QPushButton {
                background-color: #03DAC6;
                color: #000000;
                border: none;
                border-radius: 4px;
                font-family: Arial;
                font-size: 18px;
                font-weight: bold;
                padding: 0px;
                margin: 0px;
            }
            QPushButton:hover {
                background-color: #05E5D0;
            }
        """)
        plus_btn.clicked.connect(lambda: self.quantity_changed.emit(product_id, quantity + 1))
        layout.addWidget(plus_btn)
        
        return widget
    
    def clear_cart(self):
        """Clear the cart display"""
        self.table.setRowCount(0)
        self.cart_items = []
        self.net_label.setText("₱0.00")
        self.vat_label.setText("₱0.00")
        self.total_label.setText("₱0.00")
        self.item_count_label.setText("0 items")
    
    def get_selected_product_id(self) -> int:
        """Get the product ID of the selected row"""
        row = self.table.currentRow()
        if row >= 0:
            item = self.table.item(row, 0)
            if item:
                return item.data(Qt.ItemDataRole.UserRole)
        return None
