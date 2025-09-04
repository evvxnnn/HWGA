from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QLineEdit,
    QPushButton, QHBoxLayout, QCheckBox, QMessageBox,
    QMainWindow, QStatusBar, QGroupBox, QButtonGroup,
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QShortcut, QKeySequence
from datetime import datetime
from database import insert_radio_log
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


# Default units and locations - can be customized in settings
DEFAULT_UNITS = {
    "Unit 21": ["AEI The Rock", "Andrews", "Breeden Lot", "CCDC", "CEP", "CEP - Bldg 60", "CEP - Gate 1", "CEP - Gate 7", "CEP - Gate 82", "CEP - Gate 96", "City PG", "COB", "COB - CSOC", "COB Brown St. Lot", "Cole PG", "COM", "CSS", "CTC", "FSP", "Hangar", "IOB", "Lionbridge", "Skooters", "SMC", "SSC", "Union Hall/Reeves"],
    "Unit 22": ["AEI The Rock", "Andrews", "Breeden Lot", "CCDC", "CEP", "CEP - Bldg 60", "CEP - Gate 1", "CEP - Gate 7", "CEP - Gate 82", "CEP - Gate 96", "City PG", "COB", "COB - CSOC", "COB Brown St. Lot", "Cole PG", "COM", "CSS", "CTC", "FSP", "Hangar", "IOB", "Lionbridge", "Skooters", "SMC", "SSC", "Union Hall/Reeves"],
    "Unit 31": ["AEI The Rock", "Andrews", "Breeden Lot", "CCDC", "CEP", "CEP - Bldg 60", "CEP - Gate 1", "CEP - Gate 7", "CEP - Gate 82", "CEP - Gate 96", "City PG", "COB", "COB - CSOC", "COB Brown St. Lot", "Cole PG", "COM", "CSS", "CTC", "FSP", "Hangar", "IOB", "Lionbridge", "Skooters", "SMC", "SSC", "Union Hall/Reeves"],
    "Unit 32": ["AEI The Rock", "Andrews", "Breeden Lot", "CCDC", "CEP", "CEP - Bldg 60", "CEP - Gate 1", "CEP - Gate 7", "CEP - Gate 82", "CEP - Gate 96", "City PG", "COB", "COB - CSOC", "COB Brown St. Lot", "Cole PG", "COM", "CSS", "CTC", "FSP", "Hangar", "IOB", "Lionbridge", "Skooters", "SMC", "SSC", "Union Hall/Reeves"],
    "Unit 41": ["CEP", "CEP - Gate 7", "CMEP", "CMIC", "COB", "COB - CSOC", "CESC", "OLY", "SEMI", "SEP", "SILC", "Test Track", "WSS"],
    "Unit 42": ["CEP", "CEP - Gate 7", "CMEP", "CMIC", "COB", "COB - CSOC", "CESC", "OLY", "SEMI", "SEP", "SILC", "Test Track", "WSS"]
}

# Keep UNITS for backward compatibility and settings dialog
UNITS = DEFAULT_UNITS

