"""
Pharmacy POS - Main Entry Point
Production-ready, offline-first Point of Sale for pharmacies
"""
import sys
import os

# Add the project directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication, QSplashScreen, QMessageBox, QDialog
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPixmap

from config import APP_NAME, APP_VERSION, BACKUP_DIR, resource_path
from database.schema import initialize_database
from ui.main_window import MainWindow
from ui.login_dialog import LoginDialog
from services.auth_service import auth_service


def create_splash() -> QSplashScreen:
    """Create a premium splash screen"""
    from PyQt6.QtGui import QPainter, QColor, QLinearGradient, QBrush
    
    # Dimensions
    width, height = 500, 300
    pixmap = QPixmap(width, height)
    
    # 1. Background Gradient
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    gradient = QLinearGradient(0, 0, 0, height)
    gradient.setColorAt(0.0, QColor("#1A1A2E"))  # Dark Blue/Gray
    gradient.setColorAt(1.0, QColor("#0D1B2A"))  # Darker
    painter.fillRect(pixmap.rect(), QBrush(gradient))
    
    # 2. Border
    painter.setPen(QColor("#0D7377"))
    painter.drawRect(0, 0, width-1, height-1)
    
    # 3. Logo
    logo_path = resource_path(os.path.join("assets", "pharmacy.png"))
    if os.path.exists(logo_path):
        logo_pixmap = QPixmap(logo_path)
        logo_scaled = logo_pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        # Center logo horizontally, somewhat near top
        logo_x = (width - logo_scaled.width()) // 2
        logo_y = 50
        painter.drawPixmap(logo_x, logo_y, logo_scaled)
        
        text_y_start = logo_y + 80 + 40
    else:
        # Fallback text only layout
        text_y_start = 120
    
    # 4. App Name
    painter.setPen(QColor("#FFFFFF"))
    font = QFont("Segoe UI", 28, QFont.Weight.Bold)
    painter.setFont(font)
    painter.drawText(
        0, text_y_start - 30, width, 50, 
        Qt.AlignmentFlag.AlignCenter, 
        APP_NAME
    )
    
    # 5. Version
    painter.setPen(QColor("#0D7377"))
    font_small = QFont("Segoe UI", 10)
    painter.setFont(font_small)
    painter.drawText(
        0, text_y_start + 20, width, 30, 
        Qt.AlignmentFlag.AlignCenter, 
        f"v{APP_VERSION}"
    )
    
    painter.end()
    
    splash = QSplashScreen(pixmap)
    return splash


def main():
    """Main application entry point"""
    # Set high DPI attributes before creating app
    # Note: In PyQt6, high DPI is enabled by default
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    
    # Set default font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # Set App Icon
    from PyQt6.QtGui import QIcon
    icon_path = resource_path(os.path.join("assets", "pharmacy.png"))
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # Show splash screen
    splash = create_splash()
    splash.show()
    app.processEvents()
    
    try:
        # Initialize database
        splash.showMessage(
            "Initializing database...", 
            Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter,
            Qt.GlobalColor.white
        )
        app.processEvents()
        
        # Ensure backup directory exists
        os.makedirs(BACKUP_DIR, exist_ok=True)
        
        
        # Check if first run (config missing) or init fails
        import config
        setup_required = not os.path.exists(config.DB_CONFIG_FILE)
        
        if not setup_required:
            try:
                initialize_database()
            except Exception as e:
                print(f"Database initialization failed: {e}")
                setup_required = True
        
        if setup_required:
            # Launch Setup Wizard
            splash.close()
            from ui.setup_wizard import SetupWizard
            wizard = SetupWizard()
            if wizard.exec() == QDialog.DialogCode.Accepted:
                # Setup successful, retry initialization
                splash.show()
                splash.showMessage("Initializing system...", Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter, Qt.GlobalColor.white)
                app.processEvents()
                initialize_database()
            else:
                # Setup cancelled
                sys.exit(0)
        
        # Ensure at least one admin exists
        
        # Ensure at least one admin exists
        splash.showMessage("Checking security...", Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter, Qt.GlobalColor.white)
        auth_service.ensure_default_admin()
        
        # Close initial splash
        splash.close()
        
        # Application Loop
        while True:
            # Show Login Dialog
            login = LoginDialog()
            if login.exec() == QDialog.DialogCode.Accepted:
                # Re-show splash screen while loading main window
                splash.show()
                splash.showMessage(
                    "Loading interface...", 
                    Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter, 
                    Qt.GlobalColor.white
                )
                app.processEvents()
    
                # Create main window only after successful login
                window = MainWindow()
                
                # Close splash and show main window
                splash.finish(window)
                window.show()
                
                # Run the application event loop
                app.exec() # Blocks until window closes
                
                # Check for Logout vs Quit
                if not auth_service.get_current_user():
                    # User logged out explicitly (auth_service.logout() was called)
                    # Loop continues -> Show LoginDialog again
                    continue
                else:
                    # Window closed normally (Quit)
                    break
            else:
                # Login cancelled
                break
                
        sys.exit(0)
        
    except Exception as e:
        splash.close()
        _show_startup_error(str(e))
        sys.exit(1)


