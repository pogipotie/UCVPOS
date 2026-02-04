from PyQt6.QtWidgets import (
    QCalendarWidget, QSpinBox, QComboBox, QWidget, QHBoxLayout, QToolButton
)
from PyQt6.QtCore import Qt, QDate

class YearDropdownCalendarWidget(QCalendarWidget):
    """
    Custom Calendar Widget that replaces the Year SpinBox with a QComboBox.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.year_combo = QComboBox(self)
        self.year_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        self._setup_combo_style()
        
        # Populate years
        current_year = QDate.currentDate().year()
        self.start_year = current_year - 10
        self.end_year = current_year + 10
        years = [str(y) for y in range(self.start_year, self.end_year + 1)]
        self.year_combo.addItems(years)
        
        # Add to layout immediately
        nav_bar = self.findChild(QWidget, "qt_calendar_navigationbar")
        if nav_bar and nav_bar.layout():
             # Add to end of layout
             nav_bar.layout().addWidget(self.year_combo)
        
        # Connect signals
        self.year_combo.currentIndexChanged.connect(self._on_combo_changed)
        self.currentPageChanged.connect(self._on_page_changed)
        
        # Initial sync
        self._update_combo_from_calendar()

    def showEvent(self, event):
        """Ensure we hide standard controls every time visualization changes"""
        super().showEvent(event)
        # Delay slightly to let Qt setup its native widgets
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(0, self._cleanup_widgets)

    def _cleanup_widgets(self):
        """Aggressively hide standard year controls"""
        nav_bar = self.findChild(QWidget, "qt_calendar_navigationbar")
        if not nav_bar: return
        
        # Iterate all children of the nav bar layout
        layout = nav_bar.layout()
        if not layout: return

        # We look for children to hide
        for child in nav_bar.children():
            # Hide SpinBoxes (Year editor)
            if isinstance(child, QSpinBox):
                child.hide()
            
            # Hide Year ToolButton (if in that mode)
            if isinstance(child, QToolButton):
                # Standard year button usually is 'qt_calendar_yearbutton' or has year text
                if child.objectName() == "qt_calendar_yearbutton" or child.text().isdigit():
                     child.hide()

    def _setup_combo_style(self):
        self.year_combo.setStyleSheet("""
            QComboBox {
                background-color: #2C2C2C;
                border: 1px solid #333333;
                border-radius: 4px;
                padding: 4px 10px;
                min-width: 80px;
                color: #FFFFFF;
                font-weight: bold;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 0px;
                border-top-right-radius: 3px; 
                border-bottom-right-radius: 3px;
            }
            QComboBox::down-arrow {
                width: 0; 
                height: 0;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #03DAC6; /* Custom arrow */
                margin-right: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: #2C2C2C;
                color: #FFFFFF;
                selection-background-color: #03DAC6;
                selection-color: #000000;
                outline: none;
            }
        """)

    def _update_combo_from_calendar(self):
        year = self.yearShown()
        index = self.year_combo.findText(str(year))
        if index != -1:
            self.year_combo.blockSignals(True)
            self.year_combo.setCurrentIndex(index)
            self.year_combo.blockSignals(False)

    def _on_combo_changed(self, index):
        year_text = self.year_combo.currentText()
        if year_text.isdigit():
            year = int(year_text)
            self.setCurrentPage(year, self.monthShown())

    def _on_page_changed(self, year, month):
        self._update_combo_from_calendar()
