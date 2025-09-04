from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QTextEdit,
    QPushButton, QMessageBox, QMainWindow, QStatusBar,
    QHBoxLayout, QComboBox, QGroupBox,
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QShortcut, QKeySequence
from datetime import datetime
from database import insert_everbridge_log
from log_manager import log_manager
import pandas as pd
from ui.help_utils import HelpButton, get_help_training_id
from ui.styles import (
    Fonts, Colors,
    INPUT_STYLE, TABLE_STYLE, LIST_STYLE, DROPDOWN_STYLE,
    get_button_style, make_accessible,
    show_error, show_success
)
from app_settings import app_settings
from config import SITE_CODES as DEFAULT_SITE_CODES

# Get site codes from settings or use defaults
def get_site_codes():
    dropdown_options = app_settings.get("dropdown_options", {})
    return dropdown_options.get("site_codes", DEFAULT_SITE_CODES)

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
        
        # Status bar - initialize BEFORE init_ui
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready to log Everbridge alert")
        
        self.init_ui()
        self.setup_shortcuts()

    def init_ui(self):
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 30, 40, 30)

        # Add help button in top right
        header_layout = QHBoxLayout()
        header_layout.addStretch()
        help_btn = HelpButton("Everbridge Alert", get_help_training_id("everbridge"), self)
        header_layout.addWidget(help_btn)
        layout.addLayout(header_layout)
        
        # Title
        title = QLabel("Everbridge Alert Logger")
        title.setFont(Fonts.TITLE)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #e0e0e0; margin-bottom: 30px;")
        layout.addWidget(title)

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
        
        # Auto-fill timestamp if enabled in settings
        if app_settings.get("auto_timestamp", True):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            timestamp = ""
        
        self.timestamp_field = QLineEdit(timestamp)
        self.timestamp_field.setFont(Fonts.NORMAL)
        self.timestamp_field.setStyleSheet(INPUT_STYLE)
        self.timestamp_field.setMinimumHeight(45)
        make_accessible(self.timestamp_field, "Time alert was sent")
        time_layout.addWidget(self.timestamp_field)
        
        now_btn = QPushButton("Current Time")
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
        self.site_code_field.addItems(get_site_codes())
        # Set default site if configured
        default_site = app_settings.get("default_site", "")
        if default_site:
            self.site_code_field.setCurrentText(default_site)
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
        
        clear_btn = QPushButton("Clear Message")
        clear_btn.setFont(Fonts.BUTTON)
        clear_btn.setStyleSheet(get_button_style("#757575", 45))
        clear_btn.clicked.connect(self.clear_message)
        quick_layout.addWidget(clear_btn)
        
        quick_layout.addStretch()
        layout.addLayout(quick_layout)

        layout.addStretch()

        # Save button
        self.save_btn = QPushButton("Save Alert Log (Ctrl+S)")
        self.save_btn.setFont(Fonts.BUTTON_LARGE)
        self.save_btn.setStyleSheet(get_button_style(Colors.SUCCESS, 70))
        self.save_btn.clicked.connect(self.save_log)
        make_accessible(self.save_btn, "Save the Everbridge alert log")
        layout.addWidget(self.save_btn)

        # Create main tab widget for better organization
        self.main_tabs = QTabWidget()
        self.main_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #333333;
                background-color: #0d0d0d;
                margin-top: -1px;
            }
            QTabBar::tab {
                padding: 10px 20px;
                background-color: #1a1a1a;
                color: #808080;
                border: 1px solid #262626;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #0d0d0d;
                color: #e0e0e0;
                border-bottom: 2px solid #5a5a5a;
            }
        """)
        
        # Input Tab - contains existing form
        input_widget = QWidget()
        input_widget.setLayout(layout)
        self.main_tabs.addTab(input_widget, "Log New Alert")
        
        # View Logs Tab
        log_widget = QWidget()
        log_layout = QVBoxLayout()
        log_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header with controls
        controls_layout = QHBoxLayout()
        
        # Filter
        controls_layout.addWidget(QLabel("Filter:"))
        self.log_filter = QLineEdit()
        self.log_filter.setPlaceholderText("Search logs...")
        self.log_filter.textChanged.connect(self.filter_logs)
        self.log_filter.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                background-color: #1a1a1a;
                color: #e0e0e0;
                border: 1px solid #333333;
                border-radius: 4px;
                max-width: 300px;
            }
        """)
        controls_layout.addWidget(self.log_filter)
        
        controls_layout.addStretch()
        
        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_recent_logs)
        refresh_btn.setFixedWidth(100)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a1a1a;
                color: #e0e0e0;
                border: 1px solid #333333;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #262626;
            }
        """)
        controls_layout.addWidget(refresh_btn)
        
        # Export button
        export_btn = QPushButton("Export")
        export_btn.clicked.connect(self.export_logs)
        export_btn.setFixedWidth(100)
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a1a1a;
                color: #e0e0e0;
                border: 1px solid #333333;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #262626;
            }
        """)
        controls_layout.addWidget(export_btn)
        
        log_layout.addLayout(controls_layout)
        
        # Table for logs
        self.log_table = QTableWidget()
        self.log_table.setStyleSheet("""
            QTableWidget {
                background-color: #141414;
                color: #e0e0e0;
                gridline-color: #262626;
                alternate-background-color: #1a1a1a;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #333333;
            }
            QHeaderView::section {
                background-color: #1a1a1a;
                color: #e0e0e0;
                padding: 8px;
                border: 1px solid #262626;
                font-weight: 600;
            }
        """)
        self.log_table.setAlternatingRowColors(True)
        self.log_table.horizontalHeader().setStretchLastSection(True)
        self.log_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        log_layout.addWidget(self.log_table)
        
        log_widget.setLayout(log_layout)
        self.main_tabs.addTab(log_widget, "View Alert Logs")
        
        # Set main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.addWidget(self.main_tabs)
        central_widget.setLayout(main_layout)
        
        # Load initial logs
        self.load_recent_logs()

    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        QShortcut(QKeySequence("Ctrl+S"), self, self.save_log)
        QShortcut(QKeySequence("Escape"), self, self.close)
        QShortcut(QKeySequence("Ctrl+T"), self, self.set_current_time)
        QShortcut(QKeySequence("Ctrl+Shift+C"), self, self.clear_message)
        QShortcut(QKeySequence("F5"), self, self.load_recent_logs)

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
            # Also save to Excel log
            everbridge_data = {
                'alert_type': 'Alert',
                'severity': 'High',
                'subject': f"Alert - {site_code}",
                'message': message,
                'recipients': 'All',
                'response_rate': '',
            }
            
            try:
                log_manager.add_everbridge_log(everbridge_data)
                # Refresh the log display
                self.load_recent_logs()
            except Exception as e:
                print(f"Error saving to Excel: {e}")
            
            show_success(self, f"Everbridge alert log saved!\n\nSite: {site_code}\nMessage: {preview}")
            
            # Ask if they want to log the notification confirmation
            from PyQt6.QtWidgets import QMessageBox
            reply = QMessageBox.question(
                self,
                "Notification Confirmation",
                "Would you like to log the confirmation email sent to the requester?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                from ui.everbridge_workflow import NotificationConfirmationDialog
                
                alert_info = {
                    "site": site_code,
                    "original_sender": "",  # Would need to track this from email
                    "message": message
                }
                
                dialog = NotificationConfirmationDialog(alert_info=alert_info, parent=self)
                dialog.exec()
            
            # Switch to logs tab to show the new entry
            self.main_tabs.setCurrentIndex(1)
            self.load_recent_logs()
        except Exception as e:
            show_error(self, f"Error saving log: {str(e)}")
            self.status_bar.showMessage("Error saving log")
    
    def load_recent_logs(self):
        """Load recent Everbridge logs into the table"""
        try:
            df = log_manager.get_recent_logs('everbridge', limit=50)
            self.current_df = df  # Store for filtering
            if not df.empty:
                self.log_table.setRowCount(len(df))
                self.log_table.setColumnCount(len(df.columns))
                self.log_table.setHorizontalHeaderLabels(df.columns.tolist())
                
                for row in range(len(df)):
                    for col in range(len(df.columns)):
                        value = str(df.iloc[row, col])
                        item = QTableWidgetItem(value)
                        self.log_table.setItem(row, col, item)
                
                # Adjust column widths
                self.log_table.resizeColumnsToContents()
                
                # Update status
                self.status_bar.showMessage(f"Loaded {len(df)} Everbridge log entries")
            else:
                self.log_table.setRowCount(0)
                self.log_table.setColumnCount(5)
                self.log_table.setHorizontalHeaderLabels(["Date", "Time", "Alert Type", "Subject", "Message"])
                self.status_bar.showMessage("No Everbridge logs found")
        except Exception as e:
            print(f"Error loading logs: {e}")
            self.status_bar.showMessage("Error loading logs")
    
    def filter_logs(self):
        """Filter logs based on search text"""
        if not hasattr(self, 'current_df') or self.current_df.empty:
            return
        
        search_text = self.log_filter.text().lower()
        if not search_text:
            # Show all if no filter
            self.load_recent_logs()
            return
        
        # Filter dataframe
        filtered_df = self.current_df[
            self.current_df.apply(
                lambda row: any(search_text in str(cell).lower() for cell in row),
                axis=1
            )
        ]
        
        # Update table
        self.log_table.setRowCount(len(filtered_df))
        for row in range(len(filtered_df)):
            for col in range(len(filtered_df.columns)):
                value = str(filtered_df.iloc[row, col])
                item = QTableWidgetItem(value)
                self.log_table.setItem(row, col, item)
        
        self.status_bar.showMessage(f"Showing {len(filtered_df)} of {len(self.current_df)} entries")
    
    def export_logs(self):
        """Export logs to file"""
        from PyQt6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Everbridge Logs", "everbridge_logs_export.xlsx", 
            "Excel Files (*.xlsx);;CSV Files (*.csv)"
        )
        if file_path:
            try:
                if hasattr(self, 'current_df'):
                    if file_path.endswith('.csv'):
                        self.current_df.to_csv(file_path, index=False)
                    else:
                        self.current_df.to_excel(file_path, index=False)
                    QMessageBox.information(self, "Success", f"Logs exported to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export: {str(e)}")