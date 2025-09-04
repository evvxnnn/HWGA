from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton,
    QHBoxLayout, QTextEdit, QGroupBox, QLineEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QShortcut, QKeySequence
from datetime import datetime
from database import insert_phone_log
from ui.styles import (
    Fonts, Colors,
    INPUT_STYLE, get_button_style,
    show_error, show_success, make_accessible
)
from app_settings import app_settings
from log_manager import log_manager


class OnCallTechDialog(QDialog):
    """Dialog for logging on-call tech notification"""
    
    def __init__(self, site_code=None, facilities_info=None, event_chain_id=None, parent=None):
        super().__init__(parent)
        self.site_code = site_code
        self.facilities_info = facilities_info
        self.event_chain_id = event_chain_id
        
        # Generate facilities ticket number
        self.ticket_number = f"FAC-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Make dialog modal
        self.setModal(True)
        self.setWindowTitle("On-Call Tech Notification")
        self.setMinimumSize(700, 600)
        
        self.init_ui()
        self.setup_shortcuts()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 20, 30, 20)
        
        # Title
        title = QLabel("On-Call Tech Log Entry")
        title.setFont(Fonts.TITLE)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #e0e0e0; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Standard Phone Log Fields Group
        fields_group = QGroupBox("Call Information")
        fields_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #5a5a5a;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: #1a1a1a;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #e0e0e0;
                font-weight: bold;
            }
        """)
        fields_layout = QVBoxLayout()
        
        # Timestamp field
        time_layout = QHBoxLayout()
        time_label = QLabel("Call Time:")
        time_label.setFont(Fonts.LABEL)
        time_label.setMinimumWidth(150)
        time_layout.addWidget(time_label)
        
        # Auto-fill timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.timestamp_field = QLineEdit(timestamp)
        self.timestamp_field.setFont(Fonts.NORMAL)
        self.timestamp_field.setStyleSheet(INPUT_STYLE)
        make_accessible(self.timestamp_field, "Time of the call to on-call tech")
        time_layout.addWidget(self.timestamp_field)
        
        now_btn = QPushButton("Update to Now")
        now_btn.setFont(Fonts.BUTTON)
        now_btn.setStyleSheet(get_button_style(Colors.INFO, 40))
        now_btn.clicked.connect(self.set_current_time)
        make_accessible(now_btn, "Set to current time")
        time_layout.addWidget(now_btn)
        
        fields_layout.addLayout(time_layout)
        
        # Caller Name (On-Call Tech Name) - Auto-filled
        name_layout = QHBoxLayout()
        name_label = QLabel("On-Call Tech:")
        name_label.setFont(Fonts.LABEL)
        name_label.setMinimumWidth(150)
        name_layout.addWidget(name_label)
        
        # Get on-call contact for this site
        self.get_oncall_contact()
        
        self.tech_name_field = QLineEdit(self.tech_name)
        self.tech_name_field.setFont(Fonts.NORMAL)
        self.tech_name_field.setStyleSheet(INPUT_STYLE)
        self.tech_name_field.setReadOnly(True)
        make_accessible(self.tech_name_field, "Name of the on-call technician")
        name_layout.addWidget(self.tech_name_field)
        
        fields_layout.addLayout(name_layout)
        
        # Phone Number
        phone_layout = QHBoxLayout()
        phone_label = QLabel("Phone Number:")
        phone_label.setFont(Fonts.LABEL)
        phone_label.setMinimumWidth(150)
        phone_layout.addWidget(phone_label)
        
        self.tech_phone_field = QLineEdit(self.tech_phone)
        self.tech_phone_field.setFont(Fonts.NORMAL)
        self.tech_phone_field.setStyleSheet(INPUT_STYLE)
        self.tech_phone_field.setReadOnly(True)
        make_accessible(self.tech_phone_field, "Phone number of the on-call technician")
        phone_layout.addWidget(self.tech_phone_field)
        
        fields_layout.addLayout(phone_layout)
        
        # Facilities Ticket Number - Use provided or auto-generate
        ticket_layout = QHBoxLayout()
        ticket_label = QLabel("Facilities Ticket #:")
        ticket_label.setFont(Fonts.LABEL)
        ticket_label.setMinimumWidth(150)
        ticket_layout.addWidget(ticket_label)
        
        # Use ticket number from facilities_info if available
        if self.facilities_info and self.facilities_info.get('ticket_number'):
            ticket_num = self.facilities_info['ticket_number']
        else:
            ticket_num = self.ticket_number
        
        self.ticket_field = QLineEdit(ticket_num)
        self.ticket_field.setFont(Fonts.NORMAL)
        self.ticket_field.setStyleSheet(INPUT_STYLE)
        make_accessible(self.ticket_field, "Facilities ticket tracking number")
        ticket_layout.addWidget(self.ticket_field)
        
        fields_layout.addLayout(ticket_layout)
        
        # Site Code
        site_layout = QHBoxLayout()
        site_label = QLabel("Site Code:")
        site_label.setFont(Fonts.LABEL)
        site_label.setMinimumWidth(150)
        site_layout.addWidget(site_label)
        
        self.site_field = QLineEdit(self.site_code or "")
        self.site_field.setFont(Fonts.NORMAL)
        self.site_field.setStyleSheet(INPUT_STYLE)
        self.site_field.setReadOnly(True)
        make_accessible(self.site_field, "Site code for the facilities issue")
        site_layout.addWidget(self.site_field)
        
        fields_layout.addLayout(site_layout)
        
        fields_group.setLayout(fields_layout)
        layout.addWidget(fields_group)
        
        # Facilities Issue Details (if coming from facilities call)
        if self.facilities_info:
            info_group = QGroupBox("Related Facilities Issue")
            info_group.setStyleSheet("""
                QGroupBox {
                    border: 1px solid #333333;
                    border-radius: 5px;
                    margin-top: 10px;
                    padding-top: 10px;
                    background-color: #1a1a1a;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                    color: #b0b0b0;
                }
            """)
            info_layout = QVBoxLayout()
            
            # Show facilities details in a formatted way
            details_text = ""
            if self.facilities_info:
                details_text += f"Issue Type: {self.facilities_info.get('issue_type', 'N/A')}\n"
                details_text += f"Specific Issue: {self.facilities_info.get('issue_subtype', 'N/A')}\n"
                details_text += f"Location in Site: {self.facilities_info.get('location', 'N/A')}\n"
                details_text += f"Original Caller: {self.facilities_info.get('caller', 'N/A')}\n"
                if self.facilities_info.get('additional_info'):
                    details_text += f"Additional Info: {self.facilities_info.get('additional_info')}"
            
            details_label = QLabel(details_text)
            details_label.setFont(Fonts.NORMAL)
            details_label.setStyleSheet("color: #b0b0b0; padding: 10px;")
            info_layout.addWidget(details_label)
            
            info_group.setLayout(info_layout)
            layout.addWidget(info_group)
        
        # Call Notes/Summary
        notes_group = QGroupBox("Call Summary")
        notes_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #333333;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #1a1a1a;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #e0e0e0;
            }
        """)
        notes_layout = QVBoxLayout()
        
        self.notes_text = QTextEdit()
        self.notes_text.setFont(Fonts.NORMAL)
        self.notes_text.setStyleSheet(INPUT_STYLE)
        self.notes_text.setPlaceholderText("Enter summary of the call to the on-call tech...")
        self.notes_text.setMaximumHeight(120)
        
        # Pre-fill with facilities info if available
        if self.facilities_info:
            pre_notes = f"Called regarding: {self.facilities_info.get('issue_subtype', 'N/A')} at {self.facilities_info.get('location', 'N/A')}.\n"
            pre_notes += f"Tech notified and will respond."
            self.notes_text.setPlainText(pre_notes)
        
        notes_layout.addWidget(self.notes_text)
        notes_group.setLayout(notes_layout)
        layout.addWidget(notes_group)
        
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save On-Call Tech Log (Ctrl+S)")
        save_btn.setFont(Fonts.BUTTON_LARGE)
        save_btn.setStyleSheet(get_button_style(Colors.SUCCESS, 50))
        save_btn.clicked.connect(self.save_log)
        button_layout.addWidget(save_btn)
        
        skip_btn = QPushButton("Skip (Esc)")
        skip_btn.setFont(Fonts.BUTTON)
        skip_btn.setStyleSheet(get_button_style("#757575", 50))
        skip_btn.clicked.connect(self.reject)
        button_layout.addWidget(skip_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def get_oncall_contact(self):
        """Get the on-call contact info for the site"""
        dropdown_settings = app_settings.get("dropdown_options", {})
        oncall_contacts = dropdown_settings.get("oncall_contacts", {
            "SEP": {"name": "Gabe Jones", "phone": "555-0101"},
            "FSP": {"name": "Logan Tyndall", "phone": "555-0102"},
            "COB": {"name": "Evan Wainscott", "phone": "555-0103"}
        })
        
        # Default values
        self.tech_name = "Unknown"
        self.tech_phone = "Unknown"
        
        if self.site_code:
            # Check if site code contains any of the oncall keys
            for key, contact in oncall_contacts.items():
                if key in self.site_code.upper():
                    self.tech_name = contact.get("name", "Unknown")
                    self.tech_phone = contact.get("phone", "Unknown")
                    break
    
    def set_current_time(self):
        """Update timestamp to current time"""
        self.timestamp_field.setText(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        QShortcut(QKeySequence("Ctrl+S"), self, self.save_log)
        QShortcut(QKeySequence("Escape"), self, self.reject)
        QShortcut(QKeySequence("Ctrl+T"), self, self.set_current_time)
    
    def save_log(self):
        """Save the on-call tech log"""
        try:
            # Get values from fields
            timestamp = self.timestamp_field.text()
            notes = self.notes_text.toPlainText()
            ticket_number = self.ticket_field.text()
            tech_name = self.tech_name_field.text()
            tech_phone = self.tech_phone_field.text()
            site_code = self.site_field.text()
            
            # Save to database
            insert_phone_log(
                call_type="On-Call Tech",
                caller_name=tech_name,  # This is the tech's name
                site_code=site_code,
                ticket_number=ticket_number,
                address=None,
                alarm_type=None,
                issue_type=self.facilities_info.get("issue_type") if self.facilities_info else None,
                issue_subtype=self.facilities_info.get("issue_subtype") if self.facilities_info else None,
                message=notes,
                timestamp=timestamp
            )
            
            # Also save to Excel log
            phone_data = {
                'caller': tech_name,
                'number': tech_phone,
                'company': site_code or '',
                'type': 'On-Call Tech',
                'duration': '',
                'summary': notes,
                'action_items': ticket_number or ''
            }
            
            try:
                log_manager.add_phone_log(phone_data)
            except Exception as e:
                print(f"Error saving to Excel: {e}")
            
            show_success(self, f"On-call tech log saved!\n\nTech: {tech_name}\nPhone: {tech_phone}\nTicket: {ticket_number}")
            self.accept()
            
        except Exception as e:
            show_error(self, f"Error saving log: {str(e)}")