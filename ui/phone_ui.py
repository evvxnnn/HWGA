from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox,
    QLineEdit, QTextEdit, QPushButton, QHBoxLayout, 
    QMessageBox, QMainWindow, QStatusBar, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QShortcut, QKeySequence
from datetime import datetime
from database import insert_phone_log
from ui.styles import (
    Fonts, Colors,
    INPUT_STYLE, TABLE_STYLE, LIST_STYLE, DROPDOWN_STYLE,
    get_button_style, make_accessible,
    show_error, show_success
)
from app_settings import app_settings
from config import SITE_CODES as DEFAULT_SITE_CODES


# Default call types - can be customized in settings
DEFAULT_CALL_TYPES = [
    "Everbridge", "Incident Report", "Ongoing Incident",
    "Alarm Monitor Center", "Facilities", "On-Call Tech", "Other"
]

# Get call types from settings or use defaults
def get_call_types():
    dropdown_options = app_settings.get("dropdown_options", {})
    return dropdown_options.get("phone_call_types", DEFAULT_CALL_TYPES)

# Get site codes from settings or use defaults
def get_site_codes():
    dropdown_options = app_settings.get("dropdown_options", {})
    return dropdown_options.get("site_codes", DEFAULT_SITE_CODES)

# Customizable options for Facilities calls
ISSUE_TYPES = {
    "Audio Visual": ["Assistance", "Repair/Request", "Other"],
    "Building Maintenance": ["Blind/Curtain Repair", "Carpentry/Handyman", "Ceiling", "Elevator", "Fire Life Safety", "Floors", "Furniture Repair", "Hang Misc Items", "Painting", "Restroom Repairs", "Roof or Window Leak", "Shelving", "Signage", "Time Clock", "Walls", "Whiteboard", "Windows", "Other"],
    "Dock/Freight Elevator": ["Delivery Assistance", "Dock Equipment", "Dock Locks", "Dock Reservation", "Overhead Door", "Other"],
    "Doors/Locks/Keys": ["Broken Key", "Door", "Locked Desk/Cabinet", "New Access Card/Replacement", "New Key/Replacement", "Other"],
    "Electrical": ["Install New/Relocate", "Power Loss/Interruption", "Repair", "Testing/Tagging", "Other"],
    "Janitorial": ["Carpet Cleaning", "Cleanup / Spills", "Door Cleaning", "Dusting", "Empty Recycle", "Empty Trash", "Kitchen", "Odors", "Parking Lot Cleaning", "Equipment/Compactors", "Restroom", "Vacuuming", "Window/Glass", "Other"],
    "Lighting": ["Common Area/Office", "Exit Sign/Emergency Light", "Fixture", "Signage", "Other"],
    "Lockers": ["Assignment", "Battery", "Lock Out", "Repair/Maintenance", "Surrender", "Other"],
    "Pest Control": ["Interior", "Exterior", "Other"],
    "Plumbing": ["Clogged Toilet/Sink/Drain", "Repair Toilet/Sink/Drain", "Water Leak", "Other"],
    "Safety/Hazard": ["Trip/Fall Hazard", "Spill/Leak", "Equipment/Machine Malfunction", "Other"]
}

