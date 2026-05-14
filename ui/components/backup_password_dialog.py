"""
Backup Password Dialog - Verify admin password before backup
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QLineEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import os

from services.auth_service import auth_service
from ui.responsive_utils import apply_responsive_sizing


class BackupPasswordDialog(QDialog):
    """Custom styled dialog for backup password verification"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.verified = False
        self.backup_password = ""
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Backup Authentication")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        apply_responsive_sizing(self, 0.27, 0.42, 350, 300, 550, 550)
        
        # Main Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Container Card
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
        
        # Secure Backup Icon
        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_path = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "Securebackup.png")
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path).scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            icon_label.setPixmap(pixmap)
        else:
            icon_label.setText("🔒")
            icon_label.setStyleSheet("font-size: 50px; border: none; background: transparent;")
        container_layout.addWidget(icon_label)
        
        # Title
        title = QLabel("Secure Backup")
        title.setStyleSheet("""
            color: #03DAC6; 
            font-size: 22px; 
            font-weight: bold; 
            border: none; 
            background: transparent;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(title)
        
        # Info message
        info = QLabel("Enter your admin password to create a\npassword-protected backup.")
        info.setStyleSheet("color: #888; font-size: 12px; border: none; background: transparent;")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(info)
        
        # Admin Password Input
        admin_label = QLabel("Admin Password:")
        admin_label.setStyleSheet("color: #B0B0B0; font-size: 13px; border: none; background: transparent;")
        container_layout.addWidget(admin_label)
        
        self.admin_password_input = QLineEdit()
        self.admin_password_input.setPlaceholderText("Enter your admin password")
        self.admin_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.admin_password_input.setStyleSheet("""
            QLineEdit {
                background-color: #252540;
                border: 1px solid #444;
                border-radius: 0px;
                color: white;
                padding: 10px 12px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #03DAC6;
            }
        """)
        container_layout.addWidget(self.admin_password_input)
        
        # Backup Password Input
        backup_label = QLabel("Backup ZIP Password:")
        backup_label.setStyleSheet("color: #B0B0B0; font-size: 13px; border: none; background: transparent;")
        container_layout.addWidget(backup_label)
        
        self.backup_password_input = QLineEdit()
        self.backup_password_input.setPlaceholderText("Password to protect the backup file")
        self.backup_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.backup_password_input.setStyleSheet("""
            QLineEdit {
                background-color: #252540;
                border: 1px solid #444;
                border-radius: 0px;
                color: white;
                padding: 10px 12px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #03DAC6;
            }
        """)
        container_layout.addWidget(self.backup_password_input)
        
        # Error label (hidden by default)
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #CF6679; font-size: 12px; border: none; background: transparent;")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.hide()
        container_layout.addWidget(self.error_label)
        
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
        
        # Create Backup Button
        backup_btn = QPushButton("Create Backup")
        backup_btn.setMinimumHeight(42)
        backup_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        backup_btn.setStyleSheet("""
            QPushButton {
                background-color: #03DAC6;
                color: #1A1A2E;
                border: none;
                border-radius: 0px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #00EDD4; }
            QPushButton:pressed { background-color: #00C4B4; }
        """)
        backup_btn.clicked.connect(self.verify_and_proceed)
        btn_layout.addWidget(backup_btn)
        
        container_layout.addLayout(btn_layout)
        layout.addWidget(container)
        
        # Focus on input
        self.admin_password_input.setFocus()
        
    def verify_and_proceed(self):
        """Verify admin password and proceed with backup"""
        admin_pass = self.admin_password_input.text()
        backup_pass = self.backup_password_input.text().strip()
        
        # Validate inputs
        if not admin_pass:
            self.show_error("Please enter your admin password")
            return
        
        if not backup_pass or len(backup_pass) < 4:
            self.show_error("Backup password must be at least 4 characters")
            return
        
        # Verify admin password
        user = auth_service.get_current_user()
        if not user:
            self.show_error("No user logged in")
            return
        
        # Check password
        if not auth_service.verify_password(user.username, admin_pass):
            self.show_error("Incorrect admin password")
            self.admin_password_input.clear()
            self.admin_password_input.setFocus()
            return
        
        # Success
        self.verified = True
        self.backup_password = backup_pass
        self.accept()
    
    def show_error(self, message: str):
        """Show error message"""
        self.error_label.setText(f"⚠️ {message}")
        self.error_label.show()
    
    def get_backup_password(self) -> str:
        """Get the backup password"""
        return self.backup_password
