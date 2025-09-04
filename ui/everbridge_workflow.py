"""
Everbridge workflow dialogs for managing the complete alert chain:
Phone Call -> Email -> Alert -> Notification Confirmation
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton,
    QHBoxLayout, QTextEdit, QGroupBox, QLineEdit,
    QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QShortcut, QKeySequence
from datetime import datetime
from database import insert_email_log
from ui.styles import (
    Fonts, Colors,
    INPUT_STYLE, get_button_style,
    show_error, show_success, make_accessible
)
from app_settings import app_settings
from log_manager import log_manager


class EverbridgeEmailDialog(QDialog):
    """Dialog for logging Everbridge email with alert message"""
    
    def __init__(self, everbridge_info=None, event_chain_id=None, parent=None):
        super().__init__(parent)
        self.everbridge_info = everbridge_info or {}
        self.event_chain_id = event_chain_id
        self.alert_data = {}
        
        self.setModal(True)
        self.setWindowTitle("Everbridge Email Log")
        self.setMinimumSize(700, 600)
        
        self.init_ui()
        self.setup_shortcuts()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 20, 30, 20)
        
        # Title
        title = QLabel("Everbridge Email - Alert Message")
        title.setFont(Fonts.TITLE)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #e0e0e0; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Info about the call
        if self.everbridge_info.get("caller"):
            info_text = f"Following up on call from: {self.everbridge_info['caller']}"
            info_label = QLabel(info_text)
            info_label.setFont(Fonts.NORMAL)
            info_label.setStyleSheet("color: #b0b0b0; padding: 5px;")
            layout.addWidget(info_label)
        
        # Email Details Group
        email_group = QGroupBox("Email Information")
        email_group.setStyleSheet("""
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
        email_layout = QVBoxLayout()
        
        # From field
        from_layout = QHBoxLayout()
        from_label = QLabel("From:")
        from_label.setFont(Fonts.LABEL)
        from_label.setMinimumWidth(100)
        from_layout.addWidget(from_label)
        
        self.from_field = QLineEdit()
        self.from_field.setFont(Fonts.NORMAL)
        self.from_field.setStyleSheet(INPUT_STYLE)
        self.from_field.setPlaceholderText("Sender's email or name")
        if self.everbridge_info.get("caller"):
            self.from_field.setText(self.everbridge_info["caller"])
        make_accessible(self.from_field, "Email sender")
        from_layout.addWidget(self.from_field)
        
        email_layout.addLayout(from_layout)
        
        # Subject field
        subject_layout = QHBoxLayout()
        subject_label = QLabel("Subject:")
        subject_label.setFont(Fonts.LABEL)
        subject_label.setMinimumWidth(100)
        subject_layout.addWidget(subject_label)
        
        self.subject_field = QLineEdit()
        self.subject_field.setFont(Fonts.NORMAL)
        self.subject_field.setStyleSheet(INPUT_STYLE)
        self.subject_field.setPlaceholderText("Email subject line")
        self.subject_field.setText("Everbridge Alert Request")
        make_accessible(self.subject_field, "Email subject")
        subject_layout.addWidget(self.subject_field)
        
        email_layout.addLayout(subject_layout)
        
        # Time received
        time_layout = QHBoxLayout()
        time_label = QLabel("Received:")
        time_label.setFont(Fonts.LABEL)
        time_label.setMinimumWidth(100)
        time_layout.addWidget(time_label)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_field = QLineEdit(timestamp)
        self.time_field.setFont(Fonts.NORMAL)
        self.time_field.setStyleSheet(INPUT_STYLE)
        make_accessible(self.time_field, "Time email was received")
        time_layout.addWidget(self.time_field)
        
        email_layout.addLayout(time_layout)
        
        email_group.setLayout(email_layout)
        layout.addWidget(email_group)
        
        # Alert Message Group
        message_group = QGroupBox("Alert Message to Send")
        message_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #ff9800;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: #1a1a1a;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #ff9800;
                font-weight: bold;
            }
        """)
        message_layout = QVBoxLayout()
        
        self.message_text = QTextEdit()
        self.message_text.setFont(Fonts.NORMAL)
        self.message_text.setStyleSheet(INPUT_STYLE)
        self.message_text.setPlaceholderText("Enter the full alert message that needs to be sent...")
        self.message_text.setMinimumHeight(200)
        
        # Pre-fill if we have initial message
        if self.everbridge_info.get("initial_message"):
            self.message_text.setPlainText(self.everbridge_info["initial_message"])
        
        message_layout.addWidget(self.message_text)
        
        # Character count
        self.char_count_label = QLabel("0 characters")
        self.char_count_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.char_count_label.setStyleSheet("color: #666; font-style: italic;")
        self.message_text.textChanged.connect(self.update_char_count)
        message_layout.addWidget(self.char_count_label)
        
        message_group.setLayout(message_layout)
        layout.addWidget(message_group)
        
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save Email & Continue to Alert")
        save_btn.setFont(Fonts.BUTTON_LARGE)
        save_btn.setStyleSheet(get_button_style(Colors.SUCCESS, 50))
        save_btn.clicked.connect(self.save_and_continue)
        button_layout.addWidget(save_btn)
        
        skip_btn = QPushButton("Skip Email")
        skip_btn.setFont(Fonts.BUTTON)
        skip_btn.setStyleSheet(get_button_style("#757575", 50))
        skip_btn.clicked.connect(self.reject)
        button_layout.addWidget(skip_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # Initial char count
        self.update_char_count()
    
    def update_char_count(self):
        """Update character count label"""
        count = len(self.message_text.toPlainText())
        self.char_count_label.setText(f"{count} characters")
        
        # Change color if message is very long
        if count > 500:
            self.char_count_label.setStyleSheet("color: #F44336; font-style: italic;")
        elif count > 300:
            self.char_count_label.setStyleSheet("color: #FF9800; font-style: italic;")
        else:
            self.char_count_label.setStyleSheet("color: #666; font-style: italic;")
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        QShortcut(QKeySequence("Ctrl+S"), self, self.save_and_continue)
        QShortcut(QKeySequence("Escape"), self, self.reject)
    
    def save_and_continue(self):
        """Save the email log and prepare alert data"""
        try:
            # Get values
            sender = self.from_field.text().strip()
            subject = self.subject_field.text().strip()
            message = self.message_text.toPlainText().strip()
            timestamp = self.time_field.text()
            
            # Validation
            if not sender:
                show_error(self, "Please enter the sender information")
                self.from_field.setFocus()
                return
            
            if not message:
                show_error(self, "Please enter the alert message")
                self.message_text.setFocus()
                return
            
            # Save email log entry (as Everbridge Alert type)
            insert_email_log(
                log_type="Everbridge Alert",
                sender=sender,
                recipient=None,
                subject=subject,
                timestamp=timestamp,
                extra_field=message[:500],  # Store first 500 chars in extra field
                msg_path="Email"
            )
            
            # Also save to Excel
            email_data = {
                'from': sender,
                'subject': subject,
                'category': 'Everbridge Alert',
                'site': '',
                'priority': 'High',
                'notes': f"Alert message: {message[:200]}..."
            }
            
            try:
                log_manager.add_email_log(email_data)
            except Exception as e:
                print(f"Error saving to Excel: {e}")
            
            # Store alert data to pass along
            self.alert_data = {
                "message": message,
                "sender": sender,
                "subject": subject
            }
            
            show_success(self, "Email logged successfully!")
            self.accept()
            
        except Exception as e:
            show_error(self, f"Error saving email log: {str(e)}")
    
    def get_alert_data(self):
        """Get the alert data to pass to next step"""
        return self.alert_data


class NotificationConfirmationDialog(QDialog):
    """Dialog for logging notification confirmation after alert is sent"""
    
    def __init__(self, alert_info=None, parent=None):
        super().__init__(parent)
        self.alert_info = alert_info or {}
        
        self.setModal(True)
        self.setWindowTitle("Notification Confirmation")
        self.setMinimumSize(600, 450)
        
        self.init_ui()
        self.setup_shortcuts()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 20, 30, 20)
        
        # Title
        title = QLabel("Notification/Confirmation Email")
        title.setFont(Fonts.TITLE)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #e0e0e0; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Info
        info_label = QLabel("Log the confirmation email sent to notify that the alert was dispatched")
        info_label.setFont(Fonts.NORMAL)
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("color: #b0b0b0; margin-bottom: 10px;")
        layout.addWidget(info_label)
        
        # Notification Details Group
        notif_group = QGroupBox("Confirmation Details")
        notif_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #4caf50;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: #1a1a1a;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #4caf50;
                font-weight: bold;
            }
        """)
        notif_layout = QVBoxLayout()
        
        # Recipient field
        recipient_layout = QHBoxLayout()
        recipient_label = QLabel("Sent To:")
        recipient_label.setFont(Fonts.LABEL)
        recipient_label.setMinimumWidth(100)
        recipient_layout.addWidget(recipient_label)
        
        self.recipient_field = QLineEdit()
        self.recipient_field.setFont(Fonts.NORMAL)
        self.recipient_field.setStyleSheet(INPUT_STYLE)
        self.recipient_field.setPlaceholderText("Email address or name of recipient")
        # Pre-fill with original sender if available
        if self.alert_info.get("original_sender"):
            self.recipient_field.setText(self.alert_info["original_sender"])
        make_accessible(self.recipient_field, "Recipient of confirmation")
        recipient_layout.addWidget(self.recipient_field)
        
        notif_layout.addLayout(recipient_layout)
        
        # Time sent
        time_layout = QHBoxLayout()
        time_label = QLabel("Sent At:")
        time_label.setFont(Fonts.LABEL)
        time_label.setMinimumWidth(100)
        time_layout.addWidget(time_label)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_field = QLineEdit(timestamp)
        self.time_field.setFont(Fonts.NORMAL)
        self.time_field.setStyleSheet(INPUT_STYLE)
        make_accessible(self.time_field, "Time confirmation was sent")
        time_layout.addWidget(self.time_field)
        
        notif_layout.addLayout(time_layout)
        
        # Confirmation message
        message_label = QLabel("Confirmation Message:")
        message_label.setFont(Fonts.LABEL)
        notif_layout.addWidget(message_label)
        
        self.confirmation_text = QTextEdit()
        self.confirmation_text.setFont(Fonts.NORMAL)
        self.confirmation_text.setStyleSheet(INPUT_STYLE)
        self.confirmation_text.setMaximumHeight(150)
        
        # Pre-fill with standard confirmation
        default_msg = "Your Everbridge alert has been successfully sent to all recipients.\n\n"
        if self.alert_info.get("site"):
            default_msg += f"Site: {self.alert_info['site']}\n"
        default_msg += f"Time Sent: {timestamp}\n"
        default_msg += "Status: Delivered"
        
        self.confirmation_text.setPlainText(default_msg)
        notif_layout.addWidget(self.confirmation_text)
        
        notif_group.setLayout(notif_layout)
        layout.addWidget(notif_group)
        
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save Confirmation (Ctrl+S)")
        save_btn.setFont(Fonts.BUTTON_LARGE)
        save_btn.setStyleSheet(get_button_style(Colors.SUCCESS, 50))
        save_btn.clicked.connect(self.save_confirmation)
        button_layout.addWidget(save_btn)
        
        skip_btn = QPushButton("Skip (Esc)")
        skip_btn.setFont(Fonts.BUTTON)
        skip_btn.setStyleSheet(get_button_style("#757575", 50))
        skip_btn.clicked.connect(self.reject)
        button_layout.addWidget(skip_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        QShortcut(QKeySequence("Ctrl+S"), self, self.save_confirmation)
        QShortcut(QKeySequence("Escape"), self, self.reject)
    
    def save_confirmation(self):
        """Save the notification confirmation log"""
        try:
            # Get values
            recipient = self.recipient_field.text().strip()
            confirmation = self.confirmation_text.toPlainText().strip()
            timestamp = self.time_field.text()
            
            # Validation
            if not recipient:
                show_error(self, "Please enter the recipient")
                self.recipient_field.setFocus()
                return
            
            # Save as Notification type email log
            insert_email_log(
                log_type="Notification",
                sender=None,
                recipient=recipient,
                subject="Everbridge Alert Confirmation",
                timestamp=timestamp,
                extra_field=None,
                msg_path="Outgoing"
            )
            
            # Also save to Excel
            email_data = {
                'from': 'Security Operations',
                'subject': 'Everbridge Alert Confirmation',
                'category': 'Notification',
                'site': self.alert_info.get('site', ''),
                'priority': 'Normal',
                'notes': f"Confirmation sent to {recipient}"
            }
            
            try:
                log_manager.add_email_log(email_data)
            except Exception as e:
                print(f"Error saving to Excel: {e}")
            
            show_success(self, "Notification confirmation logged!")
            self.accept()
            
        except Exception as e:
            show_error(self, f"Error saving confirmation: {str(e)}")