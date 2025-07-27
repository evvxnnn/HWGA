# Theme definitions for Security Ops Logger

DARK_THEME = """
/* Main Window and General */
QMainWindow {
    background-color: #1e1e1e;
    color: #ffffff;
}

QWidget {
    background-color: #1e1e1e;
    color: #ffffff;
    font-family: Arial, sans-serif;
}

/* Labels */
QLabel {
    color: #ffffff;
    background-color: transparent;
}

/* Buttons */
QPushButton {
    background-color: #2d2d30;
    color: #ffffff;
    border: 1px solid #3e3e42;
    padding: 8px;
    border-radius: 5px;
}

QPushButton:hover {
    background-color: #3e3e42;
    border: 1px solid #007ACC;
}

QPushButton:pressed {
    background-color: #007ACC;
}

QPushButton:disabled {
    background-color: #2d2d30;
    color: #656565;
    border: 1px solid #3e3e42;
}

/* Input Fields */
QLineEdit, QTextEdit {
    background-color: #2d2d30;
    color: #ffffff;
    border: 1px solid #3e3e42;
    padding: 8px;
    border-radius: 5px;
    selection-background-color: #007ACC;
}

QLineEdit:focus, QTextEdit:focus {
    border: 2px solid #007ACC;
}

QLineEdit:read-only {
    background-color: #252526;
    color: #cccccc;
}

/* ComboBox / Dropdowns */
QComboBox {
    background-color: #2d2d30;
    color: #ffffff;
    border: 1px solid #3e3e42;
    padding: 8px;
    border-radius: 5px;
}

QComboBox:hover {
    border: 1px solid #007ACC;
}

QComboBox::drop-down {
    border: none;
    background-color: #3e3e42;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #ffffff;
    margin-right: 5px;
}

QComboBox QAbstractItemView {
    background-color: #2d2d30;
    color: #ffffff;
    selection-background-color: #007ACC;
    border: 1px solid #3e3e42;
}

/* Tables */
QTableWidget {
    background-color: #252526;
    color: #ffffff;
    gridline-color: #3e3e42;
    selection-background-color: #007ACC;
    alternate-background-color: #2d2d30;
}

QTableWidget::item {
    padding: 8px;
}

QTableWidget::item:selected {
    background-color: #007ACC;
    color: #ffffff;
}

QHeaderView::section {
    background-color: #2d2d30;
    color: #ffffff;
    padding: 10px;
    border: 1px solid #3e3e42;
    font-weight: bold;
}

/* Lists */
QListWidget {
    background-color: #252526;
    color: #ffffff;
    border: 1px solid #3e3e42;
    selection-background-color: #007ACC;
}

QListWidget::item {
    padding: 8px;
    border-bottom: 1px solid #3e3e42;
}

QListWidget::item:selected {
    background-color: #007ACC;
    color: #ffffff;
}

QListWidget::item:hover {
    background-color: #3e3e42;
}

/* Tab Widget */
QTabWidget::pane {
    border: 1px solid #3e3e42;
    background-color: #1e1e1e;
}

QTabBar::tab {
    background-color: #2d2d30;
    color: #ffffff;
    padding: 10px 20px;
    margin-right: 2px;
    border: 1px solid #3e3e42;
}

QTabBar::tab:selected {
    background-color: #007ACC;
    color: #ffffff;
}

QTabBar::tab:hover {
    background-color: #3e3e42;
}

/* Group Box */
QGroupBox {
    color: #ffffff;
    border: 2px solid #3e3e42;
    border-radius: 5px;
    margin-top: 10px;
    padding-top: 10px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px 0 5px;
}

/* Scroll Bars */
QScrollBar:vertical {
    background-color: #2d2d30;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #3e3e42;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #007ACC;
}

QScrollBar:horizontal {
    background-color: #2d2d30;
    height: 12px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background-color: #3e3e42;
    border-radius: 6px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #007ACC;
}

/* Check Box */
QCheckBox {
    color: #ffffff;
    spacing: 10px;
}

QCheckBox::indicator {
    width: 20px;
    height: 20px;
    background-color: #2d2d30;
    border: 1px solid #3e3e42;
    border-radius: 3px;
}

QCheckBox::indicator:checked {
    background-color: #007ACC;
    border: 1px solid #007ACC;
}

QCheckBox::indicator:hover {
    border: 1px solid #007ACC;
}

/* Radio Button */
QRadioButton {
    color: #ffffff;
    spacing: 10px;
}

QRadioButton::indicator {
    width: 20px;
    height: 20px;
    background-color: #2d2d30;
    border: 1px solid #3e3e42;
    border-radius: 10px;
}

QRadioButton::indicator:checked {
    background-color: #007ACC;
    border: 1px solid #007ACC;
}

/* Progress Bar */
QProgressBar {
    background-color: #2d2d30;
    border: 1px solid #3e3e42;
    border-radius: 5px;
    text-align: center;
    color: #ffffff;
}

QProgressBar::chunk {
    background-color: #007ACC;
    border-radius: 5px;
}

/* Status Bar */
QStatusBar {
    background-color: #007ACC;
    color: #ffffff;
}

/* Menu Bar */
QMenuBar {
    background-color: #2d2d30;
    color: #ffffff;
}

QMenuBar::item {
    padding: 5px 10px;
    background-color: transparent;
}

QMenuBar::item:selected {
    background-color: #007ACC;
}

QMenu {
    background-color: #2d2d30;
    color: #ffffff;
    border: 1px solid #3e3e42;
}

QMenu::item:selected {
    background-color: #007ACC;
}

/* Tool Tips */
QToolTip {
    background-color: #2d2d30;
    color: #ffffff;
    border: 1px solid #007ACC;
    padding: 5px;
}

/* Message Box */
QMessageBox {
    background-color: #1e1e1e;
    color: #ffffff;
}

QMessageBox QPushButton {
    min-width: 80px;
    min-height: 30px;
}

/* Dialog */
QDialog {
    background-color: #1e1e1e;
    color: #ffffff;
}

/* Splitter */
QSplitter::handle {
    background-color: #3e3e42;
}

QSplitter::handle:hover {
    background-color: #007ACC;
}

/* Slider */
QSlider::groove:horizontal {
    background-color: #2d2d30;
    height: 6px;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background-color: #007ACC;
    width: 16px;
    height: 16px;
    margin: -5px 0;
    border-radius: 8px;
}

QSlider::handle:horizontal:hover {
    background-color: #1ba1e2;
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