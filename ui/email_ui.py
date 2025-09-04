from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTabWidget,
    QFileDialog, QLineEdit, QTextEdit, QMessageBox, QMainWindow,
    QStatusBar, QComboBox, QTableWidget, QTableWidgetItem,
    QSplitter, QHeaderView, QHBoxLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QFont, QShortcut, QKeySequence
from ui.help_utils import HelpButton, get_help_training_id
from msg_parser import parse_msg
from database import insert_email_log
from datetime import datetime
from log_manager import log_manager
from app_settings import app_settings
from config import SITE_CODES as DEFAULT_SITE_CODES

# Get site codes from settings or use defaults
def get_site_codes():
    dropdown_options = app_settings.get("dropdown_options", {})
    return dropdown_options.get("site_codes", DEFAULT_SITE_CODES)

EMAIL_TABS = [
    "Data Request", "Incident Report", "Muster Report",
    "Parking Tag App", "Badge Deactivation",
    "Everbridge Alert", "Notification", "Other"
]

class DragDropLabel(QLabel):
    def __init__(self, parent):
        super().__init__("Drag a .msg file here or click to browse\n\n(Requires Outlook installed)")
        self.parent = parent
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #333333;
                border-radius: 4px;
                padding: 40px;
                background-color: #1a1a1a;
                color: #808080;
                font-size: 12px;
                font-weight: 500;
            }
        """)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setAcceptDrops(True)
        self.setMinimumHeight(150)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if any(url.toLocalFile().endswith('.msg') for url in urls):
                event.acceptProposedAction()
                self.setStyleSheet("""
                    QLabel {
                        border: 2px solid #4a4a4a;
                        border-radius: 4px;
                        padding: 40px;
                        background-color: #1f1f1f;
                        color: #e0e0e0;
                        font-size: 12px;
                        font-weight: 500;
                    }
                """)
            else:
                event.ignore()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #333333;
                border-radius: 4px;
                padding: 40px;
                background-color: #1a1a1a;
                color: #808080;
                font-size: 12px;
                font-weight: 500;
            }
        """)

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        for url in urls:
            filepath = url.toLocalFile()
            if filepath.endswith('.msg'):
                self.parent.load_msg_file(filepath)
                break
        self.dragLeaveEvent(event)

    def mousePressEvent(self, event):
        self.parent.select_file()

