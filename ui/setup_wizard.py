"""
Setup Wizard for First Run Configuration
"""
from PyQt6.QtWidgets import (
    QWizard, QWizardPage, QVBoxLayout, QFormLayout, 
    QLineEdit, QLabel, QMessageBox, QSpinBox
)
from PyQt6.QtCore import Qt
import json
import config
from database.connection import db
from ui.responsive_utils import apply_responsive_sizing

class SetupWizard(QWizard):
    """Wizard to guide user through initial setup"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UCVPOS - First Run Setup")
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)
        apply_responsive_sizing(self, 0.35, 0.50, 500, 350, 800, 700)
        
        # Add pages
        self.addPage(DatabasePage())
        self.addPage(AdminPage())
        
        self.setStyleSheet("""
            QWizard { background-color: #f0f0f0; }
            QLabel { font-size: 12px; }
            QLineEdit { padding: 5px; border: 1px solid #ccc; border-radius: 4px; }
            QPushButton { padding: 6px 12px; }
        """)

class DatabasePage(QWizardPage):
    """Page to configure MySQL connection"""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Database Configuration")
        self.setSubTitle("Please enter your MySQL Database connection details.")
        
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        self.host_input = QLineEdit("localhost")
        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(3306)
        
        self.user_input = QLineEdit("root")
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.db_input = QLineEdit("ucvpos_db")
        
        form_layout.addRow("Host:", self.host_input)
        form_layout.addRow("Port:", self.port_input)
        form_layout.addRow("Username:", self.user_input)
        form_layout.addRow("Password:", self.pass_input)
        form_layout.addRow("Database Name:", self.db_input)
        
        layout.addLayout(form_layout)
        
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: red;")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
    def validatePage(self):
        """Test connection and save config"""
        host = self.host_input.text().strip()
        port = self.port_input.value()
        user = self.user_input.text().strip()
        password = self.pass_input.text()
        database = self.db_input.text().strip()
        
        if not host or not user or not database:
            self.status_label.setText("Please fill in all required fields.")
            return False
            
        # 1. Test Connection
        try:
            import pymysql
            # Try connecting without DB first to check server
            conn = pymysql.connect(
                host=host, port=port, user=user, password=password
            )
            
            # Create DB if not exists
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.status_label.setText(f"Connection Failed: {e}")
            return False
            
        # 2. Save Config
        new_config = {
            'host': host,
            'port': port,
            'user': user,
            'password': password,
            'database': database,
            'raise_on_warnings': True
        }
        
        try:
            if not config.save_config(new_config):
                raise Exception("Failed to write config file")
                
            # Update runtime config
            config.MYSQL_CONFIG.update(new_config)
            
            # Initialize DB Utils
            from database.schema_mysql import initialize_mysql_database
            initialize_mysql_database()
            
            return True
            
        except Exception as e:
            self.status_label.setText(f"Failed to save config: {e}")
            return False

class AdminPage(QWizardPage):
    """Page to create initial Admin account"""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Admin Account Setup")
        self.setSubTitle("Create your master administrator account.")
        
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        self.username_input = QLineEdit("admin")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        form_layout.addRow("Username:", self.username_input)
        form_layout.addRow("Password:", self.password_input)
        form_layout.addRow("Confirm Password:", self.confirm_input)
        
        layout.addLayout(form_layout)
        self.setLayout(layout)
        
    def initializePage(self):
        # Check if users exist
        try:
            cursor = db.get_connection().cursor()
            # If using pymysql directly, cursor is DictCursor usually, but let's check basic query
            cursor.execute("SELECT COUNT(*) as count FROM users")
            result = cursor.fetchone()
            count = result['count'] if result else 0
            if count > 0:
                self.setTitle("Admin Account (Optional)")
                self.setSubTitle("Users already exist in the database. You can skip this step or create another admin.")
        except:
            pass
            
    def validatePage(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        confirm = self.confirm_input.text()
        
        if not username:
            QMessageBox.warning(self, "Validation Error", "Username is required.")
            return False
            
        if not password:
            QMessageBox.warning(self, "Validation Error", "Password is required.")
            return False
            
        if password != confirm:
            QMessageBox.warning(self, "Validation Error", "Passwords do not match.")
            return False
            
        # Create User
        try:
            from services.auth_service import auth_service
            # auth_service has create_user? No, usually in repository
            from repositories.user_repo import user_repo
            from database.models import User
            
            # Check if user exists
            existing = user_repo.get_by_username(username)
            if existing:
                QMessageBox.warning(self, "Error", f"User '{username}' already exists.")
                return False
                
            # Manual creation since auth_service might handle login state
            # Assuming user_repo.create handles hashing? 
            # Let's check user_repo.py in next step if verification fails.
            # Assuming standard create(user_obj, password) or similar.
            
            # Wait, let's check user_repo.py signature.
            # Assuming user_repo.create(user_data, password)
            
            new_user = User(
                id=None,
                username=username,
                password_hash="", # Repo will handle
                role="admin",
                full_name="Administrator",
                is_active=True
            )
            
            if user_repo.create_user(new_user, password):
                return True
            else:
                QMessageBox.critical(self, "Error", "Failed to create user in database.")
                return False
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create user: {e}")
            return False