def _show_startup_error(error_msg: str):
    """Show a premium dark-themed startup error dialog"""
    from PyQt6.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
        QPushButton, QFrame, QGraphicsDropShadowEffect
    )
    from PyQt6.QtGui import QColor, QPainter, QBrush, QLinearGradient

    dialog = QDialog()
    dialog.setWindowTitle("Startup Error")
    dialog.setFixedSize(480, 320)
    dialog.setStyleSheet("background-color: #0D1117;")

    layout = QVBoxLayout(dialog)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)

    # ── Top accent bar ──
    accent = QFrame()
    accent.setFixedHeight(4)
    accent.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #E94560, stop:1 #FF6B6B);")
    layout.addWidget(accent)

    # ── Content container ──
    content = QFrame()
    content.setStyleSheet("""
        QFrame {
            background-color: #161B22;
            border: 1px solid #30363D;
            border-top: none;
            margin: 12px;
            border-radius: 0px;
        }
    """)
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(25)
    shadow.setColor(QColor(0, 0, 0, 120))
    shadow.setOffset(0, 6)
    content.setGraphicsEffect(shadow)

    c_layout = QVBoxLayout(content)
    c_layout.setContentsMargins(28, 28, 28, 24)
    c_layout.setSpacing(16)

    # ── Icon + Title row ──
    header = QHBoxLayout()
    header.setSpacing(14)

    icon_frame = QFrame()
    icon_frame.setFixedSize(48, 48)
    icon_frame.setStyleSheet("""
        QFrame {
            background-color: rgba(233, 69, 96, 0.15);
            border: 1px solid rgba(233, 69, 96, 0.3);
            border-radius: 10px;
            margin: 0px;
        }
    """)
    icon_lbl = QLabel("✕", icon_frame)
    icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    icon_lbl.setFixedSize(48, 48)
    icon_lbl.setStyleSheet("""
        color: #E94560;
        font-size: 26px;
        font-weight: bold;
        border: none;
        background: transparent;
    """)
    header.addWidget(icon_frame)

    title = QLabel("Unable to Start")
    title.setStyleSheet("""
        color: #F0F6FC;
        font-size: 18px;
        font-weight: bold;
        border: none;
        background: transparent;
    """)
    header.addWidget(title)
    header.addStretch()
    c_layout.addLayout(header)

    # ── Separator ──
    sep = QFrame()
    sep.setFixedHeight(1)
    sep.setStyleSheet("background-color: #30363D; border: none; margin: 0px;")
    c_layout.addWidget(sep)

    # ── Error message (user-friendly) ──
    friendly = (
        "The application could not connect to the database.\n\n"
        "Please make sure your MySQL service is running\n"
        "(XAMPP or MySQL Server), then try again."
    )
    msg = QLabel(friendly)
    msg.setWordWrap(True)
    msg.setStyleSheet("""
        color: #8B949E;
        font-size: 13px;
        line-height: 1.5;
        border: none;
        background: transparent;
        padding: 4px 0;
    """)
    c_layout.addWidget(msg)

    c_layout.addStretch()

    # ── Button row ──
    btn_row = QHBoxLayout()
    btn_row.addStretch()

    ok_btn = QPushButton("OK")
    ok_btn.setFixedSize(120, 38)
    ok_btn.setCursor(Qt.CursorShape.PointingHandCursor)
    ok_btn.setStyleSheet("""
        QPushButton {
            background-color: #E94560;
            color: #FFFFFF;
            font-size: 13px;
            font-weight: bold;
            border: none;
            border-radius: 0px;
        }
        QPushButton:hover {
            background-color: #D63851;
        }
        QPushButton:pressed {
            background-color: #B00020;
        }
    """)
    ok_btn.clicked.connect(dialog.accept)
    btn_row.addWidget(ok_btn)
    c_layout.addLayout(btn_row)

    layout.addWidget(content)
    dialog.exec()


if __name__ == "__main__":
    main()
