"""
Payment Dialog - Cash payment processing with change calculation
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class PaymentDialog(QDialog):
    """Dialog for processing cash payment"""
    
    def __init__(self, total_amount: float, parent=None, discount_type: str = None, discount_amount: float = 0.0, original_total: float = None):
        super().__init__(parent)
        self.total_amount = total_amount  # This is final_total if discounted
        self.discount_type = discount_type
        self.discount_amount = discount_amount
        self.original_total = original_total or total_amount
        self.amount_tendered = 0.0
        self.setup_ui()

    
    def setup_ui(self):
        self.setWindowTitle("Process Payment")
        # Responsive sizing
        screen = self.screen().availableGeometry()
        width = int(screen.width() * 0.40)
        height = int(screen.height() * 0.85)
        
        # Constraints
        width = max(450, min(width, 600))  # Max width 600px
        height = max(700, min(height, 900)) # Max height 900px
        
        self.resize(width, height)
        self.setMinimumSize(450, 700)
        self.setModal(True)
        self.setStyleSheet("background-color: #1A1A2E; color: white;")
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Total display frame
        total_frame = QFrame()
        
        # Style based on discount type
        if self.discount_type:
            total_frame.setStyleSheet("""
                QFrame {
                    background-color: #1F2B47;
                    border: 2px solid #FFB800;
                    border-radius: 0px;
                    padding: 10px;
                }
            """)
        else:
            total_frame.setStyleSheet("""
                QFrame {
                    background-color: #1F2B47;
                    border: 2px solid #0D7377;
                    border-radius: 0px;
                    padding: 10px;
                }
            """)
        
        total_layout = QVBoxLayout(total_frame)
        total_layout.setSpacing(5)
        
        if self.discount_type:
            # SC/PWD Discount Header
            discount_header = QLabel(f"{'SENIOR CITIZEN' if self.discount_type == 'SC' else 'PWD'} DISCOUNT")
            discount_header.setStyleSheet("color: #FFB800; font-size: 14px; font-weight: bold; letter-spacing: 1px;")
            discount_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
            total_layout.addWidget(discount_header)
            
            # Original Price
            orig_row = QHBoxLayout()
            orig_label = QLabel("Original Price:")
            orig_label.setStyleSheet("color: #888888; font-size: 14px;")
            orig_row.addWidget(orig_label)
            orig_row.addStretch()
            orig_value = QLabel(f"₱{self.original_total:,.2f}")
            orig_value.setStyleSheet("color: #888888; font-size: 14px; text-decoration: line-through;")
            orig_row.addWidget(orig_value)
            total_layout.addLayout(orig_row)
            
            # VAT Exempt
            vat_exempt = self.original_total / 1.12
            vat_row = QHBoxLayout()
            vat_label = QLabel("VAT Exempt:")
            vat_label.setStyleSheet("color: #CCCCCC; font-size: 14px;")
            vat_row.addWidget(vat_label)
            vat_row.addStretch()
            vat_value = QLabel(f"₱{vat_exempt:,.2f}")
            vat_value.setStyleSheet("color: #FFFFFF; font-size: 14px;")
            vat_row.addWidget(vat_value)
            total_layout.addLayout(vat_row)
            
            # 20% Discount
            disc_row = QHBoxLayout()
            disc_label = QLabel("Less 20% Discount:")
            disc_label.setStyleSheet("color: #FFB800; font-size: 14px;")
            disc_row.addWidget(disc_label)
            disc_row.addStretch()
            disc_value = QLabel(f"-₱{self.discount_amount:,.2f}")
            disc_value.setStyleSheet("color: #FFB800; font-size: 14px; font-weight: bold;")
            disc_row.addWidget(disc_value)
            total_layout.addLayout(disc_row)
        else:
            # Normal VAT breakdown
            from services.settings_service import settings_service
            tax_rate = settings_service.get('financial', 'tax_rate') or 12.0
            vat_amount = self.total_amount - (self.total_amount / (1 + tax_rate / 100)) if tax_rate > 0 else 0
            net_amount = self.total_amount - vat_amount
            
            net_row = QHBoxLayout()
            net_label = QLabel("Net Amount:")
            net_label.setStyleSheet("color: #CCCCCC; font-size: 16px;")
            net_row.addWidget(net_label)
            net_row.addStretch()
            net_value = QLabel(f"₱{net_amount:,.2f}")
            net_value.setStyleSheet("color: #FFFFFF; font-size: 16px; font-weight: bold;")
            net_row.addWidget(net_value)
            total_layout.addLayout(net_row)
            
            vat_row = QHBoxLayout()
            vat_label = QLabel(f"VAT ({tax_rate:.0f}%):")
            vat_label.setStyleSheet("color: #CCCCCC; font-size: 16px;")
            vat_row.addWidget(vat_label)
            vat_row.addStretch()
            vat_value = QLabel(f"₱{vat_amount:,.2f}")
            vat_value.setStyleSheet("color: #FFFFFF; font-size: 16px; font-weight: bold;")
            vat_row.addWidget(vat_value)
            total_layout.addLayout(vat_row)
        
        # Divider
        div = QFrame()
        div.setFrameShape(QFrame.Shape.HLine)
        div.setStyleSheet("background-color: #2D3A5A; max-height: 1px;")
        total_layout.addWidget(div)
        
        # Total
        total_label = QLabel("AMOUNT TO PAY")
        total_label.setStyleSheet("color: #B0B0B0; font-size: 14px; font-weight: bold; letter-spacing: 1px;")
        total_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        total_layout.addWidget(total_label)
        
        self.total_display = QLabel(f"₱{self.total_amount:,.2f}")
        self.total_display.setStyleSheet("color: #00BF6D; font-size: 42px; font-weight: bold;")
        self.total_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.total_display.setMinimumHeight(60)
        total_layout.addWidget(self.total_display)
        
        layout.addWidget(total_frame)
        
        # Amount tendered input
        input_container = QVBoxLayout()
        input_container.setSpacing(5)
        
        amount_label = QLabel("CASH RECEIVED")
        amount_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #B0B0B0; letter-spacing: 0.5px;")
        input_container.addWidget(amount_label)
        
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("0.00")
        self.amount_input.setMinimumHeight(50)
        self.amount_input.setStyleSheet("""
            QLineEdit {
                background-color: #16213E;
                color: #FFFFFF;
                border: 2px solid #2D3A5A;
                border-radius: 0px;
                font-size: 32px;
                padding: 5px 15px;
                font-weight: bold;
            }
            QLineEdit:focus {
                border: 2px solid #03DAC6;
                background-color: #1F2B47;
            }
        """)
        self.amount_input.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.amount_input.textChanged.connect(self.calculate_change)
        self.amount_input.returnPressed.connect(self.handle_enter_press)
        input_container.addWidget(self.amount_input)
        
        layout.addLayout(input_container)
        
        # Quick amount buttons
        quick_layout = QGridLayout()

        quick_layout.setSpacing(8)
        
        # ... existing logic for amounts ...
        next_50 = round(self.total_amount / 50) * 50 + 50
        if self.total_amount % 50 == 0: next_50 = self.total_amount 
        
        next_100 = round(self.total_amount / 100) * 100 + 100
        if self.total_amount % 100 == 0: next_100 = self.total_amount
        
        button_data = [
            ("EXACT", self.total_amount),
            (f"₱{next_50:.0f}", next_50),
            (f"₱{next_100:.0f}", next_100),
            ("₱100", 100),
            ("₱200", 200),
            ("₱500", 500),
            ("₱1,000", 1000),
            ("₱2,000", 2000),
        ]
        
        row, col = 0, 0
        for text, amount in button_data:
            btn = QPushButton(text)
            btn.setMinimumHeight(50)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2D3A5A;
                    color: white;
                    border: 1px solid #3D4A6A;
                    border-radius: 0px;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #3D4A6A;
                    border-color: #4D5A7A;
                    margin-top: -2px;
                }
                QPushButton:pressed {
                    background-color: #1F2B47;
                    margin-top: 0px;
                }
            """)
            btn.clicked.connect(lambda checked, a=amount: self.set_amount(a))
            quick_layout.addWidget(btn, row, col)
            col += 1
            if col > 3:
                col = 0
                row += 1
        
        layout.addLayout(quick_layout)
        
        # Change display
        change_frame = QFrame()
        change_frame.setStyleSheet("""
            QFrame {
                background-color: #16213E;
                border: 2px solid #2D3A5A;
                border-radius: 0px;
                padding: 10px;
            }
        """)
        change_layout = QVBoxLayout(change_frame)
        
        change_label = QLabel("CHANGE DUE")
        change_label.setStyleSheet("color: #B0B0B0; font-size: 12px; font-weight: bold; letter-spacing: 0.5px;")
        change_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        change_layout.addWidget(change_label)
        
        self.change_display = QLabel("₱0.00")
        self.change_display.setStyleSheet("color: #FFB800; font-size: 32px; font-weight: bold;")
        self.change_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        change_layout.addWidget(self.change_display)
        
        layout.addWidget(change_frame)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        cancel_btn = QPushButton("CANCEL (Esc)")
        cancel_btn.setMinimumHeight(55)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 2px solid #CF6679;
                color: #CF6679;
                border-radius: 0px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(207, 102, 121, 0.1);
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        self.confirm_btn = QPushButton("CONFIRM PAYMENT (Enter)")
        self.confirm_btn.setMinimumHeight(65)
        self.confirm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.confirm_btn.setEnabled(False)
        self.confirm_btn.clicked.connect(self.confirm_payment)
        # Style set dynamically but set base here
        self.confirm_btn.setStyleSheet("""
            QPushButton {
                background-color: #03DAC6;
                color: #000000;
                border: none;
                border-radius: 0px;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #05E5D0; }
            QPushButton:disabled { background-color: #333333; color: #555555; }
        """)
        button_layout.addWidget(self.confirm_btn, 2) # 2x stretch
        
        layout.addLayout(button_layout)
        
        # Focus on amount input
        self.amount_input.setFocus()
    
    def set_amount(self, amount: float):
        """Set amount from quick button"""
        self.amount_input.setText(f"{amount:.2f}")
    
    def calculate_change(self):
        """Calculate and display change"""
        try:
            text = self.amount_input.text().replace(",", "").replace("₱", "")
            if text:
                amount = float(text)
                change = amount - self.total_amount
                
                if round(change, 2) >= 0:
                    self.change_display.setText(f"₱{change:,.2f}")
                    self.change_display.setStyleSheet("color: #00BF6D; font-size: 32px; font-weight: bold;")
                    self.confirm_btn.setEnabled(True)
                    self.confirm_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #03DAC6;
                            color: #000000;
                            border: none;
                            border-radius: 0px;
                            font-size: 20px;
                            font-weight: bold;
                        }
                        QPushButton:hover { background-color: #05E5D0; }
                    """)
                    self.amount_tendered = amount
                else:
                    self.change_display.setText(f"-₱{abs(change):,.2f}")
                    self.change_display.setStyleSheet("color: #E94560; font-size: 32px; font-weight: bold;")
                    self.confirm_btn.setEnabled(False)
                    self.confirm_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #333333;
                            color: #555555;
                            border: none;
                            border-radius: 0px;
                            font-size: 20px;
                            font-weight: bold;
                        }
                    """)
            else:
                self.change_display.setText("₱0.00")
                self.change_display.setStyleSheet("color: #FFB800; font-size: 32px; font-weight: bold;")
                self.confirm_btn.setEnabled(False)
                self.confirm_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #333333;
                        color: #555555;
                        border: none;
                        border-radius: 0px;
                        font-size: 20px;
                        font-weight: bold;
                    }
                """)
        except ValueError:
            self.change_display.setText("Invalid")
            self.change_display.setStyleSheet("color: #E94560; font-size: 32px; font-weight: bold;")
            self.confirm_btn.setEnabled(False)
    
    def handle_enter_press(self):
        """Handle enter key in input"""
        if self.confirm_btn.isEnabled():
            self.confirm_payment()

    def confirm_payment(self):
        """Confirm the payment"""
        self.accept()
    
    def get_amount_tendered(self) -> float:
        """Get the amount tendered"""
        return self.amount_tendered
    
    def get_change(self) -> float:
        """Get the change amount"""
        return self.amount_tendered - self.total_amount
