"""
Responsive UI Utilities - Screen-aware sizing for dialogs and widgets
"""
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt


def get_responsive_size(width_percent: float, height_percent: float, 
                       min_width: int = None, min_height: int = None,
                       max_width: int = None, max_height: int = None) -> tuple:
    """
    Calculate responsive dialog/widget size based on screen dimensions.
    
    Args:
        width_percent: Desired width as percentage of screen width (0.0-1.0)
        height_percent: Desired height as percentage of screen height (0.0-1.0)
        min_width: Minimum width in pixels (optional)
        min_height: Minimum height in pixels (optional)
        max_width: Maximum width in pixels (optional)
        max_height: Maximum height in pixels (optional)
    
    Returns:
        Tuple of (width, height) in pixels, constrained by min/max values
    """
    # Get primary screen geometry
    screen = QApplication.primaryScreen().availableGeometry()
    
    # Calculate responsive dimensions
    width = int(screen.width() * width_percent)
    height = int(screen.height() * height_percent)
    
    # Apply constraints
    if min_width is not None:
        width = max(width, min_width)
    if min_height is not None:
        height = max(height, min_height)
    if max_width is not None:
        width = min(width, max_width)
    if max_height is not None:
        height = min(height, max_height)
    
    return (width, height)


def apply_responsive_sizing(widget: QWidget, width_percent: float, height_percent: float,
                           min_width: int = None, min_height: int = None,
                           max_width: int = None, max_height: int = None) -> None:
    """
    Apply responsive sizing to a widget/dialog.
    
    Args:
        widget: The QWidget or QDialog to resize
        width_percent: Desired width as percentage of screen width
        height_percent: Desired height as percentage of screen height
        min_width: Minimum width constraint
        min_height: Minimum height constraint
        max_width: Maximum width constraint
        max_height: Maximum height constraint
    """
    width, height = get_responsive_size(width_percent, height_percent, 
                                       min_width, min_height, max_width, max_height)
    widget.resize(width, height)
    widget.setMinimumSize(min_width or 300, min_height or 200)
