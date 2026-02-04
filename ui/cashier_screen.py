"""
Cashier Screen - Main POS checkout interface
Optimized for fast barcode scanning and keyboard-driven workflow
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QMessageBox, QFrame, QHeaderView, QGroupBox, QInputDialog, QCompleter, QDialog
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QKeySequence, QShortcut

from ui.components.barcode_input import BarcodeInputLarge
from ui.components.cart_table import CartTable
from ui.components.product_selection_dialog import ProductSelectionDialog
from ui.components.sale_success_dialog import SaleSuccessDialog
from ui.components.prescription_dialog import PrescriptionDialog
from ui.payment_dialog import PaymentDialog
from services.sales_service import sales_service
from services.compliance_service import compliance_service
from services.inventory_service import inventory_service
from services.auth_service import auth_service


class CashierScreen(QWidget):
    """Main POS checkout screen"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_shortcuts()
        self.setup_completer() # Initialize autocomplete
        
        # Focus input securely
        QTimer.singleShot(100, lambda: self.barcode_input.focus_input())
        self.start_new_sale()
    
    def setup_completer(self):
        """Setup autocomplete for product names and barcodes"""
        search_terms = inventory_service.get_all_search_terms()
        completer = QCompleter(search_terms)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchStartsWith)
        
        # Handle selection from popup (Click or Enter on suggestion)
        # This triggers the scan logic immediately without needing another Enter
        completer.activated.connect(self.on_barcode_scanned)
        
        self.barcode_input.input_field.setCompleter(completer)

    def setup_ui(self):
        # Main Layout (Fluid)
        layout = QHBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # ----------------------
        # LEFT PANEL (Transaction)
        # ----------------------
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(15)
        
        # Header (Logo/Title Area)
        header_layout = QHBoxLayout()
        
        title_block = QVBoxLayout()
        title = QLabel("Checkout")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #FFFFFF;")
        subtitle = QLabel("Ready for new sale")
        subtitle.setObjectName("subtitleLabel")
        subtitle.setStyleSheet("color: #03DAC6; font-size: 14px;")
        title_block.addWidget(title)
        title_block.addWidget(subtitle)
        header_layout.addLayout(title_block)
        
        header_layout.addStretch()
        
        # Session info removed as per request
        
        left_layout.addLayout(header_layout)
        
        # Scanner Bar (High visibility)
        scan_container = QFrame()
        scan_container.setStyleSheet("""
            QFrame {
                background-color: #1E1E1E;
                border: 1px solid #333333;
                border-radius: 0px;
            }
        """)
        scan_layout = QHBoxLayout(scan_container)
        scan_layout.setContentsMargins(15, 10, 15, 10)
        
        # scan_icon removed to prevent duplicate (BarcodeInputLarge has one)
        
        self.barcode_input = BarcodeInputLarge()
        self.barcode_input.setObjectName("barcodeInput")
        self.barcode_input.setPlaceholderText("Scan barcode or type product name...")
        self.barcode_input.barcode_scanned.connect(self.on_barcode_scanned)
        scan_layout.addWidget(self.barcode_input, 1)
        
        left_layout.addWidget(scan_container)
        
        # Status Toast
        self.status_label = QLabel("")
        self.status_label.setFixedHeight(0) # Hidden by default
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(self.status_label)
        
        # Cart Table (Expands)
        self.cart_table = CartTable()
        self.cart_table.quantity_changed.connect(self.on_quantity_changed)
        self.cart_table.item_removed.connect(self.on_item_removed)
        left_layout.addWidget(self.cart_table, 1)
        
        layout.addWidget(left_widget, 1) # Stretch factor 1
        
        # ----------------------
        # RIGHT PANEL (Control)
        # ----------------------
        right_widget = QWidget()
        right_widget.setFixedWidth(400) # Fixed width for consistent UI
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(15)
        
        # 1. Quick Actions Grid
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QVBoxLayout(actions_group)
        actions_layout.setSpacing(10)
        
        # Row 1
        row1 = QHBoxLayout()
        self.new_sale_btn = QPushButton("New Sale (F1)")
        self.new_sale_btn.setMinimumHeight(45)
        self.new_sale_btn.clicked.connect(self.start_new_sale)
        row1.addWidget(self.new_sale_btn)
        
        self.clear_btn = QPushButton("Clear Cart")
        self.clear_btn.setMinimumHeight(45)
        self.clear_btn.setStyleSheet("color: #CF6679; border-color: #CF6679;")
        self.clear_btn.clicked.connect(self.clear_cart)
        row1.addWidget(self.clear_btn)
        actions_layout.addLayout(row1)
        
        # Row 2
        row2 = QHBoxLayout()
        self.remove_btn = QPushButton("Remove Item (Del)")
        self.remove_btn.setMinimumHeight(45)
        self.remove_btn.clicked.connect(self.remove_selected_item)
        row2.addWidget(self.remove_btn)
        
        self.discount_btn = QPushButton("Discount") # Placeholder
        self.discount_btn.setMinimumHeight(45)
        self.discount_btn.setEnabled(False) 
        row2.addWidget(self.discount_btn)
        actions_layout.addLayout(row2)
        
        right_layout.addWidget(actions_group)
        
        right_layout.addStretch()
        
        # 2. Payment Deck (Total + Pay)
        pay_deck = QFrame()
        pay_deck.setObjectName("highlightFrame")
        pay_deck.setStyleSheet("""
            QFrame#highlightFrame {
                background-color: #16213E;
                border: 1px solid #2D3A5A;
                border-radius: 0px;
            }
        """)
        deck_layout = QVBoxLayout(pay_deck)
        deck_layout.setContentsMargins(20, 25, 20, 25)
        deck_layout.setSpacing(20)
        
        # Total Label
        total_info = QVBoxLayout()
        lbl = QLabel("TOTAL AMOUNT")
        lbl.setStyleSheet("color: #8899A6; font-size: 14px; letter-spacing: 1px;")
        lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        total_info.addWidget(lbl)
        
        self.display_total_label = QLabel("₱0.00")
        self.display_total_label.setObjectName("totalLabel")
        self.display_total_label.setStyleSheet("color: #FFFFFF; font-size: 42px; font-weight: bold;")
        self.display_total_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        total_info.addWidget(self.display_total_label)
        
        deck_layout.addLayout(total_info)
        
        # Divider
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("background-color: #2D3A5A; max-height: 1px;")
        deck_layout.addWidget(line)
        
        # Pay Button
        self.checkout_btn = QPushButton("PAY / CHECKOUT")
        self.checkout_btn.setObjectName("successButton")
        self.checkout_btn.setMinimumHeight(80)
        self.checkout_btn.setStyleSheet("""
            QPushButton#successButton {
                font-size: 24px;
                font-weight: bold;
                border-radius: 0px;
            }
        """)
        self.checkout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.checkout_btn.clicked.connect(self.process_checkout)
        deck_layout.addWidget(self.checkout_btn)
        
        shortcut_msg = QLabel("Press F12 to Checkout")
        shortcut_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        shortcut_msg.setStyleSheet("color: #03DAC6; margin-top: 5px;")
        deck_layout.addWidget(shortcut_msg)
        
        right_layout.addWidget(pay_deck)
        
        layout.addWidget(right_widget)
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # F1 - New Sale
        QShortcut(QKeySequence("F1"), self, self.start_new_sale)
        
        # F12 - Checkout
        QShortcut(QKeySequence("F12"), self, self.process_checkout)
        
        # Delete - Remove selected
        QShortcut(QKeySequence("Delete"), self, self.remove_selected_item)
        
        # Escape - Clear status
        QShortcut(QKeySequence("Escape"), self, self.clear_status)
    
    def start_new_sale(self):
        """Start a new sale session"""
        if sales_service.current_session and sales_service.current_session.cart:
            reply = QMessageBox.question(
                self, "Confirm",
                "Current cart is not empty. Start new sale?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        user = auth_service.get_current_user()
        cashier_name = user.username if user else None
        
        sales_service.start_new_sale(cashier_name)
        self.cart_table.clear_cart()
        if hasattr(self, 'display_total_label'):
            self.display_total_label.setText("₱0.00")
        self.show_status("New sale started", "success")
        self.barcode_input.focus_input()
    
    def on_barcode_scanned(self, barcode: str):
        """Handle barcode scan or product name search"""
        if not barcode:
            return
            
        # 1. Try adding by barcode (direct match)
        success, message, compliance_warning = sales_service.add_by_barcode(barcode)
        
        # 2. If valid barcode, handle it
        if success:
            self._handle_add_success(message, compliance_warning)
            return
            
        # 3. If not found, try searching by name
        # Only if the error suggests not found (or just always try search if simple add failed)
        products = inventory_service.search_products(barcode)
        
        if not products:
            self.show_status(f"Product not found: '{barcode}'", "error")
            self.barcode_input.focus_input()
            return
            
        # 4. Handle search results
        if len(products) == 1:
            # Single match - add it
            product = products[0]
            success, message, compliance_warning = sales_service.add_by_barcode(product.barcode)
            if success:
                self._handle_add_success(f"Added: {product.name}", compliance_warning)
            else:
                self.show_status(message, "error")
        else:
            # Multiple matches - use custom dialog
            dialog = ProductSelectionDialog(products, self)
            
            if dialog.exec():
                selected_product = dialog.get_selected_product()
                selected_quantity = dialog.get_selected_quantity()
                
                if selected_product:
                    success, message, compliance_warning = sales_service.add_by_barcode(
                        selected_product.barcode, 
                        quantity=selected_quantity
                    )
                    
                    if success:
                        self._handle_add_success(message, compliance_warning)
                    else:
                        self.show_status(message, "error")
        
        self.barcode_input.focus_input()
        
    def _handle_add_success(self, message, compliance_warning):
        """Helper to handle successful addition"""
        self.update_cart_display()
        
        if compliance_warning:
            if compliance_warning['severity'] == 'warning':
                # Get the product reference (it was just added to cart)
                session = sales_service.get_current_session()
                product_name = "Restricted Item"
                if session and session.cart:
                     product_name = session.cart[-1].product.name

                # Show custom prescription dialog (Premium UI)
                dialog = PrescriptionDialog(product_name, compliance_warning['message'], self)
                
                if dialog.exec() != QDialog.DialogCode.Accepted:
                    # Remove the item if cancelled
                    if session and session.cart:
                        last_item = session.cart[-1]
                        sales_service.remove_item(last_item.product.id)
                        self.update_cart_display()
                        self.show_status("Item removed - prescription not confirmed", "warning")
                        return
            else:
                self.show_status(compliance_warning['message'], 
                                'warning' if compliance_warning['type'] in ['low_stock', 'expiring_soon'] else 'info')
        else:
            self.show_status(message, "success")
    
    def on_quantity_changed(self, product_id: int, new_quantity: int):
        """Handle quantity change from cart"""
        if new_quantity < 1:
            self.on_item_removed(product_id)
        else:
            success, message = sales_service.update_quantity(product_id, new_quantity)
            if success:
                self.update_cart_display()
            else:
                self.show_status(message, "error")
        
        self.barcode_input.focus_input()
    
    def on_item_removed(self, product_id: int):
        """Handle item removal from cart"""
        success, message = sales_service.remove_item(product_id)
        if success:
            self.update_cart_display()
            self.show_status(message, "info")
        else:
            self.show_status(message, "error")
        
        self.barcode_input.focus_input()
    
    def remove_selected_item(self):
        """Remove the selected item from cart"""
        product_id = self.cart_table.get_selected_product_id()
        if product_id:
            self.on_item_removed(product_id)
        else:
            self.show_status("No item selected", "warning")
    
    def clear_cart(self):
        """Clear all items from cart"""
        if not sales_service.current_session or not sales_service.current_session.cart:
            self.show_status("Cart is already empty", "info")
            return
        
        reply = QMessageBox.question(
            self, "Confirm",
            "Clear all items from cart?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            sales_service.clear_cart()
            self.cart_table.clear_cart()
            if hasattr(self, 'display_total_label'):
                self.display_total_label.setText("₱0.00")
            self.show_status("Cart cleared", "info")
        
        self.barcode_input.focus_input()
    
    def process_checkout(self):
        """Process checkout and payment"""
        session = sales_service.get_current_session()
        
        if not session or not session.cart:
            self.show_status("Cart is empty", "error")
            return
        
        # Open payment dialog
        dialog = PaymentDialog(session.total, self)
        
        if dialog.exec():
            amount_tendered = dialog.get_amount_tendered()
            success, message, sale_id = sales_service.complete_sale(amount_tendered)
            
            if success:
                change = dialog.get_change()
                self.cart_table.clear_cart()
                self.show_status(
                    f"Sale #{sale_id} completed! Change: ₱{change:.2f}", 
                    "success"
                )
                
                # Show success dialog (Premium UI)
                # Note: session.cart still holds items because we grabbed the reference before completion
                success_dialog = SaleSuccessDialog(
                    sale_id, session.total, amount_tendered, change, session.cart, self
                )
                success_dialog.exec()
                
                self.start_new_sale()
            else:
                self.show_status(message, "error")
        
        self.barcode_input.focus_input()
    
    def update_cart_display(self):
        """Update the cart table with current session items"""
        session = sales_service.get_current_session()
        if session:
            self.cart_table.update_cart(session.cart)
            
            # Update total display
            if hasattr(self, 'display_total_label'):
                self.display_total_label.setText(f"₱{session.total:,.2f}")
    
    def show_status(self, message: str, status_type: str = "info"):
        """Show status message"""
        colors = {
            "success": ("#00BF6D", "#0D2818"),
            "error": ("#E94560", "#2D1A1A"),
            "warning": ("#FFB800", "#2D2818"),
            "info": ("#B0B0B0", "#1F2B47")
        }
        
        text_color, bg_color = colors.get(status_type, colors["info"])
        self.status_label.setStyleSheet(f"""
            background-color: {bg_color};
            color: {text_color};
            padding: 10px;
            border-radius: 0px;
            font-weight: bold;
        """)
        self.status_label.setText(message)
        
        # Auto-clear after 5 seconds for non-error messages
        if status_type != "error":
            QTimer.singleShot(5000, self.clear_status)
    
    def clear_status(self):
        """Clear status message"""
        self.status_label.setText("")
        self.status_label.setStyleSheet("")
    
    def showEvent(self, event):
        """Focus barcode input when screen becomes visible"""
        super().showEvent(event)
        QTimer.singleShot(100, self.barcode_input.focus_input)
