"""
Void Sale Dialog - Premium styled dialog for voiding sales
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QLineEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import os


class VoidSaleDialog(QDialog):
    """Custom styled void sale confirmation dialog with reason input"""
    
    def __init__(self, sale, parent=None):
        super().__init__(parent)
        self.sale = sale
        self.reason = ""
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Void Sale")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self.resize(420, 380)
        
        # Main Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Container Card - NO border-radius
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #1A1A2E;
                border: 1px solid #2D3A5A;
                border-radius: 0px;
            }
        """)
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(15)
        container_layout.setContentsMargins(30, 35, 30, 35)
        
        # Warning Icon from assets
        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_path = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "warning.png")
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path).scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            icon_label.setPixmap(pixmap)
        else:
            icon_label.setText("⚠️")
            icon_label.setStyleSheet("font-size: 50px; border: none; background: transparent;")
        container_layout.addWidget(icon_label)
        
        # Title
        title = QLabel("Void Sale")
        title.setStyleSheet("""
            color: #CF6679; 
            font-size: 22px; 
            font-weight: bold; 
            border: none; 
            background: transparent;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(title)
        
        # Sale Details Card
        details_frame = QFrame()
        details_frame.setStyleSheet("""
            QFrame {
                background-color: #252540;
                border: 1px solid #333355;
                border-radius: 0px;
                padding: 10px;
            }
        """)
        details_layout = QVBoxLayout(details_frame)
        details_layout.setContentsMargins(15, 12, 15, 12)
        details_layout.setSpacing(8)
        
        # Sale ID
        id_label = QLabel(f"Sale ID: #{self.sale.id}")
        id_label.setStyleSheet("color: #888; font-size: 12px; border: none; background: transparent;")
        details_layout.addWidget(id_label)
        
        # Amount
        amount_label = QLabel(f"Amount: ₱{self.sale.total_amount:,.2f}")
        amount_label.setStyleSheet("color: #03DAC6; font-size: 16px; font-weight: bold; border: none; background: transparent;")
        details_layout.addWidget(amount_label)
        
        # Date
        date_label = QLabel(f"Date: {self.sale.sale_date}")
        date_label.setStyleSheet("color: #888; font-size: 12px; border: none; background: transparent;")
        details_layout.addWidget(date_label)
        
        container_layout.addWidget(details_frame)
        
        # Warning message
        warning = QLabel("This will restore all items to inventory.")
        warning.setStyleSheet("color: #FFB800; font-size: 12px; border: none; background: transparent;")
        warning.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(warning)
        
        # Reason Input
        reason_label = QLabel("Reason for voiding:")
        reason_label.setStyleSheet("color: #B0B0B0; font-size: 13px; border: none; background: transparent;")
        container_layout.addWidget(reason_label)
        
        self.reason_input = QLineEdit()
        self.reason_input.setPlaceholderText("Enter reason (required)")
        self.reason_input.setStyleSheet("""
            QLineEdit {
                background-color: #252540;
                border: 1px solid #444;
                border-radius: 0px;
                color: white;
                padding: 10px 12px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #CF6679;
            }
        """)
        container_layout.addWidget(self.reason_input)
        
        container_layout.addStretch()
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        # Cancel Button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumHeight(42)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #444;
                color: #B0B0B0;
                border-radius: 0px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover { background-color: #333; color: white; }
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        # Void Button
        void_btn = QPushButton("Void Sale")
        void_btn.setMinimumHeight(42)
        void_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        void_btn.setStyleSheet("""
            QPushButton {
                background-color: #CF6679;
                color: white;
                border: none;
                border-radius: 0px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #E57388; }
            QPushButton:pressed { background-color: #B85566; }
        """)
        void_btn.clicked.connect(self.confirm_void)
        btn_layout.addWidget(void_btn)
        
        container_layout.addLayout(btn_layout)
        layout.addWidget(container)
        
        # Focus on input
        self.reason_input.setFocus()
        
    def confirm_void(self):
        """Validate and confirm the void action"""
        reason = self.reason_input.text().strip()
        if not reason:
            self.reason_input.setStyleSheet("""
                QLineEdit {
                    background-color: #252540;
                    border: 1px solid #CF6679;
                    border-radius: 0px;
                    color: white;
                    padding: 10px 12px;
                    font-size: 13px;
                }
            """)
            self.reason_input.setPlaceholderText("⚠️ Reason is required!")
            return
        
        self.reason = reason
        self.accept()
    
    def get_reason(self) -> str:
        """Get the entered reason"""
        return self.reason
