from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QColor, QFont, QPixmap
import os

class CustomSuccessDialog(QDialog):
    """A premium styled success dialog"""
    def __init__(self, parent=None, title="Success", message="Operation completed successfully"):
        super().__init__(parent)
        self.title_text = title
        self.message_text = message
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(350, 250)
        self.setup_ui()

    def setup_ui(self):
        # Main Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Container Frame (Dark & Sharp)
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
        container_layout.setContentsMargins(30, 30, 30, 30)
        container_layout.setSpacing(20)

        # Icon - Use check.png
        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_path = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "check.png")
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path).scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            icon_label.setPixmap(pixmap)
        else:
            icon_label.setText("✅")
            icon_label.setStyleSheet("font-size: 48px; border: none;")
        container_layout.addWidget(icon_label)

        # Title
        title_label = QLabel(self.title_text)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            color: #03DAC6;
            font-size: 20px;
            font-weight: bold;
            border: none;
        """)
        container_layout.addWidget(title_label)
        
        # Message
        msg_label = QLabel(self.message_text)
        msg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet("""
            color: #B3B3B3;
            font-size: 14px;
            border: none;
        """)
        container_layout.addWidget(msg_label)
        
        container_layout.addStretch()

        # OK Button
        self.btn_ok = QPushButton("OK")
        self.btn_ok.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_ok.setFixedSize(140, 40)
        self.btn_ok.setStyleSheet("""
            QPushButton {
                background-color: #03DAC6;
                border: none;
                border-radius: 0px;
                color: #000000;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #018786;
            }
            QPushButton:pressed {
                background-color: #016E6D;
            }
        """)
        self.btn_ok.clicked.connect(self.accept)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_ok)
        btn_layout.addStretch()
        container_layout.addLayout(btn_layout)
        
        layout.addWidget(self.container)
