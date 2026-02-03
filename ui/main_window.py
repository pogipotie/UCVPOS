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
from config import APP_NAME, APP_VERSION


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.apply_styles()
    
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
        self.cashier_screen = CashierScreen()
        self.inventory_screen = InventoryScreen()
        self.reports_screen = ReportsScreen()
        
        self.content_stack.addWidget(self.cashier_screen)
        self.content_stack.addWidget(self.inventory_screen)
        self.content_stack.addWidget(self.reports_screen)
        
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
        
        # POS button
        pos_btn = self._create_nav_button("POINT OF SALE", 0, "assets/POS.png")
        pos_btn.setChecked(True)
        layout.addWidget(pos_btn)
        
        # Inventory button
        inv_btn = self._create_nav_button("INVENTORY", 1, "assets/inventory.png")
        layout.addWidget(inv_btn)
        
        # Reports button
        reports_btn = self._create_nav_button("REPORTS", 2, "assets/Reports.png")
        layout.addWidget(reports_btn)
        
        layout.addStretch()
        
        # Footer removed as per request
        
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
                        text-align: center;
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
        
        if not icon_path:
             btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #B0B0B0;
                    text-align: center;
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
        if index == 1:  # Inventory
            self.inventory_screen.refresh()
    
    def _update_status_bar(self):
        """Update status bar with current info"""
        from datetime import datetime
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.status_bar.showMessage(f"Ready | {now} | Database: pos.db")
    
    def apply_styles(self):
        """Apply the main stylesheet"""
        self.setStyleSheet(MAIN_STYLESHEET)
    
    def closeEvent(self, event):
        """Handle window close"""
        from database.connection import db
        db.close()
        event.accept()
