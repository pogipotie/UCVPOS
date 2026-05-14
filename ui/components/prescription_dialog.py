from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QFrame, QHBoxLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from ui.responsive_utils import apply_responsive_sizing

class PrescriptionDialog(QDialog):
    """
    Custom warning dialog for items requiring a prescription.
    Requires explicit confirmation from the cashier.
    """
    
    def __init__(self, product_name: str, message: str, parent=None):
        super().__init__(parent)
        self.product_name = product_name
        self.message = message
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Compliance Check")
        apply_responsive_sizing(self, 0.28, 0.45, 400, 350, 600, 600)
        self.setModal(True)
        self.setStyleSheet("background-color: #1A1A2E; color: white;")
        
        layout = QVBoxLayout(self)
        layout.setSpacing(25)
        layout.setContentsMargins(30, 40, 30, 40)
        
        # Icon Area
        icon_label = QLabel("⚠️")
        icon_label.setStyleSheet("font-size: 64px;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)
        
        # Title
        title = QLabel("PRESCRIPTION REQUIRED")
        title.setStyleSheet("color: #E94560; font-size: 24px; font-weight: bold; letter-spacing: 1px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Product & Message
        info_frame = QFrame()
        info_frame.setStyleSheet("background-color: #2D1A1A; border-radius: 8px; padding: 15px;")
        info_layout = QVBoxLayout(info_frame)
        
        prod_lbl = QLabel(self.product_name)
        prod_lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
        prod_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(prod_lbl)
        
        msg_lbl = QLabel(self.message)
        msg_lbl.setStyleSheet("font-size: 14px; color: #FFB800; margin-top: 5px;")
        msg_lbl.setWordWrap(True)
        msg_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(msg_lbl)
        
        layout.addWidget(info_frame)
        
        layout.addStretch()
        
        # Actions
        actions = QVBoxLayout()
        actions.setSpacing(10)
        
        self.confirm_btn = QPushButton("CONFIRM PRESCRIPTION (Enter)")
        self.confirm_btn.setMinimumHeight(55)
        self.confirm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.confirm_btn.clicked.connect(self.accept)
        self.confirm_btn.setStyleSheet("""
            QPushButton {
                background-color: #E94560; 
                color: white; 
                border-radius: 8px; 
                font-size: 16px; 
                font-weight: bold;
            }
            QPushButton:hover { background-color: #FF5D7A; }
            QPushButton:pressed { background-color: #C0354A; }
        """)
        
        self.cancel_btn = QPushButton("Cancel / Remove Item (Esc)")
        self.cancel_btn.setMinimumHeight(45)
        self.cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent; 
                color: #B0B0B0; 
                border: 1px solid #4D4D4D;
                border-radius: 8px; 
                font-size: 14px;
            }
            QPushButton:hover { background-color: #2D3A5A; color: white; border-color: #2D3A5A; }
        """)
        
        actions.addWidget(self.confirm_btn)
        actions.addWidget(self.cancel_btn)
        layout.addLayout(actions)
        
        self.confirm_btn.setDefault(True)
        self.confirm_btn.setFocus()
