# Theme definitions for Security Ops Logger

DARK_THEME = """
/* Main Window and General */
QMainWindow {
    background-color: #0d0d0d;
    color: #e0e0e0;
}

QWidget {
    background-color: #0d0d0d;
    color: #e0e0e0;
    font-family: 'Segoe UI', Arial, sans-serif;
}

/* Labels */
QLabel {
    color: #e0e0e0;
    background-color: transparent;
}

/* Buttons */
QPushButton {
    background-color: #1a1a1a;
    color: #e0e0e0;
    border: 1px solid #333333;
    padding: 10px 16px;
    border-radius: 4px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #262626;
    border: 1px solid #4a4a4a;
}

QPushButton:pressed {
    background-color: #333333;
    border: 1px solid #4a4a4a;
}

QPushButton:disabled {
    background-color: #1a1a1a;
    color: #4a4a4a;
    border: 1px solid #262626;
}

/* Input Fields */
QLineEdit, QTextEdit {
    background-color: #1a1a1a;
    color: #e0e0e0;
    border: 1px solid #333333;
    padding: 8px;
    border-radius: 4px;
    selection-background-color: #404040;
}

QLineEdit:focus, QTextEdit:focus {
    border: 1px solid #5a5a5a;
    background-color: #1f1f1f;
}

QLineEdit:read-only {
    background-color: #141414;
    color: #808080;
}

/* ComboBox / Dropdowns */
QComboBox {
    background-color: #1a1a1a;
    color: #e0e0e0;
    border: 1px solid #333333;
    padding: 8px;
    border-radius: 4px;
}

QComboBox:hover {
    border: 1px solid #4a4a4a;
    background-color: #1f1f1f;
}

QComboBox::drop-down {
    border: none;
    background-color: #262626;
}

QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 4px solid #808080;
    margin-right: 5px;
}

QComboBox QAbstractItemView {
    background-color: #1a1a1a;
    color: #e0e0e0;
    selection-background-color: #333333;
    border: 1px solid #333333;
}

/* Tables */
QTableWidget {
    background-color: #141414;
    color: #e0e0e0;
    gridline-color: #262626;
    selection-background-color: #333333;
    alternate-background-color: #1a1a1a;
}

QTableWidget::item {
    padding: 8px;
}

/* Ensure alternate rows maintain dark background in dark mode */
QTableWidget::item:alternate {
    background-color: #1a1a1a;
    color: #e0e0e0;
}

QTableWidget::item:selected {
    background-color: #333333;
    color: #ffffff;
}

QHeaderView::section {
    background-color: #1a1a1a;
    color: #e0e0e0;
    padding: 10px;
    border: 1px solid #262626;
    font-weight: 600;
}

/* Lists */
QListWidget {
    background-color: #141414;
    color: #e0e0e0;
    border: 1px solid #333333;
    selection-background-color: #333333;
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

/* Tab Widget */
QTabWidget::pane {
    border: 1px solid #333333;
    background-color: #0d0d0d;
}

QTabBar::tab {
    background-color: #1a1a1a;
    color: #808080;
    padding: 10px 20px;
    margin-right: 2px;
    border: 1px solid #262626;
    border-bottom: none;
}

QTabBar::tab:selected {
    background-color: #0d0d0d;
    color: #e0e0e0;
    border-bottom: 2px solid #5a5a5a;
}

QTabBar::tab:hover {
    background-color: #1f1f1f;
    color: #e0e0e0;
}

/* Group Box */
QGroupBox {
    color: #e0e0e0;
    border: 1px solid #333333;
    border-radius: 4px;
    margin-top: 10px;
    padding-top: 10px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px 0 5px;
    background-color: #0d0d0d;
}

/* Scroll Bars */
QScrollBar:vertical {
    background-color: #141414;
    width: 10px;
    border: none;
}

QScrollBar::handle:vertical {
    background-color: #333333;
    border-radius: 5px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #4a4a4a;
}

QScrollBar:horizontal {
    background-color: #141414;
    height: 10px;
    border: none;
}

QScrollBar::handle:horizontal {
    background-color: #333333;
    border-radius: 5px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #4a4a4a;
}

QScrollBar::add-line, QScrollBar::sub-line {
    border: none;
    background: none;
}

/* Check Box */
QCheckBox {
    color: #e0e0e0;
    spacing: 10px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    background-color: #1a1a1a;
    border: 1px solid #333333;
    border-radius: 3px;
}

QCheckBox::indicator:checked {
    background-color: #4a4a4a;
    border: 1px solid #5a5a5a;
}

QCheckBox::indicator:hover {
    border: 1px solid #5a5a5a;
    background-color: #1f1f1f;
}

/* Radio Button */
QRadioButton {
    color: #e0e0e0;
    spacing: 10px;
}

QRadioButton::indicator {
    width: 18px;
    height: 18px;
    background-color: #1a1a1a;
    border: 1px solid #333333;
    border-radius: 9px;
}

QRadioButton::indicator:checked {
    background-color: #4a4a4a;
    border: 1px solid #5a5a5a;
}

QRadioButton::indicator:hover {
    border: 1px solid #5a5a5a;
    background-color: #1f1f1f;
}

/* Progress Bar */
QProgressBar {
    background-color: #1a1a1a;
    border: 1px solid #333333;
    border-radius: 4px;
    text-align: center;
    color: #e0e0e0;
    height: 20px;
}

QProgressBar::chunk {
    background-color: #4a4a4a;
    border-radius: 3px;
}

/* Status Bar */
QStatusBar {
    background-color: #1a1a1a;
    color: #808080;
    border-top: 1px solid #262626;
    padding: 4px;
}

/* Menu Bar */
QMenuBar {
    background-color: #141414;
    color: #e0e0e0;
    border-bottom: 1px solid #262626;
}

QMenuBar::item {
    padding: 6px 12px;
    background-color: transparent;
}

QMenuBar::item:selected {
    background-color: #262626;
}

QMenu {
    background-color: #1a1a1a;
    color: #e0e0e0;
    border: 1px solid #333333;
}

QMenu::item {
    padding: 8px 20px;
}

QMenu::item:selected {
    background-color: #262626;
}

QMenu::separator {
    height: 1px;
    background-color: #333333;
    margin: 4px 10px;
}

/* Tool Tips */
QToolTip {
    background-color: #262626;
    color: #e0e0e0;
    border: 1px solid #4a4a4a;
    padding: 6px;
    border-radius: 3px;
}

/* Message Box */
QMessageBox {
    background-color: #0d0d0d;
    color: #e0e0e0;
}

QMessageBox QLabel {
    color: #e0e0e0;
}

QMessageBox QPushButton {
    background-color: #1a1a1a;
    color: #e0e0e0;
    border: 1px solid #333333;
    padding: 8px 16px;
    min-width: 80px;
    min-height: 30px;
    border-radius: 4px;
}

QMessageBox QPushButton:hover {
    background-color: #262626;
    border: 1px solid #4a4a4a;
}

QMessageBox QPushButton:pressed {
    background-color: #333333;
}

/* Dialog */
QDialog {
    background-color: #0d0d0d;
    color: #e0e0e0;
}

/* Splitter */
QSplitter::handle {
    background-color: #262626;
    width: 2px;
    height: 2px;
}

QSplitter::handle:hover {
    background-color: #4a4a4a;
}

/* Specific button overrides - Professional monochrome style */
QPushButton[style*="background-color"] {
    /* Override inline styles to maintain consistent theme */
    background-color: #1a1a1a !important;
    color: #e0e0e0 !important;
    border: 1px solid #333333 !important;
}

QPushButton[style*="background-color"]:hover {
    background-color: #262626 !important;
    border: 1px solid #4a4a4a !important;
}

QPushButton[style*="background-color"]:pressed {
    background-color: #333333 !important;
}
"""

LIGHT_THEME = """
/* Reset to default light theme */
QMainWindow {
    background-color: #FAFAFA;
}

QWidget {
    background-color: #FAFAFA;
    color: #000000;
}

QPushButton {
    background-color: #f0f0f0;
    color: #000000;
    border: 1px solid #d0d0d0;
}

QLineEdit, QTextEdit {
    background-color: #ffffff;
    color: #000000;
    border: 1px solid #d0d0d0;
}

QComboBox {
    background-color: #ffffff;
    color: #000000;
    border: 1px solid #d0d0d0;
}

QTableWidget {
    background-color: #ffffff;
    color: #000000;
    gridline-color: #d0d0d0;
}

QListWidget {
    background-color: #ffffff;
    color: #000000;
    border: 1px solid #d0d0d0;
}
"""

def get_theme_stylesheet(theme_name="dark"):
    """Get the stylesheet for the specified theme"""
    if theme_name == "dark":
        return DARK_THEME
    else:
        return LIGHT_THEME