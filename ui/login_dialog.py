from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, 
    QMessageBox, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from services.auth_service import auth_service
from ui.responsive_utils import apply_responsive_sizing

class LoginDialog(QDialog):
    """Secure Login Screen"""
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.user = None
        self.setup_ui()
        
    def setup_ui(self):
        apply_responsive_sizing(self, 0.25, 0.55, 350, 400, 500, 700)
        
        # Main layout container with rounded corners/background
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        container = QLabel() # Using label as container for styling
        container.setObjectName("loginContainer")
        container.setStyleSheet("""
            QWidget#loginContainer {
                background-color: #1A1A2E;
                border: 1px solid #0D7377;
                border-radius: 0px;
            }
        """)
        # Drop shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 5)
        container.setGraphicsEffect(shadow)
        
        inner_layout = QVBoxLayout(container)
        inner_layout.setSpacing(20)
        inner_layout.setContentsMargins(40, 50, 40, 40)
        
        # Logo/Title
        title = QLabel("DoubleA POS")
        title.setStyleSheet("""
            font-family: 'Segoe UI'; 
            font-size: 32px; 
            font-weight: bold; 
            color: #FFFFFF;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        inner_layout.addWidget(title)
        
        subtitle = QLabel("Secure Login")
        subtitle.setStyleSheet("font-size: 16px; color: #0D7377; letter-spacing: 2px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        inner_layout.addWidget(subtitle)
        
        inner_layout.addSpacing(20)
        
        # Inputs
        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        self.username.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border-radius: 0px;
                background-color: #16213E;
                color: #FFFFFF;
                border: 1px solid #2C2C2C;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #0D7377;
            }
        """)
        inner_layout.addWidget(self.username)
        
        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border-radius: 0px;
                background-color: #16213E;
                color: #FFFFFF;
                border: 1px solid #2C2C2C;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #0D7377;
            }
        """)
        self.password.returnPressed.connect(self.handle_login)
        inner_layout.addWidget(self.password)
        
        inner_layout.addSpacing(20)
        
        # Login Button
        login_btn = QPushButton("LOGIN")
        login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        login_btn.clicked.connect(self.handle_login)
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #0D7377;
                color: white;
                font-weight: bold;
                padding: 12px;
                border-radius: 0px;
                font-size: 14px;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background-color: #0F888D;
            }
            QPushButton:pressed {
                background-color: #09595D;
            }
        """)
        inner_layout.addWidget(login_btn)
        
        # Cancel/Ext
        cancel_btn = QPushButton("Exit Application")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #666666;
                font-size: 12px;
                border: none;
            }
            QPushButton:hover {
                color: #999999;
                text-decoration: underline;
            }
        """)
        inner_layout.addWidget(cancel_btn)
        inner_layout.addStretch()
        
        layout.addWidget(container)
        
    def handle_login(self):
        username = self.username.text().strip()
        password = self.password.text().strip()
        
        if not username or not password:
            self.shake_window()
            return
            
        user = auth_service.login(username, password)
        if user:
            self.user = user
            self.accept()
        else:
            self.password.clear()
            self.password.setPlaceholderText("Invalid Credentials")
            self.password.setStyleSheet(self.password.styleSheet().replace("#2C2C2C", "#E94560"))
            self.shake_window()
    
    def shake_window(self):
        # Simple animation placeholder
        pass
