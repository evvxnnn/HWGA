# Global UI Style Configuration for Security Ops Logger
# Designed for accessibility and 1080p displays

from PyQt6.QtGui import QFont

# Font configurations
class Fonts:
    TITLE = QFont("Arial", 24, QFont.Weight.Bold)
    SUBTITLE = QFont("Arial", 18, QFont.Weight.Bold)
    LABEL = QFont("Arial", 14, QFont.Weight.Bold)
    NORMAL = QFont("Arial", 14)
    BUTTON = QFont("Arial", 16)
    BUTTON_LARGE = QFont("Arial", 16, QFont.Weight.Bold)
    STATUS = QFont("Arial", 12)

# Color scheme
class Colors:
    PRIMARY = "#2196F3"      # Blue
    SUCCESS = "#4CAF50"      # Green
    WARNING = "#FF9800"      # Orange
    DANGER = "#F44336"       # Red
    INFO = "#00BCD4"         # Cyan
    SECONDARY = "#9C27B0"    # Purple
    DARK = "#212121"         # Dark gray
    LIGHT = "#F5F5F5"        # Light gray
    
    # Specific use colors
    EMAIL = "#2196F3"
    PHONE = "#4CAF50"
    RADIO = "#FF9800"
    EVERBRIDGE = "#F44336"
    EVENT = "#7E57C2"
    STATS = "#00897B"

# Button styles
def get_button_style(color, height=60):
    return f"""
        QPushButton {{
            background-color: {color};
            color: white;
            border: none;
            border-radius: 10px;
            padding: 10px;
            font-size: 16px;
            font-weight: bold;
            min-height: {height}px;
        }}
        QPushButton:hover {{
            background-color: {color}CC;
        }}
        QPushButton:pressed {{
            background-color: {color}99;
        }}
        QPushButton:disabled {{
            background-color: #CCCCCC;
            color: #666666;
        }}
    """

# Input field styles
INPUT_STYLE = """
    QLineEdit, QTextEdit {
        padding: 10px;
        border: 2px solid #2196F3;
        border-radius: 5px;
        font-size: 14px;
    }
    QLineEdit:focus, QTextEdit:focus {
        border: 2px solid #1976D2;
        background-color: #E3F2FD;
    }
    QLineEdit:read-only {
        background-color: #F5F5F5;
        border: 2px solid #DDDDDD;
    }
"""

# Table styles
TABLE_STYLE = """
    QTableWidget {
        font-size: 14px;
        gridline-color: #DDDDDD;
        alternate-background-color: #F5F5F5;
    }
    QTableWidget::item {
        padding: 8px;
    }
    QTableWidget::item:selected {
        background-color: #2196F3;
        color: white;
    }
    QHeaderView::section {
        background-color: #1976D2;
        color: white;
        padding: 10px;
        font-weight: bold;
        font-size: 14px;
    }
"""

# Tab widget styles
TAB_STYLE = """
    QTabWidget::tab-bar {
        alignment: center;
    }
    QTabBar::tab {
        padding: 12px 24px;
        margin: 2px;
        font-size: 14px;
        background-color: #E0E0E0;
    }
    QTabBar::tab:selected {
        background-color: #2196F3;
        color: white;
        font-weight: bold;
    }
    QTabBar::tab:hover {
        background-color: #BBDEFB;
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
    msg.setStyleSheet("""
        QMessageBox {
            background-color: white;
        }
        QPushButton {
            min-width: 100px;
            min-height: 40px;
            font-size: 14px;
        }
    """)
    msg.exec()

def show_error(parent, message):
    """Show styled error message"""
    from PyQt6.QtWidgets import QMessageBox
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Icon.Critical)
    msg.setWindowTitle("Error")
    msg.setText(message)
    msg.setFont(Fonts.NORMAL)
    msg.setStyleSheet("""
        QMessageBox {
            background-color: white;
        }
        QPushButton {
            min-width: 100px;
            min-height: 40px;
            font-size: 14px;
        }
    """)
    msg.exec()

# Dropdown/ComboBox styles
DROPDOWN_STYLE = """
    QComboBox {
        padding: 10px;
        border: 2px solid #2196F3;
        border-radius: 5px;
        font-size: 14px;
        min-height: 40px;
    }
    QComboBox:focus {
        border: 2px solid #1976D2;
        background-color: #E3F2FD;
    }
    QComboBox::drop-down {
        width: 30px;
    }
    QComboBox::down-arrow {
        width: 12px;
        height: 12px;
    }
    QComboBox QAbstractItemView {
        font-size: 14px;
        padding: 5px;
    }
"""

# List widget styles
LIST_STYLE = """
    QListWidget {
        font-size: 14px;
        padding: 5px;
        border: 2px solid #DDDDDD;
        border-radius: 5px;
    }
    QListWidget::item {
        padding: 10px;
        border-bottom: 1px solid #EEEEEE;
    }
    QListWidget::item:selected {
        background-color: #2196F3;
        color: white;
    }
    QListWidget::item:hover {
        background-color: #BBDEFB;
    }
"""