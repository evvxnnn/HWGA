from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QLineEdit,
    QPushButton, QHBoxLayout, QCheckBox, QMessageBox,
    QMainWindow, QStatusBar, QGroupBox, QButtonGroup
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QShortcut, QKeySequence
from datetime import datetime
from database import insert_radio_log
from ui.styles import *

UNITS = {
    "Unit 21": ["AEI The Rock", "Andrews", "Breeden Lot", "CCDC", "CEP", "CEP - Bldg 60", "CEP - Gate 1", "CEP - Gate 7", "CEP - Gate 82", "CEP - Gate 96", "City PG", "COB", "COB - CSOC", "COB Brown St. Lot", "Cole PG", "COM", "CSS", "CTC", "FSP", "Hangar", "IOB", "Lionbridge", "Skooters", "SMC", "SSC", "Union Hall/Reeves"],
    "Unit 22": ["AEI The Rock", "Andrews", "Breeden Lot", "CCDC", "CEP", "CEP - Bldg 60", "CEP - Gate 1", "CEP - Gate 7", "CEP - Gate 82", "CEP - Gate 96", "City PG", "COB", "COB - CSOC", "COB Brown St. Lot", "Cole PG", "COM", "CSS", "CTC", "FSP", "Hangar", "IOB", "Lionbridge", "Skooters", "SMC", "SSC", "Union Hall/Reeves"],
    "Unit 31": ["AEI The Rock", "Andrews", "Breeden Lot", "CCDC", "CEP", "CEP - Bldg 60", "CEP - Gate 1", "CEP - Gate 7", "CEP - Gate 82", "CEP - Gate 96", "City PG", "COB", "COB - CSOC", "COB Brown St. Lot", "Cole PG", "COM", "CSS", "CTC", "FSP", "Hangar", "IOB", "Lionbridge", "Skooters", "SMC", "SSC", "Union Hall/Reeves"],
    "Unit 32": ["AEI The Rock", "Andrews", "Breeden Lot", "CCDC", "CEP", "CEP - Bldg 60", "CEP - Gate 1", "CEP - Gate 7", "CEP - Gate 82", "CEP - Gate 96", "City PG", "COB", "COB - CSOC", "COB Brown St. Lot", "Cole PG", "COM", "CSS", "CTC", "FSP", "Hangar", "IOB", "Lionbridge", "Skooters", "SMC", "SSC", "Union Hall/Reeves"],
    "Unit 41": ["CEP", "CEP - Gate 7", "CMEP", "CMIC", "COB", "COB - CSOC", "CESC", "OLY", "SEMI", "SEP", "SILC", "Test Track", "WSS"],
    "Unit 42": ["CEP", "CEP - Gate 7", "CMEP", "CMIC", "COB", "COB - CSOC", "CESC", "OLY", "SEMI", "SEP", "SILC", "Test Track", "WSS"]
}

REASONS = [
    "Routine Patrol",
    "Suspicious Activity",
    "Access Control Check",
    "Escort Service",
    "Alarm Response",
    "Safety Check",
    "Incident Response",
    "Break Relief",
    "Special Assignment"
]

