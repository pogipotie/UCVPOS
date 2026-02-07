from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QFrame, QHBoxLayout
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor, QPixmap
import os

class ActionSuccessDialog(QDialog):
    """Custom dialog for generic success actions with premium UI"""
    
    def __init__(self, title: str, message: str, parent=None, icon_path: str = None):
        super().__init__(parent)
        self.title_text = title
        self.message_text = message
        self.icon_path = icon_path
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Success")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Overlay/Background
        self.resize(400, 350)
        self.setModal(True)
        
        # Main Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Container Card
        self.container = QFrame()
        self.container.setStyleSheet("""
            QFrame {
                background-color: #1A1A2E;
                border: 1px solid #2D3A5A;
                border-radius: 12px;
            }
        """)
        container_layout = QVBoxLayout(self.container)
        container_layout.setSpacing(15)
        container_layout.setContentsMargins(30, 40, 30, 40)
        
        # Icon
        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        if not self.icon_path:
             self.icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "check.png")
             
        if os.path.exists(self.icon_path):
            pixmap = QPixmap(self.icon_path).scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            icon_label.setPixmap(pixmap)
        else:
            # Fallback to emoji if image missing
            icon_label.setText("✅")
            icon_label.setStyleSheet("font-size: 50px; border: none; background: transparent;")
            
        container_layout.addWidget(icon_label)
        
        # Title
        title_lbl = QLabel(self.title_text)
        title_lbl.setStyleSheet("color: #00BF6D; font-size: 22px; font-weight: bold; border: none; background: transparent;")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(title_lbl)
        
        # Message
        msg_lbl = QLabel(self.message_text)
        msg_lbl.setWordWrap(True)
        msg_lbl.setStyleSheet("color: #B0B0B0; font-size: 14px; border: none; background: transparent;")
        msg_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(msg_lbl)
        
        container_layout.addStretch()
        
        # Button
        self.ok_btn = QPushButton("OK (Enter)")
        self.ok_btn.setMinimumHeight(45)
        self.ok_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.ok_btn.clicked.connect(self.accept)
        self.ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #00BF6D;
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #00D67A; }
            QPushButton:pressed { background-color: #00A860; }
        """)
        container_layout.addWidget(self.ok_btn)
        
        layout.addWidget(self.container)
        
        # Auto focus
        self.ok_btn.setFocus()
