from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox,
    QLineEdit, QTextEdit, QPushButton, QHBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt
from datetime import datetime
from database import insert_phone_log

CALL_TYPES = [
    "Everbridge", "Incident Report", "Ongoing Incident",
    "Alarm Monitor Center", "Facilities", "On-Call Tech"
]

class PhonePanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Phone Call Log")
        self.setMinimumSize(600, 400)
        self.current_call_type = CALL_TYPES[0]
        self.fields = {}

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Call Type Dropdown
        dropdown_layout = QHBoxLayout()
        dropdown_label = QLabel("Call Type:")
        self.call_type_dropdown = QComboBox()
        self.call_type_dropdown.addItems(CALL_TYPES)
        self.call_type_dropdown.currentIndexChanged.connect(self.switch_call_type)
        dropdown_layout.addWidget(dropdown_label)
        dropdown_layout.addWidget(self.call_type_dropdown)
        layout.addLayout(dropdown_layout)

        # Timestamp
        self.timestamp_field = QLineEdit(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.timestamp_field.setReadOnly(False)
        self.timestamp_field.setPlaceholderText("Timestamp")
        layout.addWidget(self.timestamp_field)

        # Dynamic Field Area
        self.fields_layout = QVBoxLayout()
        layout.addLayout(self.fields_layout)
        self.populate_fields(self.current_call_type)

        # Save Button
        self.save_btn = QPushButton("Save Call Log")
        self.save_btn.clicked.connect(self.save_log)
        layout.addWidget(self.save_btn)

        self.setLayout(layout)

    def switch_call_type(self, index):
        self.current_call_type = CALL_TYPES[index]
        self.clear_fields()
        self.populate_fields(self.current_call_type)

    def clear_fields(self):
        for i in reversed(range(self.fields_layout.count())):
            self.fields_layout.itemAt(i).widget().deleteLater()
        self.fields = {}

    def populate_fields(self, call_type):
        add = self.add_line_edit
        if call_type == "Everbridge":
            add("Caller Name")
            add("Message")
        elif call_type == "Incident Report":
            add("Caller Name")
            add("Site Code")
            add("Incident Report Number")
        elif call_type == "Ongoing Incident":
            add("Caller Name")
            add("Site Code")
        elif call_type == "Alarm Monitor Center":
            add("Site Code")
            add("Address")
            add("Alarm Type")
        elif call_type == "Facilities":
            add("Caller Name")
            add("Issue Type")
            add("Issue Subtype")
            add("Site Code")
            add("Location in Site")
            add("Additional Info")
        elif call_type == "On-Call Tech":
            add("Caller Name")
            add("Facilities Ticket Number")

    def add_line_edit(self, label_text):
        box = QLineEdit()
        box.setPlaceholderText(label_text)
        self.fields_layout.addWidget(box)
        self.fields[label_text] = box

    def save_log(self):
        data = {k: f.text() for k, f in self.fields.items()}
        call_type = self.current_call_type
        timestamp = self.timestamp_field.text()

        insert_phone_log(
            call_type=call_type,
            caller_name=data.get("Caller Name"),
            site_code=data.get("Site Code"),
            ticket_number=data.get("Incident Report Number") or data.get("Facilities Ticket Number"),
            address=data.get("Address"),
            alarm_type=data.get("Alarm Type"),
            issue_type=data.get("Issue Type"),
            issue_subtype=data.get("Issue Subtype"),
            message=data.get("Message") or data.get("Additional Info"),
            timestamp=timestamp
        )

        QMessageBox.information(self, "Saved", "Phone call log saved successfully.")
        self.close()
