from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTabWidget,
    QFileDialog, QLineEdit, QTextEdit, QMessageBox, QMainWindow,
    QStatusBar
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QFont, QShortcut, QKeySequence
from msg_parser import parse_msg
from database import insert_email_log
from datetime import datetime

EMAIL_TABS = [
    "Data Request", "Incident Report", "Muster Report",
    "Parking Tag App", "Badge Deactivation",
    "Everbridge Alert", "Notification", "Other"
]

class DragDropLabel(QLabel):
    def __init__(self, parent):
        super().__init__("📁 Drag a .msg file here or click to browse\n\n(Requires Outlook installed)")
        self.parent = parent
        self.setStyleSheet("""
            QLabel {
                border: 3px dashed #2196F3;
                border-radius: 15px;
                padding: 40px;
                background-color: rgba(33, 150, 243, 0.1);
                font-size: 16px;
                font-weight: bold;
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
                        border: 3px solid #4CAF50;
                        border-radius: 15px;
                        padding: 40px;
                        background-color: rgba(76, 175, 80, 0.2);
                        font-size: 16px;
                        font-weight: bold;
                    }
                """)
            else:
                event.ignore()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.setStyleSheet("""
            QLabel {
                border: 3px dashed #2196F3;
                border-radius: 15px;
                padding: 40px;
                background-color: rgba(33, 150, 243, 0.1);
                font-size: 16px;
                font-weight: bold;
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

        self.init_ui()
        self.setup_shortcuts()
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready to log email")

    def init_ui(self):
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 20, 30, 20)

        # Title
        title = QLabel("📧 Email Logger")
        title_font = QFont("Arial", 24, QFont.Weight.Bold)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("margin-bottom: 20px;")
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
        layout.addWidget(self.save_btn)

        central_widget.setLayout(layout)

    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        QShortcut(QKeySequence("Ctrl+S"), self, self.save_log)
        QShortcut(QKeySequence("Ctrl+O"), self, self.select_file)
        QShortcut(QKeySequence("Escape"), self, self.close)

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
            self.add_line_edit("Site Code", label_style)
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
                extra_field = field.toPlainText() if isinstance(field, QTextEdit) else field.text()
                break

        insert_email_log(log_type, sender, recipient, subject, timestamp, extra_field, msg_path)

        QMessageBox.information(self, "Success", "Email log saved successfully!")
        self.close()