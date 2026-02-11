"""
Barcode Input Component - Auto-focused input field for barcode scanning
Optimized for USB HID barcode scanners
"""
from PyQt6.QtWidgets import QLineEdit, QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PyQt6.QtCore import pyqtSignal, Qt, QTimer
from PyQt6.QtGui import QKeyEvent


class BarcodeInput(QWidget):
    """
    Auto-focused barcode input field
    Emits scanned signal when Enter is pressed (barcode scanner behavior)
    """
    
    barcode_scanned = pyqtSignal(str)  # Emitted when barcode is scanned
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
        # Debounce timer for rapid scanning
        self.debounce_timer = QTimer()
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.setInterval(50)  # 50ms debounce
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Label
        label = QLabel("Scan Barcode")
        label.setStyleSheet("font-size: 12px; color: #B0B0B0;")
        layout.addWidget(label)
        
        # Input field
        self.input_field = QLineEdit()
        self.input_field.setObjectName("barcodeInput")
        self.input_field.setPlaceholderText("Scan or type barcode...")
        self.input_field.setClearButtonEnabled(True)
        
        # Connect signals
        self.input_field.returnPressed.connect(self.on_return_pressed)
        
        layout.addWidget(self.input_field)
    
    def on_return_pressed(self):
        """Handle Enter key press (barcode scanned)"""
        barcode = self.input_field.text().strip()
        if barcode:
            self.barcode_scanned.emit(barcode)
            self.input_field.clear()
        
        # Keep focus on input field
        self.input_field.setFocus()
    
    def focus_input(self):
        """Set focus to the input field"""
        self.input_field.setFocus()
        self.input_field.selectAll()
    
    def clear(self):
        """Clear the input field"""
        self.input_field.clear()
    
    def setPlaceholderText(self, text: str):
        """Set placeholder text for the input field"""
        self.input_field.setPlaceholderText(text)
    
    def showEvent(self, event):
        """Auto-focus when widget becomes visible"""
        super().showEvent(event)
        QTimer.singleShot(100, self.focus_input)


class BarcodeInputLarge(BarcodeInput):
    """Large version of barcode input for main checkout screen"""
    
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Scan icon/label
        icon_label = QLabel()
        icon_label.setFixedSize(24, 24)
        icon_label.setScaledContents(True)
        icon_label.setStyleSheet("background: transparent; border: none;")
        
        import os.path
        from PyQt6.QtGui import QPixmap
        from config import resource_path
        icon_path = resource_path(os.path.join("assets", "search.png"))
        if os.path.exists(icon_path):
            icon_label.setPixmap(QPixmap(icon_path))
        else:
            icon_label.setText("🔍") # Fallback
        layout.addWidget(icon_label)
        
        # Input field
        self.input_field = QLineEdit()
        self.input_field.setObjectName("barcodeInput")
        self.input_field.setPlaceholderText("Scan barcode or search product...")
        self.input_field.setClearButtonEnabled(True)
        self.input_field.setMinimumHeight(50)
        
        # Connect signals
        self.input_field.returnPressed.connect(self.on_return_pressed)
        
        layout.addWidget(self.input_field, 1)
