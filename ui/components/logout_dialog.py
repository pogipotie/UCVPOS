from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor, QFont
from ui.responsive_utils import apply_responsive_sizing

class LogoutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        apply_responsive_sizing(self, 0.22, 0.25, 300, 180, 400, 300)
        self.setup_ui()

    def setup_ui(self):
        # Main Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Container Frame (Rounded & Dark)
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

        # Icon / Title
        # Using a large styled label for visual impact
        title_label = QLabel("Confirm Logout")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            color: #FFFFFF;
            font-size: 20px;
            font-weight: bold;
            border: none;
        """)
        container_layout.addWidget(title_label)
        
        # Message
        msg_label = QLabel("Are you sure you want to end your session?")
        msg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet("""
            color: #B3B3B3;
            font-size: 14px;
            border: none;
        """)
        container_layout.addWidget(msg_label)
        
        container_layout.addStretch()

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        # Cancel Button
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancel.setFixedSize(110, 40)
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #333333;
                border-radius: 0px;
                color: #B3B3B3;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #2C2C2C;
                color: #FFFFFF;
                border-color: #444444;
            }
        """)
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)

        # Logout Button
        self.btn_logout = QPushButton("Logout")
        self.btn_logout.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_logout.setFixedSize(110, 40)
        self.btn_logout.setStyleSheet("""
            QPushButton {
                background-color: #CF6679;
                border: none;
                border-radius: 0px;
                color: #121212;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #E0778A;
            }
            QPushButton:pressed {
                background-color: #B04659;
            }
        """)
        self.btn_logout.clicked.connect(self.accept)
        btn_layout.addWidget(self.btn_logout)

        container_layout.addLayout(btn_layout)
        
        layout.addWidget(self.container)