class RadioPanel(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Radio Dispatch Log Entry")
        self.setMinimumSize(900, 700)
        self.showMaximized()
        
        self.init_ui()
        self.setup_shortcuts()
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready to log radio dispatch")

    def init_ui(self):
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 30, 40, 30)

        # Title
        title = QLabel("📻 Radio Dispatch Logger")
        title.setFont(Fonts.TITLE)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"color: {Colors.RADIO}; margin-bottom: 30px;")
        layout.addWidget(title)

        # Time section with visual enhancement
        time_group = QGroupBox("Dispatch Time")
        time_group.setFont(Fonts.LABEL)
        time_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #FF9800;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 0 10px 0 10px;
            }
        """)
        time_layout = QHBoxLayout()
        
        self.timestamp_field = QLineEdit(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.timestamp_field.setFont(Fonts.NORMAL)
        self.timestamp_field.setStyleSheet(INPUT_STYLE)
        self.timestamp_field.setMinimumHeight(45)
        make_accessible(self.timestamp_field, "Time of radio dispatch")
        time_layout.addWidget(self.timestamp_field)
        
        now_btn = QPushButton("🕐 Update to Now")
        now_btn.setFont(Fonts.BUTTON)
        now_btn.setStyleSheet(get_button_style(Colors.INFO, 45))
        now_btn.clicked.connect(self.set_current_time)
        make_accessible(now_btn, "Click to set current time")
        time_layout.addWidget(now_btn)
        
        time_group.setLayout(time_layout)
        layout.addWidget(time_group)

        # Unit selection with larger UI
        unit_layout = QHBoxLayout()
        unit_label = QLabel("Security Unit:")
        unit_label.setFont(Fonts.LABEL)
        unit_label.setMinimumWidth(150)
        unit_layout.addWidget(unit_label)
        
        self.unit_dropdown = QComboBox()
        self.unit_dropdown.addItems(UNITS.keys())
        self.unit_dropdown.setFont(Fonts.NORMAL)
        self.unit_dropdown.setStyleSheet(DROPDOWN_STYLE)
        self.unit_dropdown.setMinimumHeight(45)
        self.unit_dropdown.currentIndexChanged.connect(self.update_locations)
        make_accessible(self.unit_dropdown, "Select the security unit")
        unit_layout.addWidget(self.unit_dropdown)
        unit_layout.addStretch()
        layout.addLayout(unit_layout)

        # Location dropdown
        location_layout = QHBoxLayout()
        location_label = QLabel("Location:")
        location_label.setFont(Fonts.LABEL)
        location_label.setMinimumWidth(150)
        location_layout.addWidget(location_label)
        
        self.location_dropdown = QComboBox()
        self.location_dropdown.setFont(Fonts.NORMAL)
        self.location_dropdown.setStyleSheet(DROPDOWN_STYLE)
        self.location_dropdown.setMinimumHeight(45)
        make_accessible(self.location_dropdown, "Select the dispatch location")
        location_layout.addWidget(self.location_dropdown)
        location_layout.addStretch()
        layout.addLayout(location_layout)
        self.update_locations()

        # Reason dropdown
        reason_layout = QHBoxLayout()
        reason_label = QLabel("Reason:")
        reason_label.setFont(Fonts.LABEL)
        reason_label.setMinimumWidth(150)
        reason_layout.addWidget(reason_label)
        
        self.reason_dropdown = QComboBox()
        self.reason_dropdown.addItems(REASONS)
        self.reason_dropdown.setFont(Fonts.NORMAL)
        self.reason_dropdown.setStyleSheet(DROPDOWN_STYLE)
        self.reason_dropdown.setMinimumHeight(45)
        make_accessible(self.reason_dropdown, "Select the reason for dispatch")
        reason_layout.addWidget(self.reason_dropdown)
        reason_layout.addStretch()
        layout.addLayout(reason_layout)

        # Status checkboxes with visual enhancement
        status_group = QGroupBox("Unit Status")
        status_group.setFont(Fonts.LABEL)
        status_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #FF9800;
                border-radius: 10px;
                margin-top: 10px;
                padding: 20px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 0 10px 0 10px;
            }
        """)
        status_layout = QHBoxLayout()
        
        self.arrived_checkbox = QCheckBox("Unit ARRIVED at Location")
        self.arrived_checkbox.setFont(Fonts.NORMAL)
        self.arrived_checkbox.setStyleSheet("""
            QCheckBox {
                spacing: 10px;
            }
            QCheckBox::indicator {
                width: 30px;
                height: 30px;
            }
            QCheckBox::indicator:checked {
                background-color: #4CAF50;
                border: 2px solid #388E3C;
                border-radius: 5px;
            }
            QCheckBox::indicator:unchecked {
                background-color: white;
                border: 2px solid #999;
                border-radius: 5px;
            }
        """)
        make_accessible(self.arrived_checkbox, "Check if unit has arrived at location")
        status_layout.addWidget(self.arrived_checkbox)
        
        status_layout.addStretch()
        
        self.departed_checkbox = QCheckBox("Unit DEPARTED from Location")
        self.departed_checkbox.setFont(Fonts.NORMAL)
        self.departed_checkbox.setStyleSheet("""
            QCheckBox {
                spacing: 10px;
            }
            QCheckBox::indicator {
                width: 30px;
                height: 30px;
            }
            QCheckBox::indicator:checked {
                background-color: #2196F3;
                border: 2px solid #1976D2;
                border-radius: 5px;
            }
            QCheckBox::indicator:unchecked {
                background-color: white;
                border: 2px solid #999;
                border-radius: 5px;
            }
        """)
        make_accessible(self.departed_checkbox, "Check if unit has departed from location")
        status_layout.addWidget(self.departed_checkbox)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)

        # Quick status buttons
        quick_group = QGroupBox("Quick Status")
        quick_group.setFont(Fonts.LABEL)
        quick_layout = QHBoxLayout()
        
        arrived_only_btn = QPushButton("✅ Arrived Only")
        arrived_only_btn.setFont(Fonts.BUTTON)
        arrived_only_btn.setStyleSheet(get_button_style("#4CAF50", 50))
        arrived_only_btn.clicked.connect(lambda: self.set_status(True, False))
        quick_layout.addWidget(arrived_only_btn)
        
        departed_only_btn = QPushButton("🚪 Departed Only")
        departed_only_btn.setFont(Fonts.BUTTON)
        departed_only_btn.setStyleSheet(get_button_style("#2196F3", 50))
        departed_only_btn.clicked.connect(lambda: self.set_status(False, True))
        quick_layout.addWidget(departed_only_btn)
        
        both_btn = QPushButton("↔️ Both")
        both_btn.setFont(Fonts.BUTTON)
        both_btn.setStyleSheet(get_button_style("#9C27B0", 50))
        both_btn.clicked.connect(lambda: self.set_status(True, True))
        quick_layout.addWidget(both_btn)
        
        clear_btn = QPushButton("❌ Clear")
        clear_btn.setFont(Fonts.BUTTON)
        clear_btn.setStyleSheet(get_button_style("#757575", 50))
        clear_btn.clicked.connect(lambda: self.set_status(False, False))
        quick_layout.addWidget(clear_btn)
        
        quick_group.setLayout(quick_layout)
        layout.addWidget(quick_group)

        layout.addStretch()

        # Save button
        self.save_btn = QPushButton("💾 Save Dispatch Log (Ctrl+S)")
        self.save_btn.setFont(Fonts.BUTTON_LARGE)
        self.save_btn.setStyleSheet(get_button_style(Colors.SUCCESS, 70))
        self.save_btn.clicked.connect(self.save_log)
        make_accessible(self.save_btn, "Save the radio dispatch log")
        layout.addWidget(self.save_btn)

        central_widget.setLayout(layout)

    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        QShortcut(QKeySequence("Ctrl+S"), self, self.save_log)
        QShortcut(QKeySequence("Escape"), self, self.close)
        QShortcut(QKeySequence("Ctrl+T"), self, self.set_current_time)
        QShortcut(QKeySequence("A"), self, lambda: self.arrived_checkbox.toggle())
        QShortcut(QKeySequence("D"), self, lambda: self.departed_checkbox.toggle())

    def set_current_time(self):
        """Set timestamp to current time"""
        self.timestamp_field.setText(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.status_bar.showMessage("Timestamp updated to current time")

    def update_locations(self):
        unit = self.unit_dropdown.currentText()
        self.location_dropdown.clear()
        self.location_dropdown.addItems(UNITS.get(unit, []))

    def set_status(self, arrived, departed):
        """Quick set status checkboxes"""
        self.arrived_checkbox.setChecked(arrived)
        self.departed_checkbox.setChecked(departed)

    def save_log(self):
        unit = self.unit_dropdown.currentText()
        location = self.location_dropdown.currentText()
        reason = self.reason_dropdown.currentText()
        arrived = self.arrived_checkbox.isChecked()
        departed = self.departed_checkbox.isChecked()
        timestamp = self.timestamp_field.text()

        # Validate that at least one status is selected
        if not arrived and not departed:
            show_error(self, "Please select at least one status (Arrived or Departed)")
            return

        try:
            insert_radio_log(unit, location, reason, arrived, departed, timestamp)
            
            # Show success with summary
            status_text = []
            if arrived:
                status_text.append("ARRIVED")
            if departed:
                status_text.append("DEPARTED")
            status = " and ".join(status_text)
            
            show_success(self, f"Radio dispatch log saved!\n\n{unit} {status} at {location}")
            self.close()
        except Exception as e:
            show_error(self, f"Error saving log: {str(e)}")