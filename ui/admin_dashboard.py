"""
Admin Dashboard - Visual analytics and system overview
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QGridLayout, QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt, QPointF, QSize
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QLinearGradient, QPainterPath, QFont

from repositories.sales_repo import sales_repo
from services.inventory_service import inventory_service
from services.auth_service import auth_service
from datetime import date
import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class StatCard(QFrame):
    """A card displaying a single statistic with a color accent"""
    def __init__(self, title, value, color="#03DAC6"):
        super().__init__()
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #1E1E1E;
                border: 1px solid #333333;
                border-radius: 0px;
                border-left: 4px solid {color};
            }}
        """)
        
        layout = QVBoxLayout(self)
        
        # Header
        header = QHBoxLayout()
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("color: #B3B3B3; font-size: 13px; font-weight: 600; text-transform: uppercase;")
        header.addWidget(title_lbl)
        header.addStretch() # Push title to left, unnecessary if we had icon, but good for cleanliness
        layout.addLayout(header)
        
        # Value
        self.value_lbl = QLabel(str(value))
        self.value_lbl.setStyleSheet("color: #FFFFFF; font-size: 28px; font-weight: bold;")
        layout.addWidget(self.value_lbl)
        
    def update_value(self, new_value):
        self.value_lbl.setText(str(new_value))


class SalesChart(FigureCanvas):
    """Custom widget to draw sales trend using Matplotlib"""
    def __init__(self, parent=None):
        self.figure = Figure(figsize=(6, 4), facecolor='#1E1E1E')
        super().__init__(self.figure)
        self.setParent(parent)
        
        # Styling
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor('#1E1E1E')
        
        # Remove border around canvas if possible, or style parent
        self.setStyleSheet("background-color: #1E1E1E; border-radius: 0px;")
        
        self.data = []
        self.plot_sales()

    def set_data(self, data):
        self.data = data
        self.plot_sales()

    def plot_sales(self):
        self.ax.clear()
        self.ax.set_facecolor('#1E1E1E')
        
        # Style axes for dark theme (always, even with no data)
        self.ax.tick_params(axis='x', colors='white')
        self.ax.tick_params(axis='y', colors='white')
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['bottom'].set_color('white')
        self.ax.spines['left'].set_color('white')
        
        # Data
        if not self.data:
            self.ax.text(0.5, 0.5, 'No Data', color='#888888', ha='center', va='center', fontsize=14)
            self.draw()
            return
            
        dates = [d['date'][-5:] for d in self.data] # MM-DD
        values = [d['total'] for d in self.data]
        
        # Horizontal Bar Chart with thin bars
        bar_height = 0.15  # Very thin bars
        bars = self.ax.barh(dates, values, color='#03DAC6', height=bar_height)
        
        # Title
        self.ax.set_title("Sales Trend (Last 7 Days)", color='white', fontsize=12, pad=20)
        
        # Set large margins so single bar doesn't fill entire chart
        self.ax.margins(y=0.8)
        
        # Add value labels
        for bar in bars:
            width = bar.get_width()
            self.ax.text(width, bar.get_y() + bar.get_height()/2, 
                         f'  ₱{width:,.0f}', 
                         ha='left', va='center', color='white', fontsize=9)
                         
        self.figure.tight_layout()
        self.draw()


