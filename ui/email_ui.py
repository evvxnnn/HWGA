from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTabWidget,
    QFileDialog, QLineEdit, QTextEdit, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
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
        super().__init__("Drag a .msg file here or click to select\n(Requires Outlook installed)")
        self.parent = parent
        self.setStyleSheet("border: 2px dashed #888; padding: 20px;")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if any(url.toLocalFile().endswith('.msg') for url in urls):
                event.acceptProposedAction()
                self.setStyleSheet("border: 2px solid #4CAF50; padding: 20px; background-color: #E8F5E9;")
            else:
                event.ignore()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.setStyleSheet("border: 2px dashed #888; padding: 20px;")

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        for url in urls:
            filepath = url.toLocalFile()
            if filepath.endswith('.msg'):
                self.parent.load_msg_file(filepath)
                break
        self.setStyleSheet("border: 2px dashed #888; padding: 20px;")

    def mousePressEvent(self, event):
        self.parent.select_file()

class EmailPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Email Log")
        self.setMinimumSize(600, 400)
        self.current_tab = "Data Request"
        self.msg_path = None
        self.email_meta = {}

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.tabs = QTabWidget()
        for tab_name in EMAIL_TABS:
            tab = QWidget()
            self.tabs.addTab(tab, tab_name)
        self.tabs.currentChanged.connect(self.switch_tab)
        layout.addWidget(self.tabs)

        self.drop_label = DragDropLabel(self)
        layout.addWidget(self.drop_label)

        # Add manual entry button
        manual_btn = QPushButton("Enter Email Info Manually")
        manual_btn.clicked.connect(self.enable_manual_entry)
        layout.addWidget(manual_btn)

        self.fields_layout = QVBoxLayout()
        self.dynamic_fields = {}
        self.meta_fields = {}
        self.populate_fields(self.current_tab)
        layout.addLayout(self.fields_layout)

        self.save_btn = QPushButton("Save Log")
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self.save_log)
        layout.addWidget(self.save_btn)

        self.setLayout(layout)

    def switch_tab(self, index):
        self.current_tab = EMAIL_TABS[index]
        self.clear_fields()
        self.populate_fields(self.current_tab)
        
        # If we're in manual entry mode, make fields editable again
        if self.save_btn.isEnabled() and (not self.msg_path or self.msg_path == "Manual Entry"):
            self.make_fields_editable()

    def clear_fields(self):
        for i in reversed(range(self.fields_layout.count())):
            self.fields_layout.itemAt(i).widget().deleteLater()
        self.dynamic_fields = {}
        self.meta_fields = {}

    def populate_fields(self, tab_name):
        if tab_name == "Notification":
            self.add_line_edit("Recipient Name")
        else:
            self.add_meta_display("Sender")
            self.add_meta_display("Subject")

        self.add_meta_display("Received Time")

        if tab_name == "Data Request":
            self.add_line_edit("Ticket Number")
        elif tab_name == "Incident Report":
            self.add_line_edit("Incident Number")
        elif tab_name == "Muster Report":
            self.add_line_edit("Site Code")
        elif tab_name == "Everbridge Alert":
            self.add_text_edit("Message")
        elif tab_name in ["Badge Deactivation", "Parking Tag App", "Other"]:
            label = QLabel("(No extra fields required)")
            self.fields_layout.addWidget(label)

    def add_meta_display(self, label_text):
        box = QLineEdit()
        box.setReadOnly(True)
        box.setPlaceholderText(label_text)
        self.fields_layout.addWidget(box)
        self.meta_fields[label_text] = box

    def make_fields_editable(self):
        """Make meta fields editable for manual entry"""
        for field in self.meta_fields.values():
            field.setReadOnly(False)
            field.setStyleSheet("background-color: white;")

    def add_line_edit(self, label_text):
        box = QLineEdit()
        box.setPlaceholderText(label_text)
        self.fields_layout.addWidget(box)
        self.dynamic_fields[label_text] = box

    def add_text_edit(self, label_text):
        box = QTextEdit()
        box.setPlaceholderText(label_text)
        self.fields_layout.addWidget(box)
        self.dynamic_fields[label_text] = box

    def enable_manual_entry(self):
        """Enable manual entry without a .msg file"""
        self.make_fields_editable()
        self.save_btn.setEnabled(True)
        self.drop_label.setText("Manual entry mode - no file loaded")
        self.msg_path = None

    def select_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select .msg File", "", "Outlook Messages (*.msg)")
        if path:
            self.load_msg_file(path)

    def load_msg_file(self, path):
        try:
            self.msg_path = path
            self.drop_label.setText(f"Loaded: {path.split('/')[-1]}")
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
            else:
                self.fill_meta_fields()
                self.save_btn.setEnabled(True)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to load file: {str(e)}\n\n"
                "You can use 'Enter Email Info Manually' instead."
            )
            self.drop_label.setText("Error loading file - try manual entry")

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
        log_type = self.current_tab
        
        # Get field values - allow manual entry if parsing failed
        sender = None
        if "Sender" in self.meta_fields:
            text = self.meta_fields["Sender"].text()
            # Only use the text if it's not an error message
            if text and not text.startswith("Error"):
                sender = text
        
        recipient = self.dynamic_fields.get("Recipient Name").text() if "Recipient Name" in self.dynamic_fields else None
        
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

        QMessageBox.information(self, "Saved", "Email log saved successfully.")
        self.close()