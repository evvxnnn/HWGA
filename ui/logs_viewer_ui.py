from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QComboBox,
    QFileDialog, QMessageBox, QHeaderView, QTabWidget,
    QGroupBox, QDateEdit, QLineEdit, QGridLayout
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QShortcut, QKeySequence
from ui.styles import Fonts, get_button_style, TABLE_STYLE, DROPDOWN_STYLE
from ui.help_utils import HelpButton, get_help_training_id
import os
from datetime import datetime, timedelta
import pandas as pd

class LogsViewerPanel(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Logs Viewer")
        self.setMinimumSize(1200, 800)
        self.showMaximized()
        
        # Log types and their file paths
        self.log_types = {
            "Email Logs": "logs/email_logs.xlsx",
            "Phone Call Logs": "logs/phone_logs.xlsx",
            "Radio Dispatch Logs": "logs/radio_logs.xlsx",
            "Everbridge Alert Logs": "logs/everbridge_logs.xlsx",
            "Incident Report Logs": "logs/incident_logs.xlsx",
            "Facilities Ticket Logs": "logs/facilities_logs.xlsx",
            "Data Request Logs": "logs/data_request_logs.xlsx",
            "Badge Deactivation Logs": "logs/badge_deactivation_logs.xlsx",
            "Parking Tag Logs": "logs/parking_logs.xlsx",
            "Muster Report Logs": "logs/muster_logs.xlsx"
        }
        
        self.current_log_data = None
        self.init_ui()
        self.setup_shortcuts()
    
    def init_ui(self):
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header with title and help button
        header_layout = QHBoxLayout()
        header_layout.addStretch()
        
        # Title
        title = QLabel("Security Operations Logs Viewer")
        title.setFont(Fonts.TITLE)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #e0e0e0; margin-bottom: 10px;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Help button
        help_btn = HelpButton("Logs Viewer", get_help_training_id("logs"), self)
        header_layout.addWidget(help_btn)
        
        layout.addLayout(header_layout)
        
        # Control panel
        control_panel = self.create_control_panel()
        layout.addWidget(control_panel)
        
        # Create tabs for different views
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #333333;
                background-color: #0d0d0d;
            }
            QTabBar::tab {
                padding: 10px 20px;
                background-color: #1a1a1a;
                color: #808080;
                border: 1px solid #262626;
            }
            QTabBar::tab:selected {
                background-color: #0d0d0d;
                color: #e0e0e0;
                border-bottom: 2px solid #5a5a5a;
            }
        """)
        
        # Data view tab
        self.data_tab = self.create_data_tab()
        self.tabs.addTab(self.data_tab, "Data View")
        
        # Statistics tab
        self.stats_tab = self.create_stats_tab()
        self.tabs.addTab(self.stats_tab, "Statistics")
        
        # Export tab
        self.export_tab = self.create_export_tab()
        self.tabs.addTab(self.export_tab, "Export")
        
        layout.addWidget(self.tabs)
        
        central_widget.setLayout(layout)
    
    def create_control_panel(self):
        """Create the control panel for log selection and filtering"""
        panel = QGroupBox("Log Controls")
        panel.setStyleSheet("""
            QGroupBox {
                color: #e0e0e0;
                border: 1px solid #333333;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: 500;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                background-color: #0d0d0d;
            }
        """)
        
        layout = QGridLayout()
        layout.setSpacing(15)
        
        # Log type selection
        type_label = QLabel("Select Log Type:")
        type_label.setFont(Fonts.LABEL)
        layout.addWidget(type_label, 0, 0)
        
        self.log_combo = QComboBox()
        self.log_combo.addItems(self.log_types.keys())
        self.log_combo.setStyleSheet(DROPDOWN_STYLE)
        self.log_combo.currentTextChanged.connect(self.load_log_file)
        layout.addWidget(self.log_combo, 0, 1)
        
        # Date range filter
        date_label = QLabel("Date Range:")
        date_label.setFont(Fonts.LABEL)
        layout.addWidget(date_label, 0, 2)
        
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        self.start_date.setCalendarPopup(True)
        self.start_date.setStyleSheet("""
            QDateEdit {
                padding: 8px;
                background-color: #1a1a1a;
                color: #e0e0e0;
                border: 1px solid #333333;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.start_date, 0, 3)
        
        to_label = QLabel("to")
        to_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(to_label, 0, 4)
        
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        self.end_date.setStyleSheet("""
            QDateEdit {
                padding: 8px;
                background-color: #1a1a1a;
                color: #e0e0e0;
                border: 1px solid #333333;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.end_date, 0, 5)
        
        # Search field
        search_label = QLabel("Search:")
        search_label.setFont(Fonts.LABEL)
        layout.addWidget(search_label, 1, 0)
        
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Enter search term...")
        self.search_field.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                background-color: #1a1a1a;
                color: #e0e0e0;
                border: 1px solid #333333;
                border-radius: 4px;
            }
            QLineEdit:focus {
                border: 1px solid #5a5a5a;
            }
        """)
        self.search_field.textChanged.connect(self.filter_logs)
        layout.addWidget(self.search_field, 1, 1, 1, 2)
        
        # Action buttons
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setStyleSheet(get_button_style())
        self.refresh_btn.clicked.connect(self.refresh_data)
        layout.addWidget(self.refresh_btn, 1, 3)
        
        self.filter_btn = QPushButton("Apply Filters")
        self.filter_btn.setStyleSheet(get_button_style())
        self.filter_btn.clicked.connect(self.apply_filters)
        layout.addWidget(self.filter_btn, 1, 4)
        
        self.clear_btn = QPushButton("Clear Filters")
        self.clear_btn.setStyleSheet(get_button_style())
        self.clear_btn.clicked.connect(self.clear_filters)
        layout.addWidget(self.clear_btn, 1, 5)
        
        panel.setLayout(layout)
        return panel
    
    def create_data_tab(self):
        """Create the data view tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Status label
        self.status_label = QLabel("No log file loaded")
        self.status_label.setStyleSheet("color: #808080; padding: 10px;")
        layout.addWidget(self.status_label)
        
        # Table widget
        self.table = QTableWidget()
        self.table.setStyleSheet(TABLE_STYLE)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        layout.addWidget(self.table)
        
        widget.setLayout(layout)
        return widget
    
    def create_stats_tab(self):
        """Create the statistics tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Statistics display
        self.stats_display = QLabel("Load a log file to view statistics")
        self.stats_display.setStyleSheet("""
            QLabel {
                color: #808080;
                padding: 20px;
                background-color: #1a1a1a;
                border: 1px solid #333333;
                border-radius: 4px;
            }
        """)
        self.stats_display.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self.stats_display)
        
        widget.setLayout(layout)
        return widget
    
    def create_export_tab(self):
        """Create the export tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Export options
        export_group = QGroupBox("Export Options")
        export_group.setStyleSheet("""
            QGroupBox {
                color: #e0e0e0;
                border: 1px solid #333333;
                border-radius: 4px;
                margin-top: 10px;
                padding: 20px;
            }
        """)
        
        export_layout = QGridLayout()
        
        # Export format
        format_label = QLabel("Export Format:")
        format_label.setFont(Fonts.LABEL)
        export_layout.addWidget(format_label, 0, 0)
        
        self.format_combo = QComboBox()
        self.format_combo.addItems(["Excel (.xlsx)", "CSV (.csv)", "PDF Report"])
        self.format_combo.setStyleSheet(DROPDOWN_STYLE)
        export_layout.addWidget(self.format_combo, 0, 1)
        
        # Export buttons
        self.export_current_btn = QPushButton("Export Current View")
        self.export_current_btn.setStyleSheet(get_button_style())
        self.export_current_btn.clicked.connect(self.export_current_view)
        export_layout.addWidget(self.export_current_btn, 1, 0)
        
        self.export_all_btn = QPushButton("Export All Data")
        self.export_all_btn.setStyleSheet(get_button_style())
        self.export_all_btn.clicked.connect(self.export_all_data)
        export_layout.addWidget(self.export_all_btn, 1, 1)
        
        self.generate_report_btn = QPushButton("Generate Monthly Report")
        self.generate_report_btn.setStyleSheet(get_button_style())
        self.generate_report_btn.clicked.connect(self.generate_monthly_report)
        export_layout.addWidget(self.generate_report_btn, 2, 0, 1, 2)
        
        export_group.setLayout(export_layout)
        layout.addWidget(export_group)
        
        # Export status
        self.export_status = QLabel("")
        self.export_status.setStyleSheet("color: #808080; padding: 10px;")
        layout.addWidget(self.export_status)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        QShortcut(QKeySequence("Ctrl+R"), self, self.refresh_data)
        QShortcut(QKeySequence("Ctrl+F"), self, lambda: self.search_field.setFocus())
        QShortcut(QKeySequence("Ctrl+E"), self, self.export_current_view)
        QShortcut(QKeySequence("Escape"), self, self.close)
    
    def load_log_file(self, log_type=None):
        """Load the selected log file"""
        if not log_type:
            log_type = self.log_combo.currentText()
        
        file_path = self.log_types.get(log_type)
        if not file_path or not os.path.exists(file_path):
            self.status_label.setText(f"Log file not found: {file_path}")
            self.table.clear()
            self.current_log_data = None
            return
        
        try:
            # Load the Excel file
            self.current_log_data = pd.read_excel(file_path)
            self.display_data(self.current_log_data)
            self.update_statistics()
            self.status_label.setText(f"Loaded {len(self.current_log_data)} records from {log_type}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load log file: {str(e)}")
            self.status_label.setText(f"Error loading {log_type}")
    
    def display_data(self, data):
        """Display data in the table"""
        if data is None or data.empty:
            self.table.clear()
            return
        
        # Set up table
        self.table.setRowCount(len(data))
        self.table.setColumnCount(len(data.columns))
        self.table.setHorizontalHeaderLabels(data.columns.tolist())
        
        # Populate table
        for row in range(len(data)):
            for col in range(len(data.columns)):
                value = str(data.iloc[row, col])
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, col, item)
        
        # Adjust column widths
        self.table.resizeColumnsToContents()
    
    def filter_logs(self):
        """Filter logs based on search term"""
        search_term = self.search_field.text().lower()
        if not search_term or self.current_log_data is None:
            self.display_data(self.current_log_data)
            return
        
        # Filter data
        filtered_data = self.current_log_data[
            self.current_log_data.apply(
                lambda row: any(search_term in str(cell).lower() for cell in row),
                axis=1
            )
        ]
        self.display_data(filtered_data)
        self.status_label.setText(f"Showing {len(filtered_data)} of {len(self.current_log_data)} records")
    
    def apply_filters(self):
        """Apply date range filters"""
        if self.current_log_data is None:
            return
        
        start = self.start_date.date().toPyDate()
        end = self.end_date.date().toPyDate()
        
        # Assuming there's a 'Date' or 'Timestamp' column
        date_columns = ['Date', 'Timestamp', 'date', 'timestamp', 'created_at']
        date_col = None
        for col in date_columns:
            if col in self.current_log_data.columns:
                date_col = col
                break
        
        if date_col:
            filtered_data = self.current_log_data[
                (pd.to_datetime(self.current_log_data[date_col]).dt.date >= start) &
                (pd.to_datetime(self.current_log_data[date_col]).dt.date <= end)
            ]
            self.display_data(filtered_data)
            self.status_label.setText(f"Showing {len(filtered_data)} records from {start} to {end}")
        else:
            QMessageBox.warning(self, "Warning", "No date column found in this log file")
    
    def clear_filters(self):
        """Clear all filters"""
        self.search_field.clear()
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        self.end_date.setDate(QDate.currentDate())
        self.display_data(self.current_log_data)
        if self.current_log_data is not None:
            self.status_label.setText(f"Showing all {len(self.current_log_data)} records")
    
    def refresh_data(self):
        """Refresh the current log file"""
        self.load_log_file()
    
    def update_statistics(self):
        """Update statistics display"""
        if self.current_log_data is None or self.current_log_data.empty:
            self.stats_display.setText("No data to analyze")
            return
        
        stats_text = f"""
        <h3>Log Statistics</h3>
        <p><b>Total Records:</b> {len(self.current_log_data)}</p>
        <p><b>Columns:</b> {', '.join(self.current_log_data.columns.tolist())}</p>
        """
        
        # Add more specific statistics based on data
        if 'Date' in self.current_log_data.columns or 'Timestamp' in self.current_log_data.columns:
            date_col = 'Date' if 'Date' in self.current_log_data.columns else 'Timestamp'
            try:
                dates = pd.to_datetime(self.current_log_data[date_col])
                stats_text += f"""
                <p><b>Date Range:</b> {dates.min().date()} to {dates.max().date()}</p>
                <p><b>Most Active Day:</b> {dates.dt.date.value_counts().index[0]}</p>
                """
            except:
                pass
        
        self.stats_display.setText(stats_text)
    
    def export_current_view(self):
        """Export the current table view"""
        if self.table.rowCount() == 0:
            QMessageBox.warning(self, "Warning", "No data to export")
            return
        
        format_type = self.format_combo.currentText()
        if "Excel" in format_type:
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Excel File", "", "Excel Files (*.xlsx)")
            if file_path:
                self.export_to_excel(file_path)
        elif "CSV" in format_type:
            file_path, _ = QFileDialog.getSaveFileName(self, "Save CSV File", "", "CSV Files (*.csv)")
            if file_path:
                self.export_to_csv(file_path)
    
    def export_all_data(self):
        """Export all data from current log"""
        if self.current_log_data is None:
            QMessageBox.warning(self, "Warning", "No data to export")
            return
        
        format_type = self.format_combo.currentText()
        if "Excel" in format_type:
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Excel File", "", "Excel Files (*.xlsx)")
            if file_path:
                self.current_log_data.to_excel(file_path, index=False)
                self.export_status.setText(f"Exported to {file_path}")
    
    def export_to_excel(self, file_path):
        """Export table to Excel"""
        # Get data from table
        data = []
        headers = []
        for col in range(self.table.columnCount()):
            headers.append(self.table.horizontalHeaderItem(col).text())
        
        for row in range(self.table.rowCount()):
            row_data = []
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                row_data.append(item.text() if item else "")
            data.append(row_data)
        
        df = pd.DataFrame(data, columns=headers)
        df.to_excel(file_path, index=False)
        self.export_status.setText(f"Exported to {file_path}")
    
    def export_to_csv(self, file_path):
        """Export table to CSV"""
        # Similar to export_to_excel but save as CSV
        pass
    
    def generate_monthly_report(self):
        """Generate a monthly report"""
        QMessageBox.information(self, "Info", "Monthly report generation will be implemented")