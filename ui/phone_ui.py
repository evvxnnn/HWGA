from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox,
    QLineEdit, QTextEdit, QPushButton, QHBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt
from datetime import datetime
from database import insert_phone_log

CALL_TYPES = [
    "Everbridge", "Incident Report", "Ongoing Incident",
    "Alarm Monitor Center", "Facilities", "On-Call Tech", "Other"
]

# Customizable options for Facilities calls
ISSUE_TYPES = {
    "Audio Visual": ["Assistance", "Repair/Request", "Other"],
    "Building Maintenance": ["Blind/Curtain Repair", "Carpentry/Handyman", "Ceiling", "Elevator", "Fire Life Safety", "Floors", "Furniture Repair", "Hang Misc Items", "Painting", "Restroom Repairs", "Roof or Window Leak", "Shelving", "Signage", "Time Clock", "Walls", "Whiteboard", "Windows", "Other"],
    "Dock/Freight Elevator": ["Delivery Assistance", "Dock Equipment", "Dock Locks", "Dock Reservation", "Overhead Door", "Other"],
    "Doors/Locks?Keys": ["Broken Key", "Door", "Locked Desk/Cabinet", "New Access Card/Replacement", "New Key/Replacement", "Other"],
    "Electrical": ["Install New/Relocate", "Power Loss/Interruption", "Repair", "Testing/Tagging", "Other"],
    "Janitorial": ["Carpet Cleaning", "Cleanup / Spills", "Door Cleaning", "Dusting", "Empty Recycle", "Empty Trash", "Kitchen", "Odors", "Parking Lot Cleaning", "Equipment/Compactors", "Restroom", "Vacuuming", "Window/Glass", "Other"],
    "Lighting": ["Common Area/Office", "Exit Sign/Emergency Light", "Fixture", "Signage", "Other"],
    "Lockers": ["Assignment", "Battery", "Lock Out", "Repair/Maitenance", "Surrender", "Other"],
    "Pest Control": ["Interior", "Exterior", "Other"],
    "Plumbing": ["Clogged Toilet/Sink/Drain", "Repair Toilet/Sink/Drain", "Water Leak", "Other"],
    "Safety/Hazard": ["Trip/Fall Hazard", "Spill/Leak", "Equipment/Machine Malfunction", "Other"]
}

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
        add_text = self.add_text_edit
        add_dropdown = self.add_dropdown
        
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
            
            # Issue Type dropdown
            self.issue_type_dropdown = add_dropdown("Issue Type", list(ISSUE_TYPES.keys()))
            self.issue_type_dropdown.currentIndexChanged.connect(self.update_subtypes)
            
            # Issue Subtype dropdown
            self.issue_subtype_dropdown = add_dropdown("Issue Subtype", [])
            self.update_subtypes()  # Initialize with first type's subtypes
            
            add("Site Code")
            add("Location in Site")
            add("Additional Info")
        elif call_type == "On-Call Tech":
            add("Caller Name")
            add("Facilities Ticket Number")
        elif call_type == "Other":
            add("Caller Name")
            add_text("Description", height=150)

    def add_line_edit(self, label_text):
        box = QLineEdit()
        box.setPlaceholderText(label_text)
        self.fields_layout.addWidget(box)
        self.fields[label_text] = box

    def add_text_edit(self, label_text, height=100):
        label = QLabel(label_text)
        self.fields_layout.addWidget(label)
        box = QTextEdit()
        box.setPlaceholderText(f"Enter {label_text.lower()}")
        box.setMaximumHeight(height)
        self.fields_layout.addWidget(box)
        self.fields[label_text] = box

    def add_dropdown(self, label_text, items):
        label = QLabel(label_text)
        self.fields_layout.addWidget(label)
        dropdown = QComboBox()
        dropdown.addItems(items)
        self.fields_layout.addWidget(dropdown)
        self.fields[label_text] = dropdown
        return dropdown

    def update_subtypes(self):
        if hasattr(self, 'issue_type_dropdown') and hasattr(self, 'issue_subtype_dropdown'):
            issue_type = self.issue_type_dropdown.currentText()
            self.issue_subtype_dropdown.clear()
            self.issue_subtype_dropdown.addItems(ISSUE_TYPES.get(issue_type, []))

    def save_log(self):
        data = {}
        for k, f in self.fields.items():
            if isinstance(f, QLineEdit):
                data[k] = f.text()
            elif isinstance(f, QTextEdit):
                data[k] = f.toPlainText()
            elif isinstance(f, QComboBox):
                data[k] = f.currentText()
        
        call_type = self.current_call_type
        timestamp = self.timestamp_field.text()

        # Map fields appropriately for Other category
        if call_type == "Other":
            message = data.get("Description", "")
        else:
            message = data.get("Message") or data.get("Additional Info") or data.get("Description")

        insert_phone_log(
            call_type=call_type,
            caller_name=data.get("Caller Name"),
            site_code=data.get("Site Code"),
            ticket_number=data.get("Incident Report Number") or data.get("Facilities Ticket Number"),
            address=data.get("Address"),
            alarm_type=data.get("Alarm Type"),
            issue_type=data.get("Issue Type"),
            issue_subtype=data.get("Issue Subtype"),
            message=message,
            timestamp=timestamp
        )

        QMessageBox.information(self, "Saved", "Phone call log saved successfully.")
        self.close()