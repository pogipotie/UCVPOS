"""
Void Details Dialog - Premium styled dialog for viewing void details
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import os
from ui.responsive_utils import apply_responsive_sizing


class VoidDetailsDialog(QDialog):
    """Custom styled dialog for viewing void sale details"""
    
    def __init__(self, sale, parent=None):
        super().__init__(parent)
        self.sale = sale
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Void Details")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        apply_responsive_sizing(self, 0.25, 0.38, 320, 300, 480, 480)
        
        # Main Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Container Card - NO border-radius
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #1A1A2E;
                border: 1px solid #2D3A5A;
                border-radius: 0px;
            }
        """)
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(12)
        container_layout.setContentsMargins(30, 30, 30, 30)
        
        # Icon from assets
        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_path = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "remove.png")
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path).scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            icon_label.setPixmap(pixmap)
        else:
            icon_label.setText("🗑️")
            icon_label.setStyleSheet("font-size: 40px; border: none; background: transparent;")
        container_layout.addWidget(icon_label)
        
        # Title
        title = QLabel(f"Sale #{self.sale.id} - Voided")
        title.setStyleSheet("""
            color: #CF6679; 
            font-size: 18px; 
            font-weight: bold; 
            border: none; 
            background: transparent;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(title)
        
        # Details Frame
        details_frame = QFrame()
        details_frame.setStyleSheet("""
            QFrame {
                background-color: #252540;
                border: 1px solid #333355;
                border-radius: 0px;
            }
        """)
        details_layout = QVBoxLayout(details_frame)
        details_layout.setContentsMargins(15, 15, 15, 15)
        details_layout.setSpacing(10)
        
        # Amount
        amount_row = QHBoxLayout()
        amount_lbl = QLabel("Amount:")
        amount_lbl.setStyleSheet("color: #888; font-size: 12px; border: none; background: transparent;")
        amount_val = QLabel(f"₱{self.sale.total_amount:,.2f}")
        amount_val.setStyleSheet("color: #03DAC6; font-size: 14px; font-weight: bold; border: none; background: transparent;")
        amount_row.addWidget(amount_lbl)
        amount_row.addStretch()
        amount_row.addWidget(amount_val)
        details_layout.addLayout(amount_row)
        
        # Reason
        reason = getattr(self.sale, 'void_reason', None) or "No reason provided"
        reason_lbl = QLabel("Reason:")
        reason_lbl.setStyleSheet("color: #888; font-size: 12px; border: none; background: transparent;")
        details_layout.addWidget(reason_lbl)
        
        reason_val = QLabel(reason)
        reason_val.setWordWrap(True)
        reason_val.setStyleSheet("color: #FFB800; font-size: 13px; border: none; background: transparent; padding-left: 5px;")
        details_layout.addWidget(reason_val)
        
        # Voided At
        voided_at = getattr(self.sale, 'voided_at', None) or "Unknown"
        voided_row = QHBoxLayout()
        voided_lbl = QLabel("Voided At:")
        voided_lbl.setStyleSheet("color: #888; font-size: 12px; border: none; background: transparent;")
        voided_val = QLabel(str(voided_at))
        voided_val.setStyleSheet("color: white; font-size: 12px; border: none; background: transparent;")
        voided_row.addWidget(voided_lbl)
        voided_row.addStretch()
        voided_row.addWidget(voided_val)
        details_layout.addLayout(voided_row)
        
        container_layout.addWidget(details_frame)
        container_layout.addStretch()
        
        # Close Button
        close_btn = QPushButton("Close")
        close_btn.setMinimumHeight(40)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #333;
                color: white;
                border: none;
                border-radius: 0px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover { background-color: #444; }
        """)
        close_btn.clicked.connect(self.accept)
        container_layout.addWidget(close_btn)
        
        layout.addWidget(container)
