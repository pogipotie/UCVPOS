"""
UI Styles - Modern Premium Dark Pharmacy Theme
"""

# Premium Color Palette (Material Design / Cyberpunk inspired but professional)
COLORS = {
    'background': '#121212',       # Very dark grey, almost black
    'surface': '#1E1E1E',          # Slightly lighter for cards/panels
    'surface_highlight': '#2C2C2C', # Hover states
    'primary': '#03DAC6',          # Vibrant Teal for primary actions
    'primary_dark': '#018786',     # Darker teal for pressed states
    'secondary': '#BB86FC',        # Soft Purple for secondary highlights
    'accent': '#03DAC6',           # Same as primary for consistency
    'error': '#CF6679',            # Soft red for errors
    'success': '#00E676',          # Bright green for success/money
    'warning': '#FFB74D',          # Orange for warnings
    'text': '#FFFFFF',             # High emphasis text
    'text_secondary': '#B3B3B3',   # Medium emphasis text
    'border': '#333333',           # Subtle borders
    'input_bg': '#2C2C2C',         # Input fields background
}

# Main application stylesheet
MAIN_STYLESHEET = """
/* Global Reset & Base */
QMainWindow, QWidget {
    background-color: #121212;
    color: #FFFFFF;
    font-family: 'Segoe UI', 'Roboto', Helvetica, Arial, sans-serif;
    font-size: 14px;
    outline: none;
}

/* -------------------------------------------------------------------------
   Buttons - Modern, Rounded, Interactive
   ------------------------------------------------------------------------- */
QPushButton {
    background-color: #1E1E1E;
    color: #03DAC6;
    border: 1px solid #03DAC6;
    border-radius: 0px;
    padding: 10px 20px;
    font-weight: 600;
    font-size: 14px;
}

QPushButton:hover {
    background-color: rgba(3, 218, 198, 0.1);
}

QPushButton:pressed {
    background-color: rgba(3, 218, 198, 0.2);
}

QPushButton:disabled {
    border-color: #333333;
    color: #666666;
    background-color: transparent;
}

/* Primary Action Button (Solid Teal) */
QPushButton#primaryButton {
    background-color: #03DAC6;
    color: #000000;
    border: none;
    font-weight: 700;
}

QPushButton#primaryButton:hover {
    background-color: #05E5D0;
}

QPushButton#primaryButton:pressed {
    background-color: #018786;
}

/* Success Button (Money/Checkout) */
QPushButton#successButton {
    background-color: #00E676;
    color: #000000;
    border: none;
    font-weight: 700;
    font-size: 16px;
}

QPushButton#successButton:hover {
    background-color: #00FF85;
}

QPushButton#successButton:pressed {
    background-color: #00B359;
}

/* Danger/Destructive Button (Red) */
QPushButton#dangerButton {
    background-color: transparent;
    border: 1px solid #CF6679;
    color: #CF6679;
}

QPushButton#dangerButton:hover {
    background-color: rgba(207, 102, 121, 0.1);
}

QPushButton#dangerButton:pressed {
    background-color: rgba(207, 102, 121, 0.2);
}

/* -------------------------------------------------------------------------
   Inputs - Clean, Focus States
   ------------------------------------------------------------------------- */
QLineEdit, QSpinBox, QDoubleSpinBox, QDateEdit {
    background-color: #2C2C2C;
    color: #FFFFFF;
    border: 1px solid #333333;
    border-radius: 0px;
    padding: 8px 12px;
    font-size: 14px;
    selection-background-color: #BB86FC;
    selection-color: #000000;
}

QDateEdit {
    min-width: 130px;
}

QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus {
    border: 1px solid #BB86FC;
    background-color: #333333;
}

QLineEdit:disabled, QSpinBox:disabled {
    background-color: #1E1E1E;
    color: #666666;
    border-color: #333333;
}

/* Special Inputs */
QLineEdit#barcodeInput {
    font-size: 16px;
    border: 1px solid #03DAC6;
    background-color: #1A1A1A;
}

QLineEdit#barcodeInput:focus {
    border: 2px solid #03DAC6;
}

/* -------------------------------------------------------------------------
   Tables - Readable, Alternating, Hover
   ------------------------------------------------------------------------- */
QTableWidget {
    background-color: #1E1E1E;
    color: #E0E0E0;
    border: 1px solid #333333;
    gridline-color: #333333;
    selection-background-color: rgba(187, 134, 252, 0.2);
    selection-color: #FFFFFF;
    font-size: 14px;
}

QTableWidget::item {
    padding: 8px 5px;
    border-bottom: 1px solid #282828;
}

QHeaderView::section {
    background-color: #2C2C2C;
    color: #B3B3B3;
    padding: 8px;
    border: none;
    border-bottom: 1px solid #333333;
    font-weight: 600;
    text-transform: uppercase;
    font-size: 12px;
}

/* -------------------------------------------------------------------------
   Scrollbars - Minimalist
   ------------------------------------------------------------------------- */
QScrollBar:vertical {
    border: none;
    background: #121212;
    width: 10px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #424242;
    min-height: 20px;
    border-radius: 0px;
}

QScrollBar::handle:vertical:hover {
    background: #616161;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* -------------------------------------------------------------------------
   Cards & Frames
   ------------------------------------------------------------------------- */
QFrame#cardFrame {
    background-color: #1E1E1E;
    border: 1px solid #333333;
    border-radius: 0px;
}

/* Highlighted sections (Total amount, etc) */
QFrame#highlightFrame {
    background-color: #252525;
    border: 1px solid #333333;
    border-radius: 0px;
}

QGroupBox {
    border: 1px solid #333333;
    border-radius: 0px;
    margin-top: 20px;
    font-weight: bold;
    color: #B3B3B3;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
}

/* -------------------------------------------------------------------------
   Labels & Typography
   ------------------------------------------------------------------------- */
QLabel {
    color: #FFFFFF;
    background-color: transparent;
}

/* Headers */
QLabel#titleLabel {
    font-size: 24px;
    font-weight: 300; /* Light weight for modern look */
    color: #FFFFFF;
    letter-spacing: 0.5px;
}

QLabel#subtitleLabel {
    font-size: 14px;
    color: #B3B3B3;
}

/* Money/Total displays */
QLabel#totalLabel {
    font-family: 'Consolas', 'Monaco', monospace; /* Monospaced for numbers */
    font-size: 36px;
    font-weight: 700;
    color: #00E676;
}

/* -------------------------------------------------------------------------
   Tabs & Navigation
   ------------------------------------------------------------------------- */
QTabWidget::pane {
    border: 1px solid #333333;
    background: #1E1E1E;
    border-radius: 0px;
}

QTabBar::tab {
    background: #121212;
    color: #999999;
    padding: 10px 20px;
    border-radius: 0px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background: #1E1E1E;
    color: #03DAC6;
    border-bottom: 2px solid #03DAC6;
}

QTabBar::tab:hover:!selected {
    background: #1A1A1A;
    color: #CCCCCC;
}

/* -------------------------------------------------------------------------
   Sidebar
   ------------------------------------------------------------------------- */
QFrame#sidebar {
    background-color: #181818;
    border-right: 1px solid #252525;
}

/* Navigation Buttons in Sidebar */
/* (See main_window.py for specifics, but global styles here) */

/* -------------------------------------------------------------------------
   Status Bar
   ------------------------------------------------------------------------- */
QStatusBar {
    background-color: #121212;
    color: #666666;
    border-top: 1px solid #252525;
}
/* -------------------------------------------------------------------------
   Calendar Widget (Premium UI)
   ------------------------------------------------------------------------- */
QCalendarWidget QWidget {
    background-color: #1A1A1A;
    color: #FFFFFF;
}

/* Navigation Bar (Header) */
QCalendarWidget QWidget#qt_calendar_navigationbar {
    background-color: #121212;
    border-bottom: 1px solid #333333;
    min-height: 45px; /* Comfortable touch/click target */
}

/* Month/Year Buttons & Arrows */
QCalendarWidget QToolButton {
    color: #E0E0E0;
    background-color: transparent;
    border: none;
    border-radius: 0px;
    margin: 3px;
    padding: 6px;
    font-weight: 600;
    font-size: 14px;
}

QCalendarWidget QToolButton:hover {
    background-color: #2C2C2C;
    color: #FFFFFF;
}

QCalendarWidget QToolButton:pressed {
    background-color: #03DAC6;
    color: #000000;
}

QCalendarWidget QToolButton::menu-indicator {
    image: none;
}

/* Year SpinBox */
QCalendarWidget QSpinBox {
    background-color: #2C2C2C;
    border: 1px solid #333333;
    border-radius: 0px;
    color: #FFFFFF;
    selection-background-color: #03DAC6;
    selection-color: #000000;
    min-height: 30px;
    min-width: 90px;
    margin-right: 5px;
    padding-right: 25px;
    font-weight: bold;
}

QCalendarWidget QSpinBox::up-button, QCalendarWidget QSpinBox::down-button {
    subcontrol-origin: padding;
    width: 22px;
    background-color: #383838;
    border: none;
}

QCalendarWidget QSpinBox::up-button {
    subcontrol-position: top right;
    border-top-right-radius: 0px;
    margin-bottom: 1px; /* Separation */
}

QCalendarWidget QSpinBox::down-button {
    subcontrol-position: bottom right;
    border-bottom-right-radius: 0px;
    margin-top: 1px;
}

QCalendarWidget QSpinBox::up-button:hover, QCalendarWidget QSpinBox::down-button:hover {
    background-color: #03DAC6;
}

/* Day Grid */
QCalendarWidget QAbstractItemView:enabled {
    background-color: #1A1A1A;
    color: #E0E0E0;
    selection-background-color: #03DAC6;
    selection-color: #000000;
    outline: none;
    font-size: 13px;
    gridline-color: transparent;
}

QCalendarWidget QAbstractItemView:disabled {
    color: #444444;
}
"""

