# Global UI Style Configuration for Security Ops Logger
# Designed for accessibility and 1080p displays

from PyQt6.QtGui import QFont

# Font configurations
class Fonts:
    TITLE = QFont("Segoe UI", 20, QFont.Weight.DemiBold)
    SUBTITLE = QFont("Segoe UI", 16, QFont.Weight.DemiBold)
    LABEL = QFont("Segoe UI", 12, QFont.Weight.Medium)
    NORMAL = QFont("Segoe UI", 11)
    BUTTON = QFont("Segoe UI", 11, QFont.Weight.Medium)
    BUTTON_LARGE = QFont("Segoe UI", 12, QFont.Weight.Medium)
    STATUS = QFont("Segoe UI", 10)

# Color scheme - Professional monochrome
class Colors:
    PRIMARY = "#4a4a4a"      # Medium gray
    SUCCESS = "#5a5a5a"      # Light gray
    WARNING = "#6a6a6a"      # Lighter gray
    DANGER = "#7a7a7a"       # Even lighter gray
    INFO = "#404040"         # Dark gray
    SECONDARY = "#505050"    # Gray
    DARK = "#1a1a1a"         # Very dark gray
    LIGHT = "#e0e0e0"        # Light gray
    
    # Specific use colors - all monochrome
    EMAIL = "#4a4a4a"
    PHONE = "#4a4a4a"
    RADIO = "#4a4a4a"
    EVERBRIDGE = "#4a4a4a"
    EVENT = "#4a4a4a"
    STATS = "#4a4a4a"

# Button styles - Professional dark theme
def get_button_style(color=None, height=45):
    return f"""
        QPushButton {{
            background-color: #1a1a1a;
            color: #e0e0e0;
            border: 1px solid #333333;
            border-radius: 4px;
            padding: 8px 16px;
            font-size: 11px;
            font-weight: 500;
            min-height: {height}px;
        }}
        QPushButton:hover {{
            background-color: #262626;
            border: 1px solid #4a4a4a;
        }}
        QPushButton:pressed {{
            background-color: #333333;
        }}
        QPushButton:disabled {{
            background-color: #1a1a1a;
            color: #4a4a4a;
        }}
    """

# Professional button style - monochrome only
def get_colored_button_style(color=None, height=45):
    return get_button_style(color, height)

# Input field styles - Professional dark theme
INPUT_STYLE = """
    QLineEdit, QTextEdit {
        padding: 8px;
        background-color: #1a1a1a;
        color: #e0e0e0;
        border: 1px solid #333333;
        border-radius: 4px;
        font-size: 11px;
    }
    QLineEdit:focus, QTextEdit:focus {
        border: 1px solid #5a5a5a;
        background-color: #1f1f1f;
    }
    QLineEdit:read-only {
        background-color: #141414;
        color: #808080;
        border: 1px solid #262626;
    }
"""

# Table styles - Professional dark theme
TABLE_STYLE = """
    QTableWidget {
        font-size: 11px;
        background-color: #141414;
        color: #e0e0e0;
        gridline-color: #262626;
        alternate-background-color: #1a1a1a;
    }
    QTableWidget::item {
        padding: 8px;
    }
    QTableWidget::item:selected {
        background-color: #333333;
        color: #ffffff;
    }
    QHeaderView::section {
        background-color: #1a1a1a;
        color: #e0e0e0;
        padding: 10px;
        font-weight: 600;
        font-size: 11px;
        border: 1px solid #262626;
    }
"""

# Tab widget styles - Professional dark theme
TAB_STYLE = """
    QTabWidget::tab-bar {
        alignment: center;
    }
    QTabBar::tab {
        padding: 10px 20px;
        margin: 2px;
        font-size: 11px;
        background-color: #1a1a1a;
        color: #808080;
        border: 1px solid #262626;
        border-bottom: none;
    }
    QTabBar::tab:selected {
        background-color: #0d0d0d;
        color: #e0e0e0;
        font-weight: 500;
        border-bottom: 2px solid #5a5a5a;
    }
    QTabBar::tab:hover {
        background-color: #1f1f1f;
        color: #e0e0e0;
    }
"""

# Common dialog settings
def setup_window(window, title, width=900, height=700):
    """Apply common window settings"""
    window.setWindowTitle(title)
    window.setMinimumSize(width, height)
    window.showMaximized()
    
    # Set application-wide font
    window.setFont(Fonts.NORMAL)

# Accessibility helpers
def make_accessible(widget, description):
    """Add accessibility features to a widget"""
    widget.setToolTip(description)
    widget.setWhatsThis(description)

# Message box styles
def show_success(parent, message):
    """Show styled success message"""
    from PyQt6.QtWidgets import QMessageBox
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Icon.Information)
    msg.setWindowTitle("Success")
    msg.setText(message)
    msg.setFont(Fonts.NORMAL)
    # Don't override theme styling for message boxes
    msg.exec()

def show_error(parent, message):
    """Show styled error message"""
    from PyQt6.QtWidgets import QMessageBox
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Icon.Critical)
    msg.setWindowTitle("Error")
    msg.setText(message)
    msg.setFont(Fonts.NORMAL)
    # Don't override theme styling for message boxes
    msg.exec()

# Dropdown/ComboBox styles - Professional dark theme
DROPDOWN_STYLE = """
    QComboBox {
        padding: 8px;
        background-color: #1a1a1a;
        color: #e0e0e0;
        border: 1px solid #333333;
        border-radius: 4px;
        font-size: 11px;
        min-height: 35px;
    }
    QComboBox:focus {
        border: 1px solid #5a5a5a;
        background-color: #1f1f1f;
    }
    QComboBox::drop-down {
        width: 20px;
        background-color: #262626;
        border: none;
    }
    QComboBox::down-arrow {
        width: 10px;
        height: 10px;
    }
    QComboBox QAbstractItemView {
        background-color: #1a1a1a;
        color: #e0e0e0;
        font-size: 11px;
        padding: 5px;
        selection-background-color: #333333;
    }
"""

# List widget styles - Professional dark theme
LIST_STYLE = """
    QListWidget {
        font-size: 11px;
        padding: 5px;
        background-color: #141414;
        color: #e0e0e0;
        border: 1px solid #333333;
        border-radius: 4px;
    }
    QListWidget::item {
        padding: 8px;
        border-bottom: 1px solid #262626;
    }
    QListWidget::item:selected {
        background-color: #333333;
        color: #ffffff;
    }
    QListWidget::item:hover {
        background-color: #1f1f1f;
    }
"""