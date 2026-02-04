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

from config import APP_NAME, APP_VERSION, BACKUP_DIR
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
    logo_path = os.path.join(os.path.dirname(__file__), "assets", "pharmacy.png")
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
    icon_path = os.path.join(os.path.dirname(__file__), "assets", "pharmacy.png")
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
        
        # Initialize database schema
        initialize_database()
        
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
        QMessageBox.critical(
            None, 
            "Startup Error",
            f"Failed to start application:\n\n{str(e)}"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
