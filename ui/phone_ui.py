from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox,
    QLineEdit, QTextEdit, QPushButton, QHBoxLayout, 
    QMessageBox, QMainWindow, QStatusBar, QScrollArea,
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QShortcut, QKeySequence
from datetime import datetime
from database import insert_phone_log
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
        
        # Status bar - initialize BEFORE init_ui
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready to log phone call")

        self.init_ui()
        self.setup_shortcuts()

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

        # Add help button in top right
        header_layout = QHBoxLayout()
        header_layout.addStretch()
        help_btn = HelpButton("Phone Logger", get_help_training_id("phone"), self)
        header_layout.addWidget(help_btn)
        layout.addLayout(header_layout)
        
        # Title
        title = QLabel("Phone Call Logger")
        title.setFont(Fonts.TITLE)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #e0e0e0; margin-bottom: 20px;")
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
        
        now_btn = QPushButton("Now")
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
        self.save_btn = QPushButton("Save Call Log (Ctrl+S)")
        self.save_btn.setFont(Fonts.BUTTON_LARGE)
        self.save_btn.setStyleSheet(get_button_style(Colors.SUCCESS, 60))
        self.save_btn.clicked.connect(self.save_log)
        make_accessible(self.save_btn, "Save the phone call log")
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
        self.main_tabs.addTab(input_widget, "Log New Call")
        
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
        self.main_tabs.addTab(log_widget, "View Call Logs")
        
        # Set main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.addWidget(self.main_tabs)
        
        # Update central widget
        new_central = QWidget()
        new_central.setLayout(main_layout)
        scroll_area.setWidget(new_central)
        
        # Load initial logs
        self.load_recent_logs()

    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        QShortcut(QKeySequence("Ctrl+S"), self, self.save_log)
        QShortcut(QKeySequence("Escape"), self, self.close)
        QShortcut(QKeySequence("Ctrl+T"), self, self.set_current_time)
        QShortcut(QKeySequence("F5"), self, self.load_recent_logs)

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
            phone_log_id = insert_phone_log(
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

            # Also save to Excel log
            phone_data = {
                'caller': data.get("Caller Name", "Unknown"),
                'number': '',  # Not capturing phone number in this form
                'company': data.get("Site Code", ""),
                'type': call_type,
                'duration': '',
                'summary': message or '',
                'action_items': data.get("Incident Report Number") or data.get("Facilities Ticket Number") or ''
            }
            
            try:
                log_manager.add_phone_log(phone_data)
                # Refresh the log display
                self.load_recent_logs()
            except Exception as e:
                print(f"Error saving to Excel: {e}")
            
            show_success(self, "Phone call log saved successfully!")
            
            # Note: Would need to get actual log ID for proper linking
            # For now event chain will track by timestamp
            
            # Check if this was a facilities call and prompt for on-call tech
            if call_type == "Facilities":
                from PyQt6.QtWidgets import QMessageBox
                from logic.event_handler import create_event_chain, link_log_to_event
                
                # Ask about creating event chain
                chain_reply = QMessageBox.question(
                    self,
                    "Create Event Chain",
                    "Would you like to auto-create an event chain for these related events?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes
                )
                
                event_chain_id = None
                if chain_reply == QMessageBox.StandardButton.Yes:
                    # Create event chain with proper naming: SITE Date Time Type
                    site = data.get("Site Code", "UNKNOWN")
                    chain_date = datetime.now().strftime("%m-%d-%Y")
                    chain_time = datetime.now().strftime("%H%M")
                    chain_title = f"{site} {chain_date} {chain_time} Facilities"
                    
                    event_chain_id = create_event_chain(
                        title=chain_title,
                        description=f"Facilities issue at {site} - {data.get('Issue Subtype', '')}"
                    )
                    
                    # Link the phone log to the event chain
                    if event_chain_id and phone_log_id:
                        try:
                            link_log_to_event(
                                event_chain_id, 
                                "phone_logs",
                                phone_log_id,
                                timestamp
                            )
                        except Exception as e:
                            print(f"Error linking phone log to event chain: {e}")
                
                reply = QMessageBox.question(
                    self, 
                    "On-Call Tech",
                    "Would you like to start the on-call tech process?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    # First ask about facilities ticket
                    ticket_reply = QMessageBox.question(
                        self,
                        "Facilities Ticket",
                        "Would you like to create a facilities work order ticket?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.Yes
                    )
                    
                    if ticket_reply == QMessageBox.StandardButton.Yes:
                        # Launch facilities ticket dialog
                        from ui.facilities_ticket_ui import FacilitiesTicketDialog
                        
                        # Prepare phone data to pass
                        phone_data = {
                            "caller": data.get("Caller Name"),
                            "site_code": data.get("Site Code"),
                            "location": data.get("Location in Site"),
                            "issue_type": data.get("Issue Type"),
                            "issue_subtype": data.get("Issue Subtype"),
                            "additional_info": data.get("Additional Info")
                        }
                        
                        ticket_dialog = FacilitiesTicketDialog(
                            phone_data=phone_data,
                            event_chain_id=event_chain_id,
                            parent=self
                        )
                        
                        # The ticket dialog handles the on-call tech flow internally
                        ticket_dialog.exec()
                    else:
                        # Skip ticket, go straight to on-call tech
                        from ui.oncall_tech_ui import OnCallTechDialog
                        
                        facilities_info = {
                            "caller": data.get("Caller Name"),
                            "issue_type": data.get("Issue Type"),
                            "issue_subtype": data.get("Issue Subtype"),
                            "location": data.get("Location in Site"),
                            "additional_info": data.get("Additional Info")
                        }
                        
                        dialog = OnCallTechDialog(
                            site_code=data.get("Site Code"),
                            facilities_info=facilities_info,
                            event_chain_id=event_chain_id,
                            parent=self
                        )
                        dialog.exec()
            
            # Check if this was an Everbridge call and start the chain
            if call_type == "Everbridge":
                from PyQt6.QtWidgets import QMessageBox
                from logic.event_handler import create_event_chain, link_log_to_event
                
                # Ask about creating event chain
                chain_reply = QMessageBox.question(
                    self,
                    "Create Event Chain", 
                    "Would you like to auto-create an event chain for the Everbridge workflow?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes
                )
                
                event_chain_id = None
                if chain_reply == QMessageBox.StandardButton.Yes:
                    # Create event chain with proper naming: SITE Date Time Type
                    # For Everbridge, we might not have site yet, use ALERT
                    chain_date = datetime.now().strftime("%m-%d-%Y")
                    chain_time = datetime.now().strftime("%H%M")
                    chain_title = f"ALERT {chain_date} {chain_time} Everbridge"
                    
                    event_chain_id = create_event_chain(
                        title=chain_title,
                        description=f"Everbridge alert request from {data.get('Caller Name', 'Unknown')}"
                    )
                    
                    # Link the phone log to the event chain
                    if event_chain_id and phone_log_id:
                        try:
                            link_log_to_event(
                                event_chain_id,
                                "phone_logs",
                                phone_log_id,
                                timestamp
                            )
                        except Exception as e:
                            print(f"Error linking phone log to event chain: {e}")
                
                reply = QMessageBox.question(
                    self,
                    "Everbridge Email", 
                    "Do you need to log the Everbridge email with the alert message?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    # Launch Everbridge email workflow
                    from ui.everbridge_workflow import EverbridgeEmailDialog
                    
                    everbridge_info = {
                        "caller": data.get("Caller Name"),
                        "initial_message": data.get("Message")
                    }
                    
                    dialog = EverbridgeEmailDialog(
                        everbridge_info=everbridge_info,
                        event_chain_id=event_chain_id,
                        parent=self
                    )
                    
                    if dialog.exec():
                        # If email was logged, continue to alert
                        self.continue_everbridge_alert(dialog.get_alert_data(), event_chain_id)
                else:
                    # Skip email, go straight to alert
                    self.continue_everbridge_alert({
                        "message": data.get("Message", ""),
                        "caller": data.get("Caller Name", "")
                    }, event_chain_id)
            
            # Switch to logs tab to show the new entry
            self.main_tabs.setCurrentIndex(1)
            self.load_recent_logs()
        except Exception as e:
            show_error(self, f"Error saving log: {str(e)}")
            self.status_bar.showMessage("Error saving log")
    
    def load_recent_logs(self):
        """Load recent phone logs into the table"""
        try:
            df = log_manager.get_recent_logs('phone', limit=50)
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
                self.status_bar.showMessage(f"Loaded {len(df)} phone log entries")
            else:
                self.log_table.setRowCount(0)
                self.log_table.setColumnCount(5)
                self.log_table.setHorizontalHeaderLabels(["Date", "Time", "Caller", "Type", "Summary"])
                self.status_bar.showMessage("No phone logs found")
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
    
    def continue_everbridge_alert(self, alert_data, event_chain_id=None):
        """Continue the Everbridge workflow with alert"""
        from PyQt6.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(
            self,
            "Send Everbridge Alert",
            "Ready to log the Everbridge alert?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Import and open main window to navigate to Everbridge
            try:
                # Get the main window instance
                app = self.window()
                while app.parent():
                    app = app.parent()
                
                # Find the main window with the tab switching capability
                from PyQt6.QtWidgets import QApplication
                for widget in QApplication.topLevelWidgets():
                    if hasattr(widget, 'open_everbridge_panel'):
                        # Call the method to open Everbridge panel
                        widget.open_everbridge_panel()
                        
                        # After a brief delay, pre-fill the data
                        from PyQt6.QtCore import QTimer
                        def prefill_data():
                            # Find the Everbridge panel that was just opened
                            for child in widget.findChildren(QWidget):
                                if child.__class__.__name__ == "EverbridgePanel":
                                    if alert_data.get("message"):
                                        child.message_box.setText(alert_data["message"])
                                    child.message_box.setFocus()
                                    
                                    # Store event chain ID if available
                                    if event_chain_id:
                                        child.event_chain_id = event_chain_id
                                    break
                        
                        QTimer.singleShot(100, prefill_data)
                        break
                else:
                    # Fallback: open as standalone window
                    from ui.everbridge_ui import EverbridgePanel
                    everbridge_panel = EverbridgePanel()
                    
                    if alert_data.get("message"):
                        everbridge_panel.message_box.setText(alert_data["message"])
                    
                    if event_chain_id:
                        everbridge_panel.event_chain_id = event_chain_id
                    
                    everbridge_panel.show()
                    
            except Exception as e:
                print(f"Error navigating to Everbridge: {e}")
                # Fallback to standalone window
                from ui.everbridge_ui import EverbridgePanel
                everbridge_panel = EverbridgePanel()
                
                if alert_data.get("message"):
                    everbridge_panel.message_box.setText(alert_data["message"])
                
                if event_chain_id:
                    everbridge_panel.event_chain_id = event_chain_id
                
                everbridge_panel.show()
    
    def export_logs(self):
        """Export logs to file"""
        from PyQt6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Phone Logs", "phone_logs_export.xlsx", 
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