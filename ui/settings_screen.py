"""
Settings Screen - Configuration for the application
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QGroupBox, QDoubleSpinBox, QFileDialog,
    QFormLayout, QMessageBox, QScrollArea
)
from PyQt6.QtCore import Qt
from services.settings_service import settings_service

class SettingsScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = QLabel("System Settings")
        header.setStyleSheet("color: white; font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(header)
        
        # Scroll Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(20)
        
        # 1. Store Information
        store_group = QGroupBox("Store Information")
        store_group.setStyleSheet(self._group_box_style())
        store_layout = QFormLayout(store_group)
        store_layout.setSpacing(15)
        
        self.store_name = self._create_input("Store Name")
        self.store_address = self._create_input("Address")
        self.store_phone = self._create_input("Phone Number")
        self.store_header = self._create_input("Receipt Header Message")
        
        store_layout.addRow(self._create_label("Store Name:"), self.store_name)
        store_layout.addRow(self._create_label("Address:"), self.store_address)
        store_layout.addRow(self._create_label("Phone:"), self.store_phone)
        store_layout.addRow(self._create_label("Receipt Header:"), self.store_header)
        
        content_layout.addWidget(store_group)
        
        # 2. Financials
        finance_group = QGroupBox("Financials")
        finance_group.setStyleSheet(self._group_box_style())
        finance_layout = QFormLayout(finance_group)
        finance_layout.setSpacing(15)
        
        self.tax_rate = QDoubleSpinBox()
        self.tax_rate.setRange(0, 100)
        self.tax_rate.setSingleStep(1.0)
        self.tax_rate.setSuffix("%")
        self.tax_rate.setStyleSheet(self._spinbox_style())
        
        self.currency_symbol = self._create_input("Currency Symbol (e.g., ₱)")
        self.currency_symbol.setFixedWidth(50)
        
        finance_layout.addRow(self._create_label("Tax Rate (VAT):"), self.tax_rate)
        finance_layout.addRow(self._create_label("Currency:"), self.currency_symbol)
        
        content_layout.addWidget(finance_group)
        
        # 3. System
        system_group = QGroupBox("System & Data")
        system_group.setStyleSheet(self._group_box_style())
        system_layout = QFormLayout(system_group)
        system_layout.setSpacing(15)
        
        path_layout = QHBoxLayout()
        self.backup_path = self._create_input("")
        self.backup_path.setReadOnly(True)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.setFixedWidth(100)
        browse_btn.clicked.connect(self.browse_backup_path)
        browse_btn.setStyleSheet("""
            QPushButton {
                background-color: #333333;
                color: white;
                border: 1px solid #555;
                padding: 5px;
                border-radius: 0px;
            }
            QPushButton:hover { background-color: #444; }
        """)
        
        path_layout.addWidget(self.backup_path)
        path_layout.addWidget(browse_btn)
        
        system_layout.addRow(self._create_label("Backup Location:"), path_layout)

        # Report Save Location
        report_path_layout = QHBoxLayout()
        self.report_path = self._create_input("")
        self.report_path.setReadOnly(True)
        
        browse_report_btn = QPushButton("Browse...")
        browse_report_btn.setFixedWidth(100)
        browse_report_btn.clicked.connect(self.browse_report_path)
        browse_report_btn.setStyleSheet(browse_btn.styleSheet())
        
        report_path_layout.addWidget(self.report_path)
        report_path_layout.addWidget(browse_report_btn)
        
        system_layout.addRow(self._create_label("Reports Save Location:"), report_path_layout)
        
        content_layout.addWidget(system_group)
        
        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        # Save Button
        save_btn = QPushButton("Save Settings")
        save_btn.setMinimumHeight(50)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self.save_settings)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #03DAC6;
                color: #000000;
                font-weight: bold;
                font-size: 16px;
                border-radius: 0px;
                margin-top: 10px;
            }
            QPushButton:hover { background-color: #018786; }
        """)
        
        layout.addWidget(save_btn)
        
    def load_data(self):
        """Load current settings into fields"""
        settings = settings_service.get_all()
        
        store = settings.get('store_info', {})
        self.store_name.setText(store.get('name', ''))
        self.store_address.setText(store.get('address', ''))
        self.store_phone.setText(store.get('phone', ''))
        self.store_header.setText(store.get('header_text', ''))
        
        financial = settings.get('financial', {})
        self.tax_rate.setValue(financial.get('tax_rate', 0.0))
        self.currency_symbol.setText(financial.get('currency_symbol', '₱'))
        
        system = settings.get('system', {})
        self.backup_path.setText(system.get('backup_path', ''))
        self.report_path.setText(system.get('reports_path', ''))
        
    def save_settings(self):
        """Save fields back to service"""
        new_settings = {
            "store_info": {
                "name": self.store_name.text(),
                "address": self.store_address.text(),
                "phone": self.store_phone.text(),
                "header_text": self.store_header.text()
            },
            "financial": {
                "tax_rate": self.tax_rate.value(),
                "currency_symbol": self.currency_symbol.text()
            },
            "system": {
                "backup_path": self.backup_path.text(),
                "reports_path": self.report_path.text(),
                "printer_name": "" 
            }
        }
        
        # Preserve existing printer_name if not in UI
        current = settings_service.get_all()
        new_settings["system"]["printer_name"] = current.get("system", {}).get("printer_name", "")
        
        settings_service.update_all(new_settings)
        
        from ui.components.custom_message_box import CustomSuccessDialog
        dialog = CustomSuccessDialog(self, "Settings Saved", "Your configuration has been successfully updated.")
        dialog.exec()
        
    def browse_backup_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select Backup Folder")
        if path:
            self.backup_path.setText(path)

    def browse_report_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select Reports Folder")
        if path:
            self.report_path.setText(path)
            
    def _create_input(self, placeholder):
        inp = QLineEdit()
        inp.setPlaceholderText(placeholder)
        inp.setStyleSheet(self._input_style())
        return inp
        
    def _create_label(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet("color: #CCCCCC; font-size: 14px;")
        return lbl
        
    def _group_box_style(self):
        return """
            QGroupBox {
                color: #03DAC6;
                font-weight: bold;
                border: 1px solid #333333;
                border-radius: 0px;
                margin-top: 20px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """
        
    def _input_style(self):
        return """
            QLineEdit {
                background-color: #2D2D2D;
                border: 1px solid #333333;
                border-radius: 0px;
                padding: 10px;
                color: white;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #03DAC6;
            }
        """

    def _spinbox_style(self):
        return """
            QDoubleSpinBox {
                background-color: #2D2D2D;
                border: 1px solid #333333;
                border-radius: 0px;
                padding: 5px 10px;
                color: white;
                font-size: 14px;
            }
            QDoubleSpinBox:focus {
                border: 1px solid #03DAC6;
            }
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                width: 20px;
                background-color: #333;
                border: none;
            }
            QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
                background-color: #444;
            }
            QDoubleSpinBox::up-arrow {
                image: url(assets/arrow_up.svg);
                width: 12px;
                height: 12px;
            }
            QDoubleSpinBox::down-arrow {
                image: url(assets/arrow_down.svg);
                width: 12px;
                height: 12px;
            }
        """
