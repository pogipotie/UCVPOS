from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QFrame, QHBoxLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import os
from ui.responsive_utils import apply_responsive_sizing

class ActionConfirmDialog(QDialog):
    """Custom confirmation dialog (e.g. for delete) with premium UI"""
    
    def __init__(self, title: str, message: str, parent=None, icon_path: str = None, confirm_text: str = "Confirm", is_danger: bool = False):
        super().__init__(parent)
        self.title_text = title
        self.message_text = message
        self.icon_path = icon_path
        self.confirm_text = confirm_text
        self.is_danger = is_danger
        self.result_confirmed = False
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Confirm Action")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Overlay/Background
        apply_responsive_sizing(self, 0.28, 0.40, 350, 300, 550, 500)
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
        
        # Fallback icon path (e.g. warning.png or trash.png if you had them)
        # For now, we use a text emoji fallback if icon_path is None or invalid
        if self.icon_path and os.path.exists(self.icon_path):
            pixmap = QPixmap(self.icon_path).scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            icon_label.setPixmap(pixmap)
        else:
            # Fallback to emoji
            icon_label.setText("⚠️" if not self.is_danger else "🗑️")
            icon_label.setStyleSheet("font-size: 50px; border: none; background: transparent;")
            
        container_layout.addWidget(icon_label)
        
        # Title
        title_lbl = QLabel(self.title_text)
        color = "#FF4757" if self.is_danger else "#FFB800" # Red for danger, Orange for warning
        title_lbl.setStyleSheet(f"color: {color}; font-size: 22px; font-weight: bold; border: none; background: transparent;")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(title_lbl)
        
        # Message
        msg_lbl = QLabel(self.message_text)
        msg_lbl.setWordWrap(True)
        msg_lbl.setStyleSheet("color: #B0B0B0; font-size: 14px; border: none; background: transparent;")
        msg_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(msg_lbl)
        
        container_layout.addStretch()
        
        # Buttons Row
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        # Cancel Button
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setMinimumHeight(45)
        self.cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #444;
                color: #B0B0B0;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover { background-color: #333; color: white; }
        """)
        btn_layout.addWidget(self.cancel_btn)
        
        # Confirm Button
        self.confirm_btn = QPushButton(self.confirm_text)
        self.confirm_btn.setMinimumHeight(45)
        self.confirm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.confirm_btn.clicked.connect(self.confirm_action)
        
        if self.is_danger:
            self.confirm_btn.setStyleSheet("""
                QPushButton {
                    background-color: #FF4757;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #FF6B81; }
                QPushButton:pressed { background-color: #E03B4B; }
            """)
        else:
             self.confirm_btn.setStyleSheet("""
                QPushButton {
                    background-color: #FFB800;
                    color: black;
                    border: none;
                    border-radius: 6px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #FFC933; }
            """)
            
        btn_layout.addWidget(self.confirm_btn)
        
        container_layout.addLayout(btn_layout)
        
        layout.addWidget(self.container)
        
        # Default focus on confirm for quick action (Enter key)
        self.confirm_btn.setDefault(True)
        self.confirm_btn.setFocus()
        
    def confirm_action(self):
        self.result_confirmed = True
        self.accept()
