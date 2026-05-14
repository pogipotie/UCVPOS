from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QDialog, QFormLayout, QLineEdit, QComboBox,
    QMessageBox, QHeaderView, QGroupBox, QFrame, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QColor
from repositories.user_repo import user_repo
from database.models import User

class UserFormDialog(QDialog):
    """Dialog to Add/Edit User (Premium UI)"""
    def __init__(self, parent=None, user: User = None):
        super().__init__(parent)
        self.user = user
        # Window Setup
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(500, 450)
        self.old_pos = None
        self.setup_ui()
        if user:
            self.populate_form()
            
    def setup_ui(self):
        # Main Layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Container
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
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        # --- Header ---
        header = QFrame()
        header.setStyleSheet("""
            background-color: #252525;
            border-bottom: 1px solid #333333;
            border-radius: 0px;
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 15, 20, 15)
        
        title_text = "Edit User" if self.user else "Add New User"
        title_lbl = QLabel(title_text)
        title_lbl.setStyleSheet("color: #03DAC6; font-size: 18px; font-weight: bold; border: none;")
        header_layout.addWidget(title_lbl)
        header_layout.addStretch()
        
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent; color: #B3B3B3; border: none; font-size: 16px; font-weight: bold;
            }
            QPushButton:hover { color: #FFFFFF; background-color: #CF6679; border-radius: 0px; }
        """)
        close_btn.clicked.connect(self.reject)
        header_layout.addWidget(close_btn)
        
        container_layout.addWidget(header)
        
        # --- Content ---
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(20)
        
        # Username
        self.username = self._create_input("Username *")
        content_layout.addWidget(self._create_field_container("Username", self.username))
        
        # Full Name
        self.full_name = self._create_input("Full Name")
        content_layout.addWidget(self._create_field_container("Full Name", self.full_name))
        
        # Role
        self.role = QComboBox()
        self.role.addItems(["cashier", "admin"])

        self.role.setFixedHeight(40)
        self.role.setStyleSheet("""
            QComboBox {
                background-color: #2C2C2C; color: white; border: 1px solid #333333; padding: 5px 10px; border-radius: 0px;
            }
            QComboBox::drop-down { border: none; }
            QComboBox::down-arrow { image: url(assets/arrow_down.svg); width: 12px; height: 12px; }
        """)
        content_layout.addWidget(self._create_field_container("Role", self.role))
        
        # Password
        self.password = self._create_input("Password")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setPlaceholderText("Leave empty to keep current" if self.user else "Required")
        content_layout.addWidget(self._create_field_container("Password", self.password))
        
        container_layout.addWidget(content_widget)
        
        # --- Footer ---
        footer = QFrame()
        footer.setStyleSheet("""
            background-color: #252525; border-top: 1px solid #333333; border-radius: 0px;
        """)
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(20, 15, 20, 15)
        footer_layout.setSpacing(15)
        footer_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setFixedSize(100, 40)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent; border: 1px solid #444; color: #B3B3B3; border-radius: 0px; font-weight: 600;
            }
            QPushButton:hover { background-color: #333; color: white; }
        """)
        cancel_btn.clicked.connect(self.reject)
        footer_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save User")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setFixedSize(120, 40)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #03DAC6; border: none; color: black; border-radius: 0px; font-weight: bold; font-size: 14px;
            }
            QPushButton:hover { background-color: #05E5D0; }
        """)
        save_btn.clicked.connect(self.save_user)
        footer_layout.addWidget(save_btn)
        
        container_layout.addWidget(footer)
        main_layout.addWidget(self.container)

    def _create_input(self, placeholder):
        le = QLineEdit()
        le.setPlaceholderText(placeholder)
        le.setFixedHeight(40)
        le.setStyleSheet("""
            QLineEdit {
                background-color: #2C2C2C; border: 1px solid #333333; border-radius: 0px; padding: 0 10px; color: white;
            }
            QLineEdit:focus { border: 1px solid #03DAC6; }
        """)
        return le

    def _create_field_container(self, label, widget):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(5)
        lbl = QLabel(label)
        lbl.setStyleSheet("color: #B3B3B3; font-size: 12px; font-weight: bold; text-transform: uppercase;")
        layout.addWidget(lbl)
        layout.addWidget(widget)
        return container

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.pos() + delta)
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.old_pos = None
        
    def populate_form(self):
        self.username.setText(self.user.username)
        self.username.setEnabled(False) # Cannot change username
        self.username.setStyleSheet(self.username.styleSheet() + "color: #666;")
        self.full_name.setText(self.user.full_name or "")
        self.role.setCurrentText(self.user.role)
        
    def save_user(self):
        username = self.username.text().strip()
        password = self.password.text().strip()
        full_name = self.full_name.text().strip()
        role = self.role.currentText()
        
        if not username:
            QMessageBox.warning(self, "Error", "Username required")
            return
            
        if not self.user and not password:
            QMessageBox.warning(self, "Error", "Password required for new user")
            return
            
        try:
            if self.user:
                # Update
                self.user.full_name = full_name
                self.user.role = role
                self.user.is_active = True
                user_repo.update_user(self.user)
                if password:
                    user_repo.update_password(self.user.id, password)
            else:
                # Create
                new_user = User(
                    username=username,
                    full_name=full_name,
                    role=role,
                    is_active=True
                )
                if user_repo.get_by_username(username):
                    QMessageBox.warning(self, "Error", "Username already exists")
                    return
                user_repo.create_user(new_user, password)
                
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class UserManagementScreen(QWidget):
    """Screen to manage users"""
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.refresh_data()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = QHBoxLayout()
        title = QLabel("User Management")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #FFFFFF;")
        header.addWidget(title)
        header.addStretch()
        
        add_btn = QPushButton("+ Add User")
        add_btn.setStyleSheet("""
            background-color: #0D7377; color: white; padding: 8px 16px; border-radius: 4px;
        """)
        add_btn.clicked.connect(self.add_user)
        header.addWidget(add_btn)
        
        layout.addLayout(header)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Username", "Full Name", "Role", "Last Login"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #1A1A2E; color: white; border: 1px solid #2D3A5A;
            }
            QHeaderView::section {
                background-color: #0F0F1A; color: white; padding: 8px;
            }
        """)
        self.table.doubleClicked.connect(self.edit_user)
        layout.addWidget(self.table)
        
        # Note
        note = QLabel("Double-click a row to edit user.")
        note.setStyleSheet("color: #888888; font-style: italic;")
        layout.addWidget(note)
        
    def refresh_data(self):
        users = user_repo.get_all()
        self.table.setRowCount(len(users))
        for row, user in enumerate(users):
            self.table.setItem(row, 0, QTableWidgetItem(str(user.id)))
            self.table.setItem(row, 1, QTableWidgetItem(user.username))
            self.table.setItem(row, 2, QTableWidgetItem(user.full_name or ""))
            self.table.setItem(row, 3, QTableWidgetItem(user.role))
            self.table.setItem(row, 4, QTableWidgetItem(str(user.last_login or "Ns/A")))
            
    def add_user(self):
        dialog = UserFormDialog(self)
        if dialog.exec():
            self.refresh_data()
            
    def edit_user(self):
        row = self.table.currentRow()
        if row < 0: return
        
        username = self.table.item(row, 1).text()
        user = user_repo.get_by_username(username)
        
        if user:
            dialog = UserFormDialog(self, user)
            if dialog.exec():
                self.refresh_data()
