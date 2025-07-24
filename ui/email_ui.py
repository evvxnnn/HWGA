from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTabWidget,
    QFileDialog, QLineEdit, QTextEdit, QMessageBox
)
from PyQt6.QtCore import Qt
from msg_parser import parse_msg
from database import insert_email_log

EMAIL_TABS = [
    "Data Request", "Incident Report", "Muster Report",
    "Parking Tag App", "Badge Deactivation",
    "Everbridge Alert", "Notification", "Other"
]

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

        self.drop_label = QLabel("Drag a .msg file here or click to select")
        self.drop_label.setStyleSheet("border: 2px dashed #888; padding: 20px;")
        self.drop_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_label.setAcceptDrops(True)
        self.drop_label.mousePressEvent = self.select_file
        layout.addWidget(self.drop_label)

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

    def select_file(self, event):
        path, _ = QFileDialog.getOpenFileName(self, "Select .msg File", "", "Outlook Messages (*.msg)")
        if path:
            self.msg_path = path
            self.drop_label.setText(f"Loaded: {path.split('/')[-1]}")
            self.email_meta = parse_msg(path)
            self.fill_meta_fields()
            self.save_btn.setEnabled(True)

    def fill_meta_fields(self):
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
        sender = self.meta_fields.get("Sender").text() if "Sender" in self.meta_fields else None
        recipient = self.dynamic_fields.get("Recipient Name").text() if "Recipient Name" in self.dynamic_fields else None
        subject = self.meta_fields.get("Subject").text() if "Subject" in self.meta_fields else None
        timestamp = self.meta_fields.get("Received Time").text() if "Received Time" in self.meta_fields else None
        msg_path = self.msg_path

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
