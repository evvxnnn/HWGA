from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QTextEdit,
    QPushButton, QMessageBox, QMainWindow, QStatusBar,
    QHBoxLayout, QComboBox, QGroupBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QShortcut, QKeySequence
from datetime import datetime
from database import insert_everbridge_log
from ui.styles import *
from config import SITE_CODES

# Common Everbridge alert templates
ALERT_TEMPLATES = {
    "Select Template...": "",
    "Fire Alarm": "Fire alarm activated at {site}. Please evacuate immediately via nearest exit.",
    "Severe Weather": "Severe weather alert for {site}. All personnel move to designated shelter areas.",
    "Security Incident": "Security incident reported at {site}. Shelter in place until all clear.",
    "Power Outage": "Power outage affecting {site}. Emergency lighting activated.",
    "Medical Emergency": "Medical emergency at {site}. First responders en route.",
    "System Test": "This is a test of the Everbridge alert system for {site}. No action required.",
    "All Clear": "All clear at {site}. Normal operations may resume.",
}

class EverbridgePanel(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Everbridge Alert Log Entry")
        self.setMinimumSize(900, 700)
        self.showMaximized()
        
        self.init_ui()
        self.setup_shortcuts()
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready to log Everbridge alert")

    def init_ui(self):
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 30, 40, 30)

        # Title with alert icon
        title_layout = QHBoxLayout()
        title_layout.addStretch()
        
        title = QLabel("⚠️ Everbridge Alert Logger")
        title.setFont(Fonts.TITLE)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"color: {Colors.DANGER}; margin-bottom: 30px;")
        title_layout.addWidget(title)
        
        title_layout.addStretch()
        layout.addLayout(title_layout)

        # Alert info
        info_label = QLabel("Log mass notification alerts sent through Everbridge")
        info_label.setFont(Fonts.NORMAL)
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("color: #666; margin-bottom: 20px;")
        layout.addWidget(info_label)

        # Timestamp section
        time_group = QGroupBox("Alert Time")
        time_group.setFont(Fonts.LABEL)
        time_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #F44336;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 0 10px 0 10px;
            }
        """)
        time_layout = QHBoxLayout()
        
        self.timestamp_field = QLineEdit(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.timestamp_field.setFont(Fonts.NORMAL)
        self.timestamp_field.setStyleSheet(INPUT_STYLE)
        self.timestamp_field.setMinimumHeight(45)
        make_accessible(self.timestamp_field, "Time alert was sent")
        time_layout.addWidget(self.timestamp_field)
        
        now_btn = QPushButton("🕐 Current Time")
        now_btn.setFont(Fonts.BUTTON)
        now_btn.setStyleSheet(get_button_style(Colors.INFO, 45))
        now_btn.clicked.connect(self.set_current_time)
        make_accessible(now_btn, "Set to current time")
        time_layout.addWidget(now_btn)
        
        time_group.setLayout(time_layout)
        layout.addWidget(time_group)

        # Site Code section
        site_layout = QHBoxLayout()
        site_label = QLabel("Site Code:")
        site_label.setFont(Fonts.LABEL)
        site_label.setMinimumWidth(150)
        site_layout.addWidget(site_label)
        
        self.site_code_field = QComboBox()
        self.site_code_field.setEditable(True)
        self.site_code_field.addItems(SITE_CODES)
        self.site_code_field.setFont(Fonts.NORMAL)
        self.site_code_field.setStyleSheet(DROPDOWN_STYLE)
        self.site_code_field.setMinimumHeight(45)
        make_accessible(self.site_code_field, "Enter or select the site code")
        site_layout.addWidget(self.site_code_field)
        site_layout.addStretch()
        layout.addLayout(site_layout)

        # Template selection
        template_layout = QHBoxLayout()
        template_label = QLabel("Template:")
        template_label.setFont(Fonts.LABEL)
        template_label.setMinimumWidth(150)
        template_layout.addWidget(template_label)
        
        self.template_dropdown = QComboBox()
        self.template_dropdown.addItems(ALERT_TEMPLATES.keys())
        self.template_dropdown.setFont(Fonts.NORMAL)
        self.template_dropdown.setStyleSheet(DROPDOWN_STYLE)
        self.template_dropdown.setMinimumHeight(45)
        self.template_dropdown.currentTextChanged.connect(self.apply_template)
        make_accessible(self.template_dropdown, "Select a message template")
        template_layout.addWidget(self.template_dropdown)
        template_layout.addStretch()
        layout.addLayout(template_layout)

        # Message section
        message_group = QGroupBox("Alert Message")
        message_group.setFont(Fonts.LABEL)
        message_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #F44336;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 0 10px 0 10px;
            }
        """)
        message_layout = QVBoxLayout()
        
        self.message_box = QTextEdit()
        self.message_box.setFont(Fonts.NORMAL)
        self.message_box.setStyleSheet("""
            QTextEdit {
                padding: 15px;
                border: 1px solid #DDD;
                border-radius: 5px;
                font-size: 16px;
                line-height: 1.5;
            }
            QTextEdit:focus {
                border: 2px solid #F44336;
                background-color: #FFEBEE;
            }
        """)
        self.message_box.setPlaceholderText("Enter the alert message that was sent...")
        self.message_box.setMinimumHeight(200)
        make_accessible(self.message_box, "Enter the full alert message")
        message_layout.addWidget(self.message_box)
        
        # Character count
        self.char_count_label = QLabel("0 characters")
        self.char_count_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.char_count_label.setStyleSheet("color: #666; font-style: italic;")
        self.message_box.textChanged.connect(self.update_char_count)
        message_layout.addWidget(self.char_count_label)
        
        message_group.setLayout(message_layout)
        layout.addWidget(message_group)

        # Quick action buttons
        quick_layout = QHBoxLayout()
        quick_layout.addStretch()
        
        clear_btn = QPushButton("🗑️ Clear Message")
        clear_btn.setFont(Fonts.BUTTON)
        clear_btn.setStyleSheet(get_button_style("#757575", 45))
        clear_btn.clicked.connect(self.clear_message)
        quick_layout.addWidget(clear_btn)
        
        quick_layout.addStretch()
        layout.addLayout(quick_layout)

        layout.addStretch()

        # Save button
        self.save_btn = QPushButton("💾 Save Alert Log (Ctrl+S)")
        self.save_btn.setFont(Fonts.BUTTON_LARGE)
        self.save_btn.setStyleSheet(get_button_style(Colors.SUCCESS, 70))
        self.save_btn.clicked.connect(self.save_log)
        make_accessible(self.save_btn, "Save the Everbridge alert log")
        layout.addWidget(self.save_btn)

        central_widget.setLayout(layout)

    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        QShortcut(QKeySequence("Ctrl+S"), self, self.save_log)
        QShortcut(QKeySequence("Escape"), self, self.close)
        QShortcut(QKeySequence("Ctrl+T"), self, self.set_current_time)
        QShortcut(QKeySequence("Ctrl+Shift+C"), self, self.clear_message)

    def set_current_time(self):
        """Set timestamp to current time"""
        self.timestamp_field.setText(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.status_bar.showMessage("Timestamp updated to current time")

    def apply_template(self, template_name):
        """Apply selected template to message"""
        if template_name in ALERT_TEMPLATES and template_name != "Select Template...":
            template = ALERT_TEMPLATES[template_name]
            site_code = self.site_code_field.currentText()
            message = template.format(site=site_code if site_code else "[SITE]")
            self.message_box.setText(message)
            self.status_bar.showMessage(f"Applied template: {template_name}")

    def update_char_count(self):
        """Update character count label"""
        count = len(self.message_box.toPlainText())
        self.char_count_label.setText(f"{count} characters")
        
        # Change color if message is very long
        if count > 500:
            self.char_count_label.setStyleSheet("color: #F44336; font-style: italic;")
        elif count > 300:
            self.char_count_label.setStyleSheet("color: #FF9800; font-style: italic;")
        else:
            self.char_count_label.setStyleSheet("color: #666; font-style: italic;")

    def clear_message(self):
        """Clear the message box"""
        reply = QMessageBox.question(
            self,
            "Clear Message",
            "Are you sure you want to clear the message?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.message_box.clear()
            self.template_dropdown.setCurrentIndex(0)

    def save_log(self):
        site_code = self.site_code_field.currentText().strip()
        message = self.message_box.toPlainText().strip()
        timestamp = self.timestamp_field.text()

        # Validation
        if not site_code:
            show_error(self, "Please enter a site code")
            self.site_code_field.setFocus()
            return

        if not message:
            show_error(self, "Please enter the alert message")
            self.message_box.setFocus()
            return

        try:
            insert_everbridge_log(site_code, message, timestamp)
            
            # Show success with preview
            preview = message[:100] + "..." if len(message) > 100 else message
            show_success(self, f"Everbridge alert log saved!\n\nSite: {site_code}\nMessage: {preview}")
            self.close()
        except Exception as e:
            show_error(self, f"Error saving log: {str(e)}")