DEFAULT_REASONS = [
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

# Keep REASONS for backward compatibility
REASONS = DEFAULT_REASONS

# Get units from settings or use defaults
def get_radio_units():
    dropdown_options = app_settings.get("dropdown_options", {})
    return dropdown_options.get("radio_unit_locations", DEFAULT_UNITS)

# Get reasons from settings or use defaults
def get_radio_reasons():
    dropdown_options = app_settings.get("dropdown_options", {})
    return dropdown_options.get("radio_reasons", DEFAULT_REASONS)

class RadioPanel(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Radio Dispatch Log Entry")
        self.setMinimumSize(900, 700)
        self.showMaximized()
        
        self.units = get_radio_units()  # Get from settings
        self.reasons = get_radio_reasons()  # Get from settings
        
        # Status bar - initialize BEFORE init_ui
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready to log radio dispatch")
        
        self.init_ui()
        self.setup_shortcuts()

    def init_ui(self):
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 30, 40, 30)

        # Add help button in top right
        header_layout = QHBoxLayout()
        header_layout.addStretch()
        help_btn = HelpButton("Radio Dispatch", get_help_training_id("radio"), self)
        header_layout.addWidget(help_btn)
        layout.addLayout(header_layout)
        
        # Title
        title = QLabel("Radio Dispatch Logger")
        title.setFont(Fonts.TITLE)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #e0e0e0; margin-bottom: 30px;")
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
        
        # Auto-fill timestamp if enabled in settings
        if app_settings.get("auto_timestamp", True):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            timestamp = ""
        
        self.timestamp_field = QLineEdit(timestamp)
        self.timestamp_field.setFont(Fonts.NORMAL)
        self.timestamp_field.setStyleSheet(INPUT_STYLE)
        self.timestamp_field.setMinimumHeight(45)
        make_accessible(self.timestamp_field, "Time of radio dispatch")
        time_layout.addWidget(self.timestamp_field)
        
        now_btn = QPushButton("Update to Now")
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
        self.unit_dropdown.addItems(self.units.keys())
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
        self.reason_dropdown.addItems(self.reasons)
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
        
        arrived_only_btn = QPushButton("Arrived Only")
        arrived_only_btn.setFont(Fonts.BUTTON)
        arrived_only_btn.setStyleSheet(get_button_style("#4CAF50", 50))
        arrived_only_btn.clicked.connect(lambda: self.set_status(True, False))
        quick_layout.addWidget(arrived_only_btn)
        
        departed_only_btn = QPushButton("Departed Only")
        departed_only_btn.setFont(Fonts.BUTTON)
        departed_only_btn.setStyleSheet(get_button_style("#2196F3", 50))
        departed_only_btn.clicked.connect(lambda: self.set_status(False, True))
        quick_layout.addWidget(departed_only_btn)
        
        both_btn = QPushButton("Both")
        both_btn.setFont(Fonts.BUTTON)
        both_btn.setStyleSheet(get_button_style("#9C27B0", 50))
        both_btn.clicked.connect(lambda: self.set_status(True, True))
        quick_layout.addWidget(both_btn)
        
        clear_btn = QPushButton("Clear")
        clear_btn.setFont(Fonts.BUTTON)
        clear_btn.setStyleSheet(get_button_style("#757575", 50))
        clear_btn.clicked.connect(lambda: self.set_status(False, False))
        quick_layout.addWidget(clear_btn)
        
        quick_group.setLayout(quick_layout)
        layout.addWidget(quick_group)

        layout.addStretch()

        # Save button
        self.save_btn = QPushButton("Save Dispatch Log (Ctrl+S)")
        self.save_btn.setFont(Fonts.BUTTON_LARGE)
        self.save_btn.setStyleSheet(get_button_style(Colors.SUCCESS, 70))
        self.save_btn.clicked.connect(self.save_log)
        make_accessible(self.save_btn, "Save the radio dispatch log")
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
        self.main_tabs.addTab(input_widget, "Log Radio Dispatch")
        
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
        self.main_tabs.addTab(log_widget, "View Radio Logs")
        
        # Set main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.addWidget(self.main_tabs)
        central_widget.setLayout(main_layout)
        
        # Load initial logs
        self.load_recent_logs()

    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        QShortcut(QKeySequence("Ctrl+S"), self, self.save_log)
        QShortcut(QKeySequence("Escape"), self, self.close)
        QShortcut(QKeySequence("Ctrl+T"), self, self.set_current_time)
        QShortcut(QKeySequence("A"), self, lambda: self.arrived_checkbox.toggle())
        QShortcut(QKeySequence("D"), self, lambda: self.departed_checkbox.toggle())
        QShortcut(QKeySequence("F5"), self, self.load_recent_logs)

    def set_current_time(self):
        """Set timestamp to current time"""
        self.timestamp_field.setText(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.status_bar.showMessage("Timestamp updated to current time")

    def update_locations(self):
        unit = self.unit_dropdown.currentText()
        self.location_dropdown.clear()
        self.location_dropdown.addItems(self.units.get(unit, []))

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
            
            # Also save to Excel log
            radio_data = {
                'unit': unit,
                'location': location,
                'type': reason,
                'message': f"{status} at {location}",
                'priority': 'Normal',
                'response': status
            }
            
            try:
                log_manager.add_radio_log(radio_data)
                # Refresh the log display
                self.load_recent_logs()
            except Exception as e:
                print(f"Error saving to Excel: {e}")
            
            show_success(self, f"Radio dispatch log saved!\n\n{unit} {status} at {location}")
            
            # Switch to logs tab to show the new entry
            self.main_tabs.setCurrentIndex(1)
            self.load_recent_logs()
        except Exception as e:
            show_error(self, f"Error saving log: {str(e)}")
            self.status_bar.showMessage("Error saving log")
    
    def load_recent_logs(self):
        """Load recent radio logs into the table"""
        try:
            df = log_manager.get_recent_logs('radio', limit=50)
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
                self.status_bar.showMessage(f"Loaded {len(df)} radio log entries")
            else:
                self.log_table.setRowCount(0)
                self.log_table.setColumnCount(5)
                self.log_table.setHorizontalHeaderLabels(["Date", "Time", "Unit", "Location", "Type"])
                self.status_bar.showMessage("No radio logs found")
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
    
    def export_logs(self):
        """Export logs to file"""
        from PyQt6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Radio Logs", "radio_logs_export.xlsx", 
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