class TopProductsList(QFrame):
    """List showing top products"""
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background-color: #1E1E1E;
                border: 1px solid #333333;
                border-radius: 0px;
            }
        """)
        
        self.layout = QVBoxLayout(self)
        
        lbl = QLabel("Top Selling Products")
        lbl.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")
        self.layout.addWidget(lbl)
        
        self.list_layout = QVBoxLayout()
        self.layout.addLayout(self.list_layout)
        self.layout.addStretch()
        
    def set_data(self, products):
        # Clear old
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        max_qty = max([p['quantity'] for p in products]) if products else 1
        
        for p in products:
            row = QWidget()
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 5, 0, 5)
            
            name = QLabel(p['name'])
            name.setStyleSheet("color: #DDD; font-size: 13px;")
            row_layout.addWidget(name)
            
            # Simple bar
            bar_container = QWidget()
            bar_container.setFixedHeight(8)
            bar_layout = QHBoxLayout(bar_container)
            bar_layout.setContentsMargins(0,0,0,0)
            
            bar_width_pct = int((p['quantity'] / max_qty) * 100)
            
            bar = QFrame()
            bar.setStyleSheet("background-color: #BB86FC; border-radius: 4px;")
            # To set width percentage we can use stretch, but explicit is easier for pure visual
            # Since layout management is tricky for arbitrary widths without subclassing, 
            # let's just use text for now or fixed width logic.
            # Actually, let's use a ProgressBar styled.
            
            from PyQt6.QtWidgets import QProgressBar
            progress = QProgressBar()
            progress.setMaximum(max_qty)
            progress.setValue(p['quantity'])
            progress.setFixedHeight(8)
            progress.setTextVisible(False)
            progress.setStyleSheet("""
                QProgressBar {
                    background-color: #2C2C2C;
                    border: none;
                    border-radius: 0px;
                }
                QProgressBar::chunk {
                    background-color: #BB86FC;
                    border-radius: 0px;
                }
            """)
            
            row_layout.addWidget(progress, 1)
            
            qty = QLabel(str(p['quantity']))
            qty.setStyleSheet("color: #BB86FC; font-weight: bold;")
            row_layout.addWidget(qty)
            
            self.list_layout.addWidget(row)

class AdminDashboard(QWidget):
    """Main Dashboard Screen"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.refresh_data()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        header = QLabel("Dashboard")
        header.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        layout.addWidget(header)
        
        # Top Stats Row
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        self.card_sales = StatCard("Sales Today", "₱0.00", "#03DAC6")
        self.card_profit = StatCard("Profit Today", "₱0.00", "#4CAF50")  # Green for profit
        self.card_transactions = StatCard("Transactions", "0", "#BB86FC")
        self.card_low_stock = StatCard("Low Stock", "0", "#FFB800")
        self.card_expired = StatCard("Expired", "0", "#CF6679")
        
        stats_layout.addWidget(self.card_sales)
        stats_layout.addWidget(self.card_profit)
        stats_layout.addWidget(self.card_transactions)
        stats_layout.addWidget(self.card_low_stock)
        stats_layout.addWidget(self.card_expired)
        
        layout.addLayout(stats_layout)
        
        # Middle Row (Charts)
        middle_layout = QHBoxLayout()
        middle_layout.setSpacing(20)
        
        self.sales_chart = SalesChart()
        middle_layout.addWidget(self.sales_chart, 2) # 66% width
        
        self.top_products = TopProductsList()
        middle_layout.addWidget(self.top_products, 1) # 33% width
        
        layout.addLayout(middle_layout, 1) # Stretch to fill
        
    def refresh_data(self):
        # 1. Today's Stats
        today = date.today()
        summary = sales_repo.get_daily_summary(today)
        self.card_sales.update_value(f"₱{summary['total_sales']:.2f}")
        self.card_transactions.update_value(summary['total_transactions'])
        
        # 2. Profit Today
        profit_data = sales_repo.get_daily_profit(today)
        self.card_profit.update_value(f"₱{profit_data['profit']:.2f}")
        
        # 2. Alerts
        low_stock_count = len(inventory_service.get_low_stock_products())
        self.card_low_stock.update_value(low_stock_count)
        
        expired_count = len(inventory_service.get_expired_products())
        self.card_expired.update_value(expired_count)
        
        # 3. Chart Data
        trend = sales_repo.get_sales_trend(7)
        self.sales_chart.set_data(trend)
        
        # 4. Top Products
        top = sales_repo.get_top_products(5)
        self.top_products.set_data(top)