class PhonePanel(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Phone Call Log Entry")
        self.setMinimumSize(900, 800)
        self.showMaximized()
        
        self.call_types = get_call_types()  # Get from settings
        self.current_call_type = self.call_types[0]
        self.fields = {}

        self.init_ui()
        self.setup_shortcuts()
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready to log phone call")

    def init_ui(self):
        # Central widget with scroll area for smaller screens
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.setCentralWidget(scroll_area)
        
        central_widget = QWidget()
        scroll_area.setWidget(central_widget)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 20, 30, 20)

        # Title
        title = QLabel("📞 Phone Call Logger")
        title.setFont(Fonts.TITLE)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("margin-bottom: 20px;")
        layout.addWidget(title)

        # Call Type Dropdown
        dropdown_layout = QHBoxLayout()
        dropdown_label = QLabel("Call Type:")
        dropdown_label.setFont(Fonts.LABEL)
        dropdown_layout.addWidget(dropdown_label)
        
        self.call_type_dropdown = QComboBox()
        self.call_type_dropdown.addItems(self.call_types)
        self.call_type_dropdown.setFont(Fonts.NORMAL)
        self.call_type_dropdown.setStyleSheet(DROPDOWN_STYLE)
        self.call_type_dropdown.currentIndexChanged.connect(self.switch_call_type)
        make_accessible(self.call_type_dropdown, "Select the type of phone call")
        dropdown_layout.addWidget(self.call_type_dropdown)
        dropdown_layout.addStretch()
        layout.addLayout(dropdown_layout)

        # Timestamp with current time button
        time_layout = QHBoxLayout()
        time_label = QLabel("Call Time:")
        time_label.setFont(Fonts.LABEL)
        time_layout.addWidget(time_label)
        
        # Auto-fill timestamp if enabled in settings
        if app_settings.get("auto_timestamp", True):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            timestamp = ""
        
        self.timestamp_field = QLineEdit(timestamp)
        self.timestamp_field.setFont(Fonts.NORMAL)
        self.timestamp_field.setStyleSheet(INPUT_STYLE)
        make_accessible(self.timestamp_field, "Enter the time of the call")
        time_layout.addWidget(self.timestamp_field)
        
        now_btn = QPushButton("🕐 Now")
        now_btn.setFont(Fonts.BUTTON)
        now_btn.setStyleSheet(get_button_style(Colors.INFO, 45))
        now_btn.clicked.connect(self.set_current_time)
        make_accessible(now_btn, "Set to current time")
        time_layout.addWidget(now_btn)
        
        layout.addLayout(time_layout)

        # Dynamic Field Area
        self.fields_layout = QVBoxLayout()
        self.fields_layout.setSpacing(10)
        layout.addLayout(self.fields_layout)
        self.populate_fields(self.current_call_type)

        # Save Button
        self.save_btn = QPushButton("💾 Save Call Log (Ctrl+S)")
        self.save_btn.setFont(Fonts.BUTTON_LARGE)
        self.save_btn.setStyleSheet(get_button_style(Colors.SUCCESS, 60))
        self.save_btn.clicked.connect(self.save_log)
        make_accessible(self.save_btn, "Save the phone call log")
        layout.addWidget(self.save_btn)

        central_widget.setLayout(layout)

    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        QShortcut(QKeySequence("Ctrl+S"), self, self.save_log)
        QShortcut(QKeySequence("Escape"), self, self.close)
        QShortcut(QKeySequence("Ctrl+T"), self, self.set_current_time)

    def set_current_time(self):
        """Set timestamp to current time"""
        self.timestamp_field.setText(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.status_bar.showMessage("Timestamp updated to current time")

    def switch_call_type(self, index):
        self.current_call_type = self.call_types[index]
        self.clear_fields()
        self.populate_fields(self.current_call_type)
        self.status_bar.showMessage(f"Call type: {self.current_call_type}")

    def clear_fields(self):
        for i in reversed(range(self.fields_layout.count())):
            widget = self.fields_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        self.fields = {}

    def populate_fields(self, call_type):
        if call_type == "Everbridge":
            self.add_line_edit("Caller Name", "Name of the person calling")
            self.add_line_edit("Message", "Brief message or alert details")
        elif call_type == "Incident Report":
            self.add_line_edit("Caller Name", "Name of the person reporting")
            self.add_site_code_dropdown("Site Code", "Location code (e.g., MAIN, DC1)")
            self.add_line_edit("Incident Report Number", "Incident tracking number")
        elif call_type == "Ongoing Incident":
            self.add_line_edit("Caller Name", "Name of the person calling")
            self.add_site_code_dropdown("Site Code", "Location code")
        elif call_type == "Alarm Monitor Center":
            self.add_site_code_dropdown("Site Code", "Location code")
            self.add_line_edit("Address", "Physical address of alarm")
            self.add_line_edit("Alarm Type", "Type of alarm triggered")
        elif call_type == "Facilities":
            self.add_line_edit("Caller Name", "Name of the person calling")
            
            # Issue Type dropdown
            self.issue_type_dropdown = self.add_dropdown(
                "Issue Type", 
                list(ISSUE_TYPES.keys()),
                "Select the category of facilities issue"
            )
            self.issue_type_dropdown.currentIndexChanged.connect(self.update_subtypes)
            
            # Issue Subtype dropdown
            self.issue_subtype_dropdown = self.add_dropdown(
                "Issue Subtype", 
                [],
                "Select the specific issue"
            )
            self.update_subtypes()  # Initialize with first type's subtypes
            
            self.add_site_code_dropdown("Site Code", "Location code")
            self.add_line_edit("Location in Site", "Specific location within the site")
            self.add_text_edit("Additional Info", "Any additional details", height=100)
        elif call_type == "On-Call Tech":
            self.add_line_edit("Caller Name", "Name of the person calling")
            self.add_line_edit("Facilities Ticket Number", "Ticket tracking number")
        elif call_type == "Other":
            self.add_line_edit("Caller Name", "Name of the person calling")
            self.add_text_edit("Description", "Full description of the call", height=200)

    def add_line_edit(self, label_text, tooltip):
        label = QLabel(label_text + ":")
        label.setFont(Fonts.LABEL)
        self.fields_layout.addWidget(label)
        
        box = QLineEdit()
        box.setFont(Fonts.NORMAL)
        box.setStyleSheet(INPUT_STYLE)
        box.setPlaceholderText(f"Enter {label_text.lower()}")
        make_accessible(box, tooltip)
        self.fields_layout.addWidget(box)
        self.fields[label_text] = box

    def add_text_edit(self, label_text, tooltip, height=150):
        label = QLabel(label_text + ":")
        label.setFont(Fonts.LABEL)
        self.fields_layout.addWidget(label)
        
        box = QTextEdit()
        box.setFont(Fonts.NORMAL)
        box.setStyleSheet(INPUT_STYLE)
        box.setPlaceholderText(f"Enter {label_text.lower()}")
        box.setMaximumHeight(height)
        make_accessible(box, tooltip)
        self.fields_layout.addWidget(box)
        self.fields[label_text] = box

    def add_dropdown(self, label_text, items, tooltip):
        label = QLabel(label_text + ":")
        label.setFont(Fonts.LABEL)
        self.fields_layout.addWidget(label)
        
        dropdown = QComboBox()
        dropdown.addItems(items)
        dropdown.setFont(Fonts.NORMAL)
        dropdown.setStyleSheet(DROPDOWN_STYLE)
        make_accessible(dropdown, tooltip)
        self.fields_layout.addWidget(dropdown)
        self.fields[label_text] = dropdown
        return dropdown
    
    def add_site_code_dropdown(self, label_text, tooltip):
        """Add a dropdown for site codes that's editable"""
        label = QLabel(label_text + ":")
        label.setFont(Fonts.LABEL)
        self.fields_layout.addWidget(label)
        
        dropdown = QComboBox()
        dropdown.setEditable(True)  # Allow custom entries
        dropdown.addItems(get_site_codes())
        dropdown.setFont(Fonts.NORMAL)
        dropdown.setStyleSheet(DROPDOWN_STYLE)
        make_accessible(dropdown, tooltip)
        self.fields_layout.addWidget(dropdown)
        self.fields[label_text] = dropdown
        return dropdown

    def update_subtypes(self):
        if hasattr(self, 'issue_type_dropdown') and hasattr(self, 'issue_subtype_dropdown'):
            issue_type = self.issue_type_dropdown.currentText()
            self.issue_subtype_dropdown.clear()
            self.issue_subtype_dropdown.addItems(ISSUE_TYPES.get(issue_type, []))

    def save_log(self):
        # Validate required fields
        if self.current_call_type != "Alarm Monitor Center" and "Caller Name" in self.fields:
            if not self.fields["Caller Name"].text().strip():
                show_error(self, "Please enter the caller's name.")
                self.fields["Caller Name"].setFocus()
                return

        data = {}
        for k, f in self.fields.items():
            if isinstance(f, QLineEdit):
                data[k] = f.text()
            elif isinstance(f, QTextEdit):
                data[k] = f.toPlainText()
            elif isinstance(f, QComboBox):
                # For editable combo boxes, get the current text
                data[k] = f.currentText()
        
        call_type = self.current_call_type
        timestamp = self.timestamp_field.text()

        # Map fields appropriately for Other category
        if call_type == "Other":
            message = data.get("Description", "")
        else:
            message = data.get("Message") or data.get("Additional Info") or data.get("Description")

        try:
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

            show_success(self, "Phone call log saved successfully!")
            self.close()
        except Exception as e:
            show_error(self, f"Error saving log: {str(e)}")
            self.status_bar.showMessage("Error saving log")