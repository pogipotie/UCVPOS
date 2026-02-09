"""
Main Window - Application shell with navigation
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QStackedWidget, QLabel, QFrame, QStatusBar
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from ui.styles import MAIN_STYLESHEET
from ui.cashier_screen import CashierScreen
from ui.inventory_screen import InventoryScreen
from ui.reports_screen import ReportsScreen
from ui.user_management_screen import UserManagementScreen
from ui.admin_dashboard import AdminDashboard
from ui.settings_screen import SettingsScreen
from ui.components.logout_dialog import LogoutDialog
from services.auth_service import auth_service
from config import APP_NAME, APP_VERSION
from PyQt6.QtWidgets import QMessageBox


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_ui()
        self.apply_permissions()
        self.apply_styles()
        self._setup_shortcuts()
    
    def _setup_shortcuts(self):
        """Setup global keyboard shortcuts"""
        from PyQt6.QtGui import QKeySequence, QShortcut
        
        # F1 -> POS (Index 1)
        self.shortcut_f1 = QShortcut(QKeySequence("F1"), self)
        self.shortcut_f1.activated.connect(lambda: self._navigate_to(1))
        
        # F2 -> Inventory (Index 2)
        self.shortcut_f2 = QShortcut(QKeySequence("F2"), self)
        self.shortcut_f2.activated.connect(lambda: self._navigate_to(2))
        
        # F3 -> Reports (Index 3) - User requested "Sales History"
        self.shortcut_f3 = QShortcut(QKeySequence("F3"), self)
        self.shortcut_f3.activated.connect(lambda: self._navigate_to(3))
        
        # F4 -> Reports (Index 3)
        self.shortcut_f4 = QShortcut(QKeySequence("F4"), self)
        self.shortcut_f4.activated.connect(lambda: self._navigate_to(3))
    
    def setup_ui(self):
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setMinimumSize(1200, 800)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar navigation
        sidebar = self._create_sidebar()
        main_layout.addWidget(sidebar)
        
        # Content area
        self.content_stack = QStackedWidget()
        
        # Add screens
        self.admin_dashboard = AdminDashboard()
        self.cashier_screen = CashierScreen()
        self.inventory_screen = InventoryScreen()
        self.reports_screen = ReportsScreen()
        self.user_management_screen = UserManagementScreen()
        self.settings_screen = SettingsScreen()
        
        # Stack Order
        self.content_stack.addWidget(self.admin_dashboard)      # Index 0
        self.content_stack.addWidget(self.cashier_screen)       # Index 1
        self.content_stack.addWidget(self.inventory_screen)     # Index 2
        self.content_stack.addWidget(self.reports_screen)       # Index 3
        self.content_stack.addWidget(self.user_management_screen) # Index 4
        self.content_stack.addWidget(self.settings_screen)       # Index 5
        
        main_layout.addWidget(self.content_stack, 1)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self._update_status_bar()
        
        # Timer to update status bar
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self._update_status_bar)
        self.status_timer.start(60000)  # Update every minute
    
    def _create_sidebar(self) -> QFrame:
        """Create the sidebar navigation"""
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(260)
        sidebar.setStyleSheet("""
            QFrame#sidebar {
                background-color: #0F0F1A;
                border-right: 1px solid #2D3A5A;
            }
        """)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(5)
        
        # Logo/Title
        logo_layout = QHBoxLayout()
        logo_layout.setSpacing(4)
        logo_layout.setContentsMargins(0, 5, 0, 5)
        
        import os
        from PyQt6.QtGui import QPixmap
        
        # Logo Icon
        logo_icon = QLabel()
        logo_icon.setFixedSize(40, 40)
        logo_icon.setScaledContents(True)
        
        # Navigate up from ui/ to root
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "pharmacy.png")
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            logo_icon.setPixmap(pixmap)
        
        # Logo Text
        logo_text = QLabel(APP_NAME)
        logo_text.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #0D7377;
        """)
        
        logo_layout.addWidget(logo_icon)
        logo_layout.addWidget(logo_text)
        logo_layout.addStretch()
        layout.addLayout(logo_layout)
        
        version_label = QLabel(f"v{APP_VERSION}")
        version_label.setStyleSheet("color: #666666; font-size: 10px; padding-left: 10px;")
        layout.addWidget(version_label)
        
        layout.addSpacing(30)
        
        # Navigation buttons
        self.nav_buttons = []
        
        # Dashboard (Index 0)
        dash_btn = self._create_nav_button("DASHBOARD", 0, "assets/dashboard.png")
        layout.addWidget(dash_btn)
        
        # POS button (Index 1)
        pos_btn = self._create_nav_button("POINT OF SALE", 1, "assets/POS.png")
        layout.addWidget(pos_btn)
        
        # Inventory button (Index 2)
        inv_btn = self._create_nav_button("INVENTORY", 2, "assets/inventory.png")
        layout.addWidget(inv_btn)
        
        # Reports button (Index 3)
        reports_btn = self._create_nav_button("REPORTS", 3, "assets/Reports.png")
        layout.addWidget(reports_btn)
        
        # User Management button (Index 4)
        users_btn = self._create_nav_button("USERS", 4, "assets/user.png")
        layout.addWidget(users_btn)
        
        # Settings button (Index 5)
        settings_btn = self._create_nav_button("SETTINGS", 5, "assets/settings.png")
        layout.addWidget(settings_btn)
        
        layout.addStretch()
        
        # Logout button
        logout_btn = QPushButton("LOGOUT")
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.clicked.connect(self.logout)
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #E94560;
                text-align: center;
                padding: 10px 15px;
                border: 1px solid #E94560;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #E94560;
                color: white;
            }
        """)
        layout.addWidget(logout_btn)
        
        return sidebar
    
    def _create_nav_button(self, text: str, index: int, icon_path: str = None) -> QPushButton:
        """Create a navigation button"""
        from PyQt6.QtGui import QIcon
        from PyQt6.QtCore import QSize
        import os
        
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setMinimumHeight(45)
        
        if icon_path:
            # Resolve path relative to root
            full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), icon_path)
            if os.path.exists(full_path):
                btn.setIcon(QIcon(full_path))
                btn.setIconSize(QSize(24, 24))
                # Add some padding to icon
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: transparent;
                        color: #B0B0B0;
                        text-align: left;
                        padding: 10px 15px;
                        border: none;
                        border-radius: 0px;
                        font-size: 14px;
                    }}
                    QPushButton:hover {{
                        background-color: #1F2B47;
                        color: #FFFFFF;
                    }}
                    QPushButton:checked {{
                        background-color: #0D7377;
                        color: #FFFFFF;
                        border: 1px solid #FFFFFF;
                    }}
                """)
            else:
                # Fallback style if icon missing
                pass
        
        if not icon_path or not os.path.exists(os.path.join(os.path.dirname(os.path.dirname(__file__)), icon_path)):
             btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #B0B0B0;
                    text-align: left;
                    padding: 10px 15px;
                    border: none;
                    border-radius: 0px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #1F2B47;
                    color: #FFFFFF;
                }
                QPushButton:checked {
                    background-color: #0D7377;
                    color: #FFFFFF;
                    border: 1px solid #FFFFFF;
                }
            """)
            
        btn.clicked.connect(lambda: self._navigate_to(index))
        self.nav_buttons.append(btn)
        return btn
    
    def _navigate_to(self, index: int):
        """Navigate to a screen"""
        # Update button states
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)
        
        # Switch content
        self.content_stack.setCurrentIndex(index)
        
        # Refresh data if needed
        if index == 0: # Dashboard
            if hasattr(self, 'admin_dashboard'):
                self.admin_dashboard.refresh_data()
        elif index == 2:  # Inventory
            self.inventory_screen.refresh()
        elif index == 4: # Users
             self.user_management_screen.refresh_data()
        elif index == 5: # Settings
             if hasattr(self, 'settings_screen'):
                 self.settings_screen.load_data()
    
    def apply_permissions(self):
        """Enable/Disable features based on role"""
        user = auth_service.get_current_user()
        if not user:
            return
            
        # Admin gets everything (default)
        if user.role == 'admin':
            # Default to Dashboard
            self._navigate_to(0)
            return
            
        # Cashier restrictions
        if user.role == 'cashier':
            # Dashboard (index 0) - Hide
            if len(self.nav_buttons) > 0:
                self.nav_buttons[0].hide()
            
            # Users Tab (index 4) - Hide
            if len(self.nav_buttons) > 4:
                self.nav_buttons[4].hide()
            
            # Settings Tab (index 5) - Hide
            if len(self.nav_buttons) > 5:
                self.nav_buttons[5].hide()
            
            # Default to POS (Index 1)
            self._navigate_to(1)
             
            # Inventory (index 2) & Reports (index 3) are visible but restricted internally

    
    def logout(self):
        """Handle logout"""
        dialog = LogoutDialog(self)
        if dialog.exec():
            # User confirmed logout
            auth_service.logout()
            self.close()
            
    def _update_status_bar(self):
        """Update status bar with current info"""
        from datetime import datetime
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        user = auth_service.get_current_user()
        user_str = f"{user.username} ({user.role})" if user else "Not Logged In"
        
        self.status_bar.showMessage(f"Ready | {now} | User: {user_str}")
    
    def apply_styles(self):
        """Apply the main stylesheet"""
        self.setStyleSheet(MAIN_STYLESHEET)
    
    def closeEvent(self, event):
        """Handle window close - use logout dialog for confirmation"""
        # Check if user is logged in
        user = auth_service.get_current_user()
        
        if user:
            # Use the existing logout dialog
            dialog = LogoutDialog(self)
            if dialog.exec():
                # User confirmed - logout and close
                auth_service.logout()
                from database.connection import db
                db.close()
                event.accept()
            else:
                # User cancelled - ignore close
                event.ignore()
        else:
            # No user logged in, just close
            from database.connection import db
            db.close()
            event.accept()