class EmailPanel(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Email Log Entry")
        self.setMinimumSize(800, 700)
        self.showMaximized()
        
        self.current_tab = "Data Request"
        self.msg_path = None
        self.email_meta = {}
        
        # Status bar - initialize BEFORE init_ui
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready to log email")

        self.init_ui()
        self.setup_shortcuts()

    def init_ui(self):
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 20, 30, 20)
        
        # Add help button in top right
        from PyQt6.QtWidgets import QHBoxLayout
        header_layout = QHBoxLayout()
        header_layout.addStretch()
        help_btn = HelpButton("Email Logger", get_help_training_id("email"), self)
        header_layout.addWidget(help_btn)
        layout.addLayout(header_layout)

        # Title
        title = QLabel("Email Logger")
        title_font = QFont("Segoe UI", 18, QFont.Weight.Bold)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #e0e0e0; margin-bottom: 10px;")
        layout.addWidget(title)

        # Tabs with larger font
        self.tabs = QTabWidget()
        self.tabs.setFont(QFont("Arial", 14))
        self.tabs.setStyleSheet("""
            QTabWidget::tab-bar {
                alignment: center;
            }
            QTabBar::tab {
                padding: 10px 20px;
                margin: 2px;
            }
            QTabBar::tab:selected {
                background-color: #2196F3;
                color: white;
            }
        """)
        
        for tab_name in EMAIL_TABS:
            tab = QWidget()
            self.tabs.addTab(tab, tab_name)
        self.tabs.currentChanged.connect(self.switch_tab)
        layout.addWidget(self.tabs)

        # Drag and drop area
        self.drop_label = DragDropLabel(self)
        layout.addWidget(self.drop_label)

        # Manual entry button
        manual_btn = QPushButton("✏️ Enter Email Info Manually")
        manual_btn.setFixedHeight(50)
        manual_btn.setFont(QFont("Arial", 14))
        manual_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        manual_btn.clicked.connect(self.enable_manual_entry)
        layout.addWidget(manual_btn)

        # Fields area
        self.fields_layout = QVBoxLayout()
        self.fields_layout.setSpacing(10)
        self.dynamic_fields = {}
        self.meta_fields = {}
        self.populate_fields(self.current_tab)
        layout.addLayout(self.fields_layout)

        # Save button
        self.save_btn = QPushButton("💾 Save Log (Ctrl+S)")
        self.save_btn.setEnabled(False)
        self.save_btn.setFixedHeight(60)
        self.save_btn.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #45A049;
            }
            QPushButton:disabled {
                background-color: #CCCCCC;
                color: #666666;
            }
        """)
        self.save_btn.clicked.connect(self.save_log)
        
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
        self.main_tabs.addTab(input_widget, "Log New Email")
        
        # View Logs Tab
        log_widget = QWidget()
        log_layout = QVBoxLayout()
        log_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header with controls
        controls_layout = QHBoxLayout()
        
        # Date filter
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
        self.main_tabs.addTab(log_widget, "View Email Logs")
        
        # Set main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.addWidget(self.main_tabs)
        central_widget.setLayout(main_layout)
        
        # Load initial logs
        self.load_recent_logs()

    def load_recent_logs(self):
        """Load recent email logs into the table"""
        try:
            df = log_manager.get_recent_logs('email', limit=50)
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
                self.status_bar.showMessage(f"Loaded {len(df)} email log entries")
            else:
                self.log_table.setRowCount(0)
                self.log_table.setColumnCount(5)
                self.log_table.setHorizontalHeaderLabels(["Date", "Time", "From", "Subject", "Category"])
                self.status_bar.showMessage("No email logs found")
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
            self, "Export Email Logs", "email_logs_export.xlsx", 
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
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        QShortcut(QKeySequence("Ctrl+S"), self, self.save_log)
        QShortcut(QKeySequence("Ctrl+O"), self, self.select_file)
        QShortcut(QKeySequence("Escape"), self, self.close)
        QShortcut(QKeySequence("F5"), self, self.load_recent_logs)

    def switch_tab(self, index):
        self.current_tab = EMAIL_TABS[index]
        self.clear_fields()
        self.populate_fields(self.current_tab)
        
        # If we're in manual entry mode, make fields editable again
        if self.save_btn.isEnabled() and (not self.msg_path or self.msg_path == "Manual Entry"):
            self.make_fields_editable()

    def clear_fields(self):
        for i in reversed(range(self.fields_layout.count())):
            widget = self.fields_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        self.dynamic_fields = {}
        self.meta_fields = {}

    def populate_fields(self, tab_name):
        # Style for labels
        label_style = "font-size: 14px; font-weight: bold; color: #333; margin-top: 10px;"
        
        if tab_name == "Notification":
            self.add_line_edit("Recipient Name", label_style)
        else:
            self.add_meta_display("Sender", label_style)
            self.add_meta_display("Subject", label_style)

        self.add_meta_display("Received Time", label_style)

        if tab_name == "Data Request":
            self.add_line_edit("Ticket Number", label_style)
        elif tab_name == "Incident Report":
            self.add_line_edit("Incident Number", label_style)
        elif tab_name == "Muster Report":
            self.add_site_code_dropdown("Site Code", label_style)
        elif tab_name == "Everbridge Alert":
            self.add_text_edit("Message", label_style)
        elif tab_name in ["Badge Deactivation", "Parking Tag App", "Other"]:
            label = QLabel("(No additional fields required)")
            label.setFont(QFont("Arial", 14))
            label.setStyleSheet("color: #666; font-style: italic; margin: 20px;")
            self.fields_layout.addWidget(label)

    def add_meta_display(self, label_text, label_style=""):
        label = QLabel(label_text)
        label.setStyleSheet(label_style)
        self.fields_layout.addWidget(label)
        
        box = QLineEdit()
        box.setReadOnly(True)
        box.setFont(QFont("Arial", 14))
        box.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #DDDDDD;
                border-radius: 5px;
                background-color: #F5F5F5;
            }
        """)
        box.setPlaceholderText(f"Enter {label_text}")
        self.fields_layout.addWidget(box)
        self.meta_fields[label_text] = box

    def add_line_edit(self, label_text, label_style=""):
        label = QLabel(label_text)
        label.setStyleSheet(label_style)
        self.fields_layout.addWidget(label)
        
        box = QLineEdit()
        box.setFont(QFont("Arial", 14))
        box.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #2196F3;
                border-radius: 5px;
            }
            QLineEdit:focus {
                border: 2px solid #1976D2;
                background-color: #E3F2FD;
            }
        """)
        box.setPlaceholderText(f"Enter {label_text}")
        self.fields_layout.addWidget(box)
        self.dynamic_fields[label_text] = box

    def add_text_edit(self, label_text, label_style=""):
        label = QLabel(label_text)
        label.setStyleSheet(label_style)
        self.fields_layout.addWidget(label)
        
        box = QTextEdit()
        box.setFont(QFont("Arial", 14))
        box.setMaximumHeight(150)
        box.setStyleSheet("""
            QTextEdit {
                padding: 10px;
                border: 2px solid #2196F3;
                border-radius: 5px;
            }
            QTextEdit:focus {
                border: 2px solid #1976D2;
                background-color: #E3F2FD;
            }
        """)
        box.setPlaceholderText(f"Enter {label_text}")
        self.fields_layout.addWidget(box)
        self.dynamic_fields[label_text] = box
    
    def add_site_code_dropdown(self, label_text, label_style=""):
        """Add a dropdown for site codes that's editable"""
        label = QLabel(label_text)
        label.setStyleSheet(label_style)
        self.fields_layout.addWidget(label)
        
        dropdown = QComboBox()
        dropdown.setEditable(True)  # Allow custom entries
        dropdown.addItems(get_site_codes())
        dropdown.setFont(QFont("Arial", 14))
        dropdown.setStyleSheet("""
            QComboBox {
                padding: 10px;
                border: 2px solid #2196F3;
                border-radius: 5px;
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
        """)
        dropdown.setPlaceholderText(f"Select or enter {label_text}")
        self.fields_layout.addWidget(dropdown)
        self.dynamic_fields[label_text] = dropdown
        return dropdown

    def make_fields_editable(self):
        """Make meta fields editable for manual entry"""
        for field in self.meta_fields.values():
            field.setReadOnly(False)
            field.setStyleSheet("""
                QLineEdit {
                    padding: 10px;
                    border: 2px solid #2196F3;
                    border-radius: 5px;
                    background-color: white;
                }
                QLineEdit:focus {
                    border: 2px solid #1976D2;
                    background-color: #E3F2FD;
                }
            """)

    def enable_manual_entry(self):
        """Enable manual entry without a .msg file"""
        self.make_fields_editable()
        self.save_btn.setEnabled(True)
        self.drop_label.setText("✏️ Manual entry mode - no file loaded")
        self.msg_path = None
        self.status_bar.showMessage("Manual entry mode enabled")

    def select_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select .msg File", "", "Outlook Messages (*.msg)")
        if path:
            self.load_msg_file(path)

    def load_msg_file(self, path):
        try:
            self.msg_path = path
            self.drop_label.setText(f"✅ Loaded: {path.split('/')[-1]}")
            self.email_meta = parse_msg(path)
            
            # Check if there was an error parsing
            if self.email_meta.get("error", False):
                QMessageBox.warning(
                    self, 
                    "Outlook Error", 
                    "Could not parse the .msg file.\n\n"
                    "Make sure Microsoft Outlook is installed and configured.\n\n"
                    "You can still manually enter the email information."
                )
                # Allow manual entry even if parsing failed
                self.make_fields_editable()
                self.save_btn.setEnabled(True)
                self.status_bar.showMessage("Parsing failed - manual entry available")
            else:
                self.fill_meta_fields()
                self.save_btn.setEnabled(True)
                self.status_bar.showMessage("Email loaded successfully")
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to load file: {str(e)}\n\n"
                "You can use 'Enter Email Info Manually' instead."
            )
            self.drop_label.setText("❌ Error loading file - try manual entry")
            self.status_bar.showMessage("Error loading file")

    def fill_meta_fields(self):
        # Only fill fields if we have valid data (no error)
        if self.email_meta.get("error", False):
            return
            
        if self.current_tab == "Notification":
            if "Sender" in self.meta_fields:
                self.meta_fields["Sender"].hide()
            if "Subject" in self.meta_fields:
                self.meta_fields["Subject"].hide()
            if "Recipient Name" in self.dynamic_fields:
                self.dynamic_fields["Recipient Name"].setText(self.email_meta.get("email", ""))
        else:
            if "Sender" in self.meta_fields:
                self.meta_fields["Sender"].setText(self.email_meta.get("sender", ""))
            if "Subject" in self.meta_fields:
                self.meta_fields["Subject"].setText(self.email_meta.get("subject", ""))
        if "Received Time" in self.meta_fields:
            timestamp = self.email_meta.get("sent_time" if self.current_tab == "Notification" else "received_time", "")
            self.meta_fields["Received Time"].setText(timestamp)

    def save_log(self):
        if not self.save_btn.isEnabled():
            return
            
        log_type = self.current_tab
        
        # Get field values - allow manual entry if parsing failed
        sender = None
        if "Sender" in self.meta_fields:
            text = self.meta_fields["Sender"].text()
            # Only use the text if it's not an error message
            if text and not text.startswith("Error"):
                sender = text
        
        recipient = self.dynamic_fields.get("Recipient Name")
        recipient = recipient.text() if recipient else None
        
        subject = None
        if "Subject" in self.meta_fields:
            text = self.meta_fields["Subject"].text()
            if text and not text.startswith("Could not parse"):
                subject = text
        
        timestamp = None
        if "Received Time" in self.meta_fields:
            text = self.meta_fields["Received Time"].text()
            if text:
                timestamp = text
        
        # If no timestamp from parsing, use current time
        if not timestamp:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        msg_path = self.msg_path if self.msg_path else "Manual Entry"

        # Only 1 extra field max for now
        extra_field = None
        for key in self.dynamic_fields:
            if key not in ["Recipient Name"]:
                field = self.dynamic_fields[key]
                if isinstance(field, QTextEdit):
                    extra_field = field.toPlainText()
                elif isinstance(field, QComboBox):
                    extra_field = field.currentText()
                else:
                    extra_field = field.text()
                break

        insert_email_log(log_type, sender, recipient, subject, timestamp, extra_field, msg_path)
        
        # Also save to Excel log
        email_data = {
            'from': sender or recipient or 'Unknown',
            'subject': subject or 'No Subject',
            'category': log_type,
            'site': extra_field if extra_field else '',
            'priority': 'Normal',
            'notes': f"MSG Path: {msg_path}" if msg_path and msg_path != "Manual Entry" else ""
        }
        
        try:
            log_manager.add_email_log(email_data)
            # Refresh the log display
            self.load_recent_logs()
        except Exception as e:
            print(f"Error saving to Excel: {e}")

        QMessageBox.information(self, "Success", "Email log saved successfully!")
        
        # Check if this was an Everbridge Alert email and continue the workflow
        if log_type == "Everbridge Alert":
            reply = QMessageBox.question(
                self,
                "Send Everbridge Alert",
                "Would you like to proceed with sending the Everbridge alert?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Open Everbridge alert panel with pre-filled data
                from ui.everbridge_ui import EverbridgePanel
                everbridge_panel = EverbridgePanel()
                
                # Pre-fill the message if we have it
                if extra_field:  # This contains the alert message
                    everbridge_panel.message_box.setText(extra_field)
                
                # Pre-fill site if available
                site = self.dynamic_fields.get("Site Code")
                if site and hasattr(site, 'currentText'):
                    everbridge_panel.site_code_field.setCurrentText(site.currentText())
                
                everbridge_panel.show()
        
        # Switch to logs tab to show the new entry
        self.main_tabs.setCurrentIndex(1)
        self.load_recent_logs()