# Contextual Styles (for rows/alerts)
# Using transparency to blend with row background
LOW_STOCK_STYLE = "color: #FFB74D; font-weight: bold;" 
EXPIRED_STYLE = "color: #CF6679; font-weight: bold; text-decoration: line-through;"
OUT_OF_STOCK_STYLE = "color: #666666; font-style: italic;"

class Styles:
    """Helper class for common styles"""
    DARK_THEME = MAIN_STYLESHEET
    
    INPUT_STYLE = """
        QLineEdit {
            background-color: #2C2C2C;
            color: #FFFFFF;
            border: 1px solid #333333;
            border-radius: 0px;
            padding: 8px 12px;
            font-size: 14px;
        }
        QLineEdit:focus {
            border: 1px solid #03DAC6;
        }
    """
    
    BTN_PRIMARY = """
        QPushButton {
            background-color: #03DAC6;
            color: #000000;
            border: none;
            font-weight: bold;
            padding: 10px;
        }
        QPushButton:hover { background-color: #05E5D0; }
        QPushButton:pressed { background-color: #018786; }
    """
    
    BTN_SECONDARY = """
        QPushButton {
            background-color: transparent;
            border: 1px solid #666666;
            color: #E0E0E0;
            padding: 10px;
        }
        QPushButton:hover { border-color: #999999; color: #FFFFFF; }
        QPushButton:pressed { background-color: #333333; }
    """

