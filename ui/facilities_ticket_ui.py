"""
Facilities Ticket UI - Integrates with phone call workflow for smooth data transfer
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTextEdit, QGroupBox, QComboBox, QSplitter,
    QWidget, QMessageBox, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QShortcut, QKeySequence
from datetime import datetime
from database import insert_phone_log  # We'll track this as a phone log type
from ui.styles import (
    Fonts, Colors,
    INPUT_STYLE, get_button_style,
    show_error, show_success, make_accessible
)
from app_settings import app_settings
from log_manager import log_manager
from logic.event_handler import link_log_to_event
import random
import string


class FacilitiesTicketDialog(QDialog):
    """Dialog for creating facilities ticket with data from phone call"""
    
    # Signal to notify when ticket is created
    ticket_created = pyqtSignal(dict)
    
    def __init__(self, phone_data=None, event_chain_id=None, parent=None):
        super().__init__(parent)
        self.phone_data = phone_data or {}
        self.event_chain_id = event_chain_id
        
        # Generate ticket number
        self.ticket_number = self.generate_ticket_number()
        
        self.setModal(True)
        self.setWindowTitle("Facilities Ticket Creation")
        self.setMinimumSize(900, 700)
        
        self.init_ui()
        self.setup_shortcuts()
        
        # Auto-fill from phone data
        if self.phone_data:
            self.auto_fill_from_phone()
    
    def generate_ticket_number(self):
        """Generate a unique facilities ticket number"""
        date_part = datetime.now().strftime("%Y%m%d")
        time_part = datetime.now().strftime("%H%M")
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        return f"FAC-{date_part}-{time_part}-{random_part}"
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 20, 30, 20)
        
        # Title
        title = QLabel("Facilities Work Order / Ticket")
        title.setFont(Fonts.TITLE)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #e0e0e0; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Show if we're in a chain
        if self.phone_data:
            chain_info = QLabel(f"📞 Following up from phone call: {self.phone_data.get('caller', 'Unknown')}")
            chain_info.setFont(Fonts.NORMAL)
            chain_info.setStyleSheet("color: #4caf50; padding: 5px; background-color: #1a1a1a; border-radius: 5px;")
            layout.addWidget(chain_info)
        
        # Ticket Information Group
        ticket_group = QGroupBox("Ticket Information")
        ticket_group.setStyleSheet("""
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
        ticket_layout = QVBoxLayout()
        
        # Ticket Number (read-only)
        ticket_num_layout = QHBoxLayout()
        ticket_num_label = QLabel("Ticket Number:")
        ticket_num_label.setFont(Fonts.LABEL)
        ticket_num_label.setMinimumWidth(150)
        ticket_num_layout.addWidget(ticket_num_label)
        
        self.ticket_field = QLineEdit(self.ticket_number)
        self.ticket_field.setFont(Fonts.NORMAL)
        self.ticket_field.setStyleSheet(INPUT_STYLE)
        self.ticket_field.setReadOnly(True)
        make_accessible(self.ticket_field, "Auto-generated ticket number")
        ticket_num_layout.addWidget(self.ticket_field)
        
        ticket_layout.addLayout(ticket_num_layout)
        
        # Date/Time
        time_layout = QHBoxLayout()
        time_label = QLabel("Date/Time:")
        time_label.setFont(Fonts.LABEL)
        time_label.setMinimumWidth(150)
        time_layout.addWidget(time_label)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_field = QLineEdit(timestamp)
        self.time_field.setFont(Fonts.NORMAL)
        self.time_field.setStyleSheet(INPUT_STYLE)
        self.time_field.setReadOnly(True)
        make_accessible(self.time_field, "Ticket creation time")
        time_layout.addWidget(self.time_field)
        
        ticket_layout.addLayout(time_layout)
        
        # Priority Level
        priority_layout = QHBoxLayout()
        priority_label = QLabel("Priority:")
        priority_label.setFont(Fonts.LABEL)
        priority_label.setMinimumWidth(150)
        priority_layout.addWidget(priority_label)
        
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Low", "Medium", "High", "Urgent", "Emergency"])
        self.priority_combo.setCurrentText("Medium")  # Default
        self.priority_combo.setFont(Fonts.NORMAL)
        self.priority_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                background-color: #1a1a1a;
                color: #e0e0e0;
                border: 1px solid #333333;
                border-radius: 4px;
            }
            QComboBox:hover {
                border: 1px solid #5a5a5a;
            }
        """)
        make_accessible(self.priority_combo, "Select ticket priority")
        priority_layout.addWidget(self.priority_combo)
        
        ticket_layout.addLayout(priority_layout)
        
        ticket_group.setLayout(ticket_layout)
        layout.addWidget(ticket_group)
        
        # Location Information Group
        location_group = QGroupBox("Location Information")
        location_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #333333;
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
            }
        """)
        location_layout = QVBoxLayout()
        
        # Site Code
        site_layout = QHBoxLayout()
        site_label = QLabel("Site Code:")
        site_label.setFont(Fonts.LABEL)
        site_label.setMinimumWidth(150)
        site_layout.addWidget(site_label)
        
        self.site_field = QLineEdit()
        self.site_field.setFont(Fonts.NORMAL)
        self.site_field.setStyleSheet(INPUT_STYLE)
        self.site_field.setPlaceholderText("e.g., SEP, FSP, COB")
        make_accessible(self.site_field, "Site code")
        site_layout.addWidget(self.site_field)
        
        location_layout.addLayout(site_layout)
        
        # Location within Site
        location_detail_layout = QHBoxLayout()
        location_detail_label = QLabel("Specific Location:")
        location_detail_label.setFont(Fonts.LABEL)
        location_detail_label.setMinimumWidth(150)
        location_detail_layout.addWidget(location_detail_label)
        
        self.location_field = QLineEdit()
        self.location_field.setFont(Fonts.NORMAL)
        self.location_field.setStyleSheet(INPUT_STYLE)
        self.location_field.setPlaceholderText("e.g., Building 5, Room 302")
        make_accessible(self.location_field, "Specific location within site")
        location_detail_layout.addWidget(self.location_field)
        
        location_layout.addLayout(location_detail_layout)
        
        location_group.setLayout(location_layout)
        layout.addWidget(location_group)
        
        # Issue Information Group
        issue_group = QGroupBox("Issue Details")
        issue_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #333333;
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
            }
        """)
        issue_layout = QVBoxLayout()
        
        # Issue Type
        issue_type_layout = QHBoxLayout()
        issue_type_label = QLabel("Issue Type:")
        issue_type_label.setFont(Fonts.LABEL)
        issue_type_label.setMinimumWidth(150)
        issue_type_layout.addWidget(issue_type_label)
        
        self.issue_type_field = QLineEdit()
        self.issue_type_field.setFont(Fonts.NORMAL)
        self.issue_type_field.setStyleSheet(INPUT_STYLE)
        self.issue_type_field.setPlaceholderText("e.g., Plumbing, Electrical, HVAC")
        make_accessible(self.issue_type_field, "Type of facilities issue")
        issue_type_layout.addWidget(self.issue_type_field)
        
        issue_layout.addLayout(issue_type_layout)
        
        # Issue Subtype
        issue_subtype_layout = QHBoxLayout()
        issue_subtype_label = QLabel("Specific Issue:")
        issue_subtype_label.setFont(Fonts.LABEL)
        issue_subtype_label.setMinimumWidth(150)
        issue_subtype_layout.addWidget(issue_subtype_label)
        
        self.issue_subtype_field = QLineEdit()
        self.issue_subtype_field.setFont(Fonts.NORMAL)
        self.issue_subtype_field.setStyleSheet(INPUT_STYLE)
        self.issue_subtype_field.setPlaceholderText("e.g., Clogged toilet, Power outage")
        make_accessible(self.issue_subtype_field, "Specific issue description")
        issue_subtype_layout.addWidget(self.issue_subtype_field)
        
        issue_layout.addLayout(issue_subtype_layout)
        
        issue_group.setLayout(issue_layout)
        layout.addWidget(issue_group)
        
        # Requestor Information
        requestor_group = QGroupBox("Requestor Information")
        requestor_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #333333;
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
            }
        """)
        requestor_layout = QVBoxLayout()
        
        # Requestor Name
        requestor_name_layout = QHBoxLayout()
        requestor_name_label = QLabel("Requestor Name:")
        requestor_name_label.setFont(Fonts.LABEL)
        requestor_name_label.setMinimumWidth(150)
        requestor_name_layout.addWidget(requestor_name_label)
        
        self.requestor_field = QLineEdit()
        self.requestor_field.setFont(Fonts.NORMAL)
        self.requestor_field.setStyleSheet(INPUT_STYLE)
        self.requestor_field.setPlaceholderText("Name of person requesting service")
        make_accessible(self.requestor_field, "Person who requested the service")
        requestor_name_layout.addWidget(self.requestor_field)
        
        requestor_layout.addLayout(requestor_name_layout)
        
        # Contact Number
        contact_layout = QHBoxLayout()
        contact_label = QLabel("Contact Number:")
        contact_label.setFont(Fonts.LABEL)
        contact_label.setMinimumWidth(150)
        contact_layout.addWidget(contact_label)
        
        self.contact_field = QLineEdit()
        self.contact_field.setFont(Fonts.NORMAL)
        self.contact_field.setStyleSheet(INPUT_STYLE)
        self.contact_field.setPlaceholderText("Phone number (optional)")
        make_accessible(self.contact_field, "Contact phone number")
        contact_layout.addWidget(self.contact_field)
        
        requestor_layout.addLayout(contact_layout)
        
        requestor_group.setLayout(requestor_layout)
        layout.addWidget(requestor_group)
        
        # Description/Notes
        notes_group = QGroupBox("Work Order Description")
        notes_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #333333;
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
            }
        """)
        notes_layout = QVBoxLayout()
        
        self.description_field = QTextEdit()
        self.description_field.setFont(Fonts.NORMAL)
        self.description_field.setStyleSheet(INPUT_STYLE)
        self.description_field.setPlaceholderText("Enter detailed description of the work required...")
        self.description_field.setMaximumHeight(150)
        make_accessible(self.description_field, "Detailed work order description")
        
        notes_layout.addWidget(self.description_field)
        
        notes_group.setLayout(notes_layout)
        layout.addWidget(notes_group)
        
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Create Ticket & Continue (Ctrl+S)")
        save_btn.setFont(Fonts.BUTTON_LARGE)
        save_btn.setStyleSheet(get_button_style(Colors.SUCCESS, 50))
        save_btn.clicked.connect(self.save_ticket)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel (Esc)")
        cancel_btn.setFont(Fonts.BUTTON)
        cancel_btn.setStyleSheet(get_button_style("#757575", 50))
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def auto_fill_from_phone(self):
        """Auto-fill fields from phone call data"""
        # Site code
        if self.phone_data.get('site_code'):
            self.site_field.setText(self.phone_data['site_code'])
        
        # Location within site
        if self.phone_data.get('location'):
            self.location_field.setText(self.phone_data['location'])
        
        # Issue type and subtype
        if self.phone_data.get('issue_type'):
            self.issue_type_field.setText(self.phone_data['issue_type'])
        
        if self.phone_data.get('issue_subtype'):
            self.issue_subtype_field.setText(self.phone_data['issue_subtype'])
        
        # Requestor
        if self.phone_data.get('caller'):
            self.requestor_field.setText(self.phone_data['caller'])
        
        # Auto-generate description
        self.generate_description()
        
        # Set priority based on issue
        if self.phone_data.get('issue_subtype'):
            issue = self.phone_data['issue_subtype'].lower()
            if any(word in issue for word in ['emergency', 'leak', 'flood', 'power', 'gas']):
                self.priority_combo.setCurrentText("High")
            elif any(word in issue for word in ['broken', 'failed', 'not working']):
                self.priority_combo.setCurrentText("Medium")
    
    def generate_description(self):
        """Generate a structured description from available data"""
        parts = []
        
        # Add caller info
        caller = self.phone_data.get('caller', 'Staff member')
        parts.append(f"{caller} reported")
        
        # Add issue type
        issue_type = self.phone_data.get('issue_type', 'facilities issue')
        issue_subtype = self.phone_data.get('issue_subtype', '')
        if issue_subtype:
            parts.append(f"{issue_subtype}")
        else:
            parts.append(f"{issue_type}")
        
        # Add location
        parts.append("occurring in")
        location = self.phone_data.get('location', 'unspecified location')
        parts.append(location)
        
        # Add site
        parts.append("at")
        site = self.phone_data.get('site_code', 'site')
        parts.append(site)
        
        # Combine
        description = " ".join(parts) + "."
        
        # Add any additional info
        if self.phone_data.get('additional_info'):
            description += f"\n\nAdditional details: {self.phone_data['additional_info']}"
        
        # Add timestamp
        description += f"\n\nReported at: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        self.description_field.setPlainText(description)
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        QShortcut(QKeySequence("Ctrl+S"), self, self.save_ticket)
        QShortcut(QKeySequence("Escape"), self, self.reject)
    
    def save_ticket(self):
        """Save the facilities ticket"""
        try:
            # Get all values
            ticket_data = {
                'ticket_number': self.ticket_field.text(),
                'timestamp': self.time_field.text(),
                'priority': self.priority_combo.currentText(),
                'site_code': self.site_field.text(),
                'location': self.location_field.text(),
                'issue_type': self.issue_type_field.text(),
                'issue_subtype': self.issue_subtype_field.text(),
                'requestor': self.requestor_field.text(),
                'contact': self.contact_field.text(),
                'description': self.description_field.toPlainText()
            }
            
            # Validate required fields
            if not ticket_data['site_code']:
                show_error(self, "Please enter a site code")
                self.site_field.setFocus()
                return
            
            if not ticket_data['issue_type']:
                show_error(self, "Please enter the issue type")
                self.issue_type_field.setFocus()
                return
            
            # Save as a phone log entry with type "Facilities Ticket"
            log_id = insert_phone_log(
                call_type="Facilities Ticket",
                caller_name=ticket_data['requestor'],
                site_code=ticket_data['site_code'],
                ticket_number=ticket_data['ticket_number'],
                address=ticket_data['location'],
                alarm_type=None,
                issue_type=ticket_data['issue_type'],
                issue_subtype=ticket_data['issue_subtype'],
                message=ticket_data['description'],
                timestamp=ticket_data['timestamp']
            )
            
            # Link to event chain if we have one
            if self.event_chain_id and log_id:
                try:
                    link_log_to_event(
                        self.event_chain_id,
                        "phone_logs",
                        log_id,
                        ticket_data['timestamp']
                    )
                except Exception as e:
                    print(f"Error linking to event chain: {e}")
            
            # Also save to Excel log
            phone_data = {
                'caller': ticket_data['requestor'],
                'number': ticket_data['contact'],
                'company': ticket_data['site_code'],
                'type': 'Facilities Ticket',
                'duration': '',
                'summary': f"{ticket_data['issue_type']}: {ticket_data['issue_subtype']}",
                'action_items': ticket_data['ticket_number']
            }
            
            try:
                log_manager.add_phone_log(phone_data)
            except Exception as e:
                print(f"Error saving to Excel: {e}")
            
            # Emit signal with ticket data
            self.ticket_created.emit(ticket_data)
            
            show_success(self, f"Facilities ticket created!\n\nTicket #: {ticket_data['ticket_number']}")
            
            # Check if we should continue to on-call tech
            reply = QMessageBox.question(
                self,
                "On-Call Tech",
                "Would you like to notify the on-call technician?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                from ui.oncall_tech_ui import OnCallTechDialog
                
                facilities_info = {
                    "caller": ticket_data['requestor'],
                    "issue_type": ticket_data['issue_type'],
                    "issue_subtype": ticket_data['issue_subtype'],
                    "location": ticket_data['location'],
                    "additional_info": ticket_data['description'],
                    "ticket_number": ticket_data['ticket_number']
                }
                
                dialog = OnCallTechDialog(
                    site_code=ticket_data['site_code'],
                    facilities_info=facilities_info,
                    event_chain_id=self.event_chain_id,
                    parent=self
                )
                
                if dialog.exec():
                    self.accept()
                else:
                    self.accept()
            else:
                self.accept()
            
        except Exception as e:
            show_error(self, f"Error creating ticket: {str(e)}")


class FacilitiesSplitView(QWidget):
    """Split view for simultaneous phone call and ticket entry"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Create splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side - Phone call entry (simplified)
        phone_widget = self.create_phone_widget()
        splitter.addWidget(phone_widget)
        
        # Right side - Facilities ticket
        ticket_widget = self.create_ticket_widget()
        splitter.addWidget(ticket_widget)
        
        # Set initial sizes (50/50)
        splitter.setSizes([450, 450])
        
        layout.addWidget(splitter)
        self.setLayout(layout)
    
    def create_phone_widget(self):
        """Create simplified phone call entry widget"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel("Phone Call Information")
        title.setFont(Fonts.LABEL)
        title.setStyleSheet("color: #e0e0e0; padding: 10px; background-color: #2a2a2a;")
        layout.addWidget(title)
        
        # Add phone fields here (simplified version)
        # This would include caller, issue type, etc.
        
        widget.setLayout(layout)
        return widget
    
    def create_ticket_widget(self):
        """Create facilities ticket widget"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel("Facilities Ticket")
        title.setFont(Fonts.LABEL)
        title.setStyleSheet("color: #e0e0e0; padding: 10px; background-color: #2a2a2a;")
        layout.addWidget(title)
        
        # Add ticket fields here
        
        widget.setLayout(layout)
        return widget