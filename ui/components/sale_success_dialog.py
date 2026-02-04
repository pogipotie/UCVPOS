from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QFrame, QHBoxLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

class SaleSuccessDialog(QDialog):
    """Custom dialog for sale completion with premium UI"""
    
    def __init__(self, sale_id: int, total: float, paid: float, change: float, items: list, parent=None,
                 discount_type: str = None, discount_amount: float = 0.0, original_total: float = None):
        super().__init__(parent)
        self.sale_id = sale_id
        self.total = total  # This is the final_total if discounted
        self.paid = paid
        self.change = change
        self.items = items
        self.discount_type = discount_type
        self.discount_amount = discount_amount
        self.original_total = original_total or total
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Sale Complete")
        # Responsive sizing
        screen = self.screen().availableGeometry()
        width = int(screen.width() * 0.35)  # Slightly narrower
        height = int(screen.height() * 0.80) # Slightly shorter
        
        # Constraints
        width = max(450, min(width, 600))
        height = max(650, min(height, 850))
        
        self.resize(width, height)
        self.setMinimumSize(450, 650)
        self.setModal(True)
        self.setStyleSheet("background-color: #1A1A2E; color: white;")
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15) # Reduced spacing
        layout.setContentsMargins(20, 20, 20, 20) # Reduced margins
        
        # Header Section (Icon + Title) - Centered Vertical
        header_layout = QVBoxLayout()
        header_layout.setSpacing(5)
        
        # Icon
        import os
        from PyQt6.QtGui import QPixmap
        
        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "shopping.png")
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path).scaled(60, 60, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            icon_label.setPixmap(pixmap)
        else:
            icon_label.setText("✅")
            icon_label.setStyleSheet("font-size: 40px;")
        
        # Title "Sale Completed"
        title_label = QLabel("Sale Completed")
        title_label.setStyleSheet("color: #00BF6D; font-size: 24px; font-weight: bold; letter-spacing: 1px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        id_label = QLabel(f"Transaction #{self.sale_id}")
        id_label.setStyleSheet("color: #8899A6; font-size: 13px;")
        id_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addWidget(id_label)
        
        layout.addLayout(header_layout)
        
        # Details Card
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #1F2B47;
                border: 1px solid #2D3A5A;
                border-radius: 0px;
                padding: 15px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(10) # Tight spacing
        
        # Show discount or VAT breakdown
        if self.discount_type:
            # SC/PWD Discount Header
            discount_header = QLabel(f"{'SENIOR CITIZEN' if self.discount_type == 'SC' else 'PWD'} SALE")
            discount_header.setStyleSheet("color: #FFB800; font-size: 13px; font-weight: bold;")
            discount_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.addWidget(discount_header)
            
            vat_exempt = self.original_total / 1.12
            self.add_row(card_layout, "Original Price", f"₱{self.original_total:,.2f}")
            self.add_row(card_layout, "VAT Exempt", f"₱{vat_exempt:,.2f}")
            self.add_row(card_layout, "Less 20% Discount", f"-₱{self.discount_amount:,.2f}", highlight=True)
            
            # Divider
            div1 = QFrame()
            div1.setFrameShape(QFrame.Shape.HLine)
            div1.setStyleSheet("background-color: #2D3A5A; max-height: 1px;")
            card_layout.addWidget(div1)
            
            self.add_row(card_layout, "Total Amount", f"₱{self.total:,.2f}")
        else:
            # Normal VAT breakdown
            from services.settings_service import settings_service
            tax_rate = settings_service.get('financial', 'tax_rate') or 12.0
            vat_amount = self.total - (self.total / (1 + tax_rate / 100)) if tax_rate > 0 else 0
            net_amount = self.total - vat_amount
            
            self.add_row(card_layout, "Net Amount", f"₱{net_amount:,.2f}")
            self.add_row(card_layout, f"VAT ({tax_rate:.0f}%)", f"₱{vat_amount:,.2f}")
            
            # Divider
            div1 = QFrame()
            div1.setFrameShape(QFrame.Shape.HLine)
            div1.setStyleSheet("background-color: #2D3A5A; max-height: 1px;")
            card_layout.addWidget(div1)
            
            self.add_row(card_layout, "Total Amount", f"₱{self.total:,.2f}")
        
        self.add_row(card_layout, "Cash Received", f"₱{self.paid:,.2f}")
        
        layout.addWidget(card)
        
        # Change Section (Compact)
        change_frame = QFrame()
        change_frame.setStyleSheet("background-color: #1F2B47; border-radius: 0px; padding: 10px;")
        change_layout = QHBoxLayout(change_frame)
        
        change_lbl = QLabel("CHANGE DUE:")
        change_lbl.setStyleSheet("color: #B0B0B0; font-size: 16px; font-weight: bold;")
        
        change_val = QLabel(f"₱{self.change:,.2f}")
        change_val.setStyleSheet("color: #FFB800; font-size: 32px; font-weight: bold;") # Reduced from 48px
        
        change_layout.addWidget(change_lbl)
        change_layout.addStretch()
        change_layout.addWidget(change_val)
        
        layout.addWidget(change_frame)
        
        layout.addStretch()
        
        # Done Button
        self.done_btn = QPushButton("PRINT & DONE (Enter)")
        self.done_btn.setMinimumHeight(50) # Reduced from 60
        self.done_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.done_btn.clicked.connect(self.print_and_close)
        self.done_btn.setStyleSheet("""
            QPushButton {
                background-color: #00BF6D;
                color: #FFFFFF;
                border: none;
                border-radius: 0px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #00D67A; }
            QPushButton:pressed { background-color: #00A860; }
        """)
        layout.addWidget(self.done_btn)
        
        # Auto focus
        self.done_btn.setFocus()

    def print_and_close(self):
        """Simulate printing then close"""
        self.generate_pdf_receipt()
        self.accept()
        
    def generate_pdf_receipt(self):
        """Generate a PDF receipt using ReportLab"""
        from reportlab.lib.units import mm
        from reportlab.pdfgen import canvas
        from datetime import datetime
        import os
        
        from services.settings_service import settings_service
        settings = settings_service.get_all()
        store = settings.get('store_info', {})
        financial = settings.get('financial', {})
        currency = 'P'  # Use 'P' for PDF (Helvetica doesn't support ₱)
        
        # Ensure directory exists
        receipt_dir = "receipts"
        if not os.path.exists(receipt_dir):
            os.makedirs(receipt_dir)
            
        timestamp = datetime.now()
        filename = f"{receipt_dir}/receipt_{self.sale_id}_{int(timestamp.timestamp())}.pdf"
        
        # Layout setup (Thermal printer paper width approx 80mm)
        # Use variable height based on item count to avoid cutting off
        base_height = 150 * mm
        item_height = 8 * mm
        page_height = base_height + (len(self.items) * item_height)
        page_width = 80 * mm
        
        c = canvas.Canvas(filename, pagesize=(page_width, page_height))
        
        # Helpers
        y = page_height - 10 * mm
        left_margin = 4 * mm
        right_margin = 4 * mm
        
        def draw_centered(text, y_pos, font="Helvetica-Bold", size=10):
            c.setFont(font, size)
            width = c.stringWidth(text, font, size)
            c.drawString((page_width - width) / 2, y_pos, text)
            return y_pos - size - 2
            
        def draw_line(y_pos):
            c.setLineWidth(0.5)
            c.line(left_margin, y_pos, page_width - right_margin, y_pos)
            return y_pos - 4 * mm
            
        # Header
        y = draw_centered(store.get('name', 'Pharmacy POS'), y, size=12)
        y = draw_centered(store.get('address', ''), y, "Helvetica", 8)
        y = draw_centered(f"Tel: {store.get('phone', '')}", y, "Helvetica", 8)
        y -= 2 * mm
        y = draw_line(y)
        
        # Transaction Info
        c.setFont("Helvetica", 8)
        c.drawString(left_margin, y, f"TXN: #{self.sale_id}")
        c.drawRightString(page_width - right_margin, y, timestamp.strftime("%Y-%m-%d %H:%M"))
        y -= 5 * mm
        y = draw_line(y)
        
        # Items Header
        c.setFont("Helvetica-Bold", 8)
        c.drawString(left_margin, y, "ITEM")
        c.drawRightString(page_width - right_margin - 30*mm, y, "QTY")
        c.drawRightString(page_width - right_margin, y, "TOTAL")
        y -= 4 * mm
        
        # Items List
        c.setFont("Helvetica", 8)
        for item in self.items:
            # Handle item name (truncate if too long)
            name = item.product.name
            if len(name) > 20: 
                name = name[:18] + ".."
            
            c.drawString(left_margin, y, name)
            
            # Qty
            c.drawRightString(page_width - right_margin - 30*mm, y, str(item.quantity))
            
            # Total
            c.drawRightString(page_width - right_margin, y, f"{item.subtotal:,.2f}")
            
            y -= 5 * mm
            
        y = draw_line(y)
        
        # VAT breakdown for receipt
        tax_rate = settings_service.get('financial', 'tax_rate') or 12.0
        vat_amount = self.total - (self.total / (1 + tax_rate / 100)) if tax_rate > 0 else 0
        net_amount = self.total - vat_amount
        
        # Net Amount
        c.setFont("Helvetica", 9)
        c.drawString(left_margin + 15*mm, y, "NET:")
        c.drawRightString(page_width - right_margin, y, f"{currency}{net_amount:,.2f}")
        y -= 4 * mm
        
        # VAT
        c.drawString(left_margin + 15*mm, y, f"VAT ({tax_rate:.0f}%):")
        c.drawRightString(page_width - right_margin, y, f"{currency}{vat_amount:,.2f}")
        y -= 5 * mm
        
        # Totals
        c.setFont("Helvetica-Bold", 10)
        c.drawString(left_margin + 15*mm, y, "TOTAL:")
        c.drawRightString(page_width - right_margin, y, f"{currency}{self.total:,.2f}")
        y -= 5 * mm
        
        c.setFont("Helvetica", 9)
        c.drawString(left_margin + 15*mm, y, "CASH:")
        c.drawRightString(page_width - right_margin, y, f"{currency}{self.paid:,.2f}")
        y -= 5 * mm
        
        c.setFont("Helvetica-Bold", 11)
        c.drawString(left_margin + 15*mm, y, "CHANGE:")
        c.drawRightString(page_width - right_margin, y, f"{currency}{self.change:,.2f}")
        y -= 8 * mm
        
        # Footer
        y = draw_line(y)
        draw_centered(store.get('header_text', 'THANK YOU FOR YOUR PURCHASE!'), y, "Helvetica", 8)
        draw_centered("Please come again.", y - 4*mm, "Helvetica", 8)
        
        c.save()
        
        try:
            os.startfile(os.path.abspath(filename))
        except:
            pass
        
    def add_row(self, layout, label, value, highlight=False):
        row = QHBoxLayout()
        lbl = QLabel(label)
        if highlight:
            lbl.setStyleSheet("color: #FFB800; font-size: 16px;")
        else:
            lbl.setStyleSheet("color: #B0B0B0; font-size: 16px;")
        val = QLabel(value)
        if highlight:
            val.setStyleSheet("color: #FFB800; font-size: 16px; font-weight: bold;")
        else:
            val.setStyleSheet("color: #FFFFFF; font-size: 16px; font-weight: bold;")
        val.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        row.addWidget(lbl)
        row.addStretch()
        row.addWidget(val)
        layout.addLayout(row)

