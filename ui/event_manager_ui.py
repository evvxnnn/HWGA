from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton,
    QHBoxLayout, QTextEdit, QLineEdit, QInputDialog, QMessageBox,
    QTableWidget, QTableWidgetItem, QSplitter, QGroupBox,
    QComboBox, QDialog, QDialogButtonBox, QListWidgetItem,
    QMainWindow, QStatusBar, QHeaderView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QShortcut, QKeySequence
from logic.event_handler import (
    get_event_chains, get_event_chain_logs, get_log_summary,
    create_event_chain, load_all_logs, link_log_to_event,
    update_event_chain
)
from database import get_log_details
import sqlite3
from database import DB_PATH
from ui.styles import *

class EventChainEditDialog(QDialog):
    def __init__(self, event_id, current_title, current_description, parent=None):
        super().__init__(parent)
        self.event_id = event_id
        self.setWindowTitle("Edit Event Chain")
        self.setModal(True)
        self.setMinimumSize(600, 400)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Title field
        title_label = QLabel("Event Title:")
        title_label.setFont(Fonts.LABEL)
        layout.addWidget(title_label)
        
        self.title_edit = QLineEdit(current_title)
        self.title_edit.setFont(Fonts.NORMAL)
        self.title_edit.setStyleSheet(INPUT_STYLE)
        self.title_edit.setMinimumHeight(40)
        layout.addWidget(self.title_edit)
        
        # Description field
        desc_label = QLabel("Description:")
        desc_label.setFont(Fonts.LABEL)
        layout.addWidget(desc_label)
        
        self.desc_edit = QTextEdit()
        self.desc_edit.setPlainText(current_description or "")
        self.desc_edit.setFont(Fonts.NORMAL)
        self.desc_edit.setStyleSheet(INPUT_STYLE)
        self.desc_edit.setMaximumHeight(150)
        layout.addWidget(self.desc_edit)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.setStyleSheet("""
            QPushButton {
                min-width: 100px;
                min-height: 40px;
                font-size: 14px;
            }
        """)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def get_values(self):
        return self.title_edit.text(), self.desc_edit.toPlainText()

class LogDetailDialog(QDialog):
    def __init__(self, table, log_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Log Details")
        self.setModal(True)
        self.setMinimumSize(700, 500)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Title
        title = QLabel("📋 Complete Log Details")
        title.setFont(Fonts.SUBTITLE)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Get log details
        details = get_log_details(table, log_id)
        
        if details:
            # Create a table to show all fields
            table_widget = QTableWidget()
            table_widget.setFont(Fonts.NORMAL)
            table_widget.setStyleSheet(TABLE_STYLE)
            table_widget.setColumnCount(2)
            table_widget.setHorizontalHeaderLabels(["Field", "Value"])
            table_widget.horizontalHeader().setStretchLastSection(True)
            table_widget.verticalHeader().setVisible(False)
            
            # Skip some internal fields
            skip_fields = ['id']
            
            for field, value in details.items():
                if field not in skip_fields and value is not None:
                    row = table_widget.rowCount()
                    table_widget.insertRow(row)
                    
                    # Format field name
                    field_name = field.replace('_', ' ').title()
                    field_item = QTableWidgetItem(field_name)
                    field_item.setFont(Fonts.LABEL)
                    table_widget.setItem(row, 0, field_item)
                    
                    value_item = QTableWidgetItem(str(value))
                    table_widget.setItem(row, 1, value_item)
            
            table_widget.resizeColumnsToContents()
            layout.addWidget(table_widget)
        else:
            error_label = QLabel("Could not load log details")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            error_label.setStyleSheet("color: #F44336; font-size: 16px;")
            layout.addWidget(error_label)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.setFont(Fonts.BUTTON)
        close_btn.setStyleSheet(get_button_style(Colors.SECONDARY, 45))
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)

class EventManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Event Chain Manager")
        self.setMinimumSize(1400, 800)
        self.showMaximized()
        self.current_event_id = None
        
        self.init_ui()
        self.setup_shortcuts()
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready to manage event chains")

    def init_ui(self):
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 15, 20, 15)
        
        # Title
        title = QLabel("🔗 Event Chain Manager")
        title.setFont(Fonts.TITLE)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"color: {Colors.EVENT}; margin-bottom: 20px;")
        main_layout.addWidget(title)
        
        # Instructions
        info = QLabel("Link related logs together to track complete incidents")
        info.setFont(Fonts.NORMAL)
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setStyleSheet("color: #666; margin-bottom: 10px;")
        main_layout.addWidget(info)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(10)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #E0E0E0;
            }
            QSplitter::handle:hover {
                background-color: #BDBDBD;
            }
        """)
        
        # Left Panel: Event Chains
        left_widget = QWidget()
        left_panel = QVBoxLayout()
        left_panel.setSpacing(10)
        
        chains_label = QLabel("📁 Event Chains")
        chains_label.setFont(Fonts.SUBTITLE)
        left_panel.addWidget(chains_label)
        
        self.event_list = QListWidget()
        self.event_list.setFont(Fonts.NORMAL)
        self.event_list.setStyleSheet(LIST_STYLE)
        self.event_list.itemSelectionChanged.connect(self.load_event_details)
        left_panel.addWidget(self.event_list)
        
        # Event chain buttons
        chain_btn_layout = QHBoxLayout()
        
        self.create_btn = QPushButton("➕ New Chain")
        self.create_btn.setFont(Fonts.BUTTON)
        self.create_btn.setStyleSheet(get_button_style(Colors.SUCCESS, 45))
        self.create_btn.clicked.connect(self.prompt_create_event)
        make_accessible(self.create_btn, "Create a new event chain")
        chain_btn_layout.addWidget(self.create_btn)
        
        self.edit_btn = QPushButton("✏️ Edit")
        self.edit_btn.setFont(Fonts.BUTTON)
        self.edit_btn.setStyleSheet(get_button_style(Colors.WARNING, 45))
        self.edit_btn.clicked.connect(self.edit_event_chain)
        self.edit_btn.setEnabled(False)
        make_accessible(self.edit_btn, "Edit selected event chain")
        chain_btn_layout.addWidget(self.edit_btn)
        
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.setFont(Fonts.BUTTON)
        self.refresh_btn.setStyleSheet(get_button_style(Colors.INFO, 45))
        self.refresh_btn.clicked.connect(self.refresh_events)
        make_accessible(self.refresh_btn, "Refresh event list")
        chain_btn_layout.addWidget(self.refresh_btn)
        
        left_panel.addLayout(chain_btn_layout)
        left_widget.setLayout(left_panel)
        
        # Middle Panel: Event Timeline
        middle_widget = QWidget()
        middle_panel = QVBoxLayout()
        middle_panel.setSpacing(10)
        
        self.timeline_label = QLabel("📅 Event Timeline")
        self.timeline_label.setFont(Fonts.SUBTITLE)
        middle_panel.addWidget(self.timeline_label)
        
        # Timeline table for better display
        self.timeline_table = QTableWidget()
        self.timeline_table.setFont(Fonts.NORMAL)
        self.timeline_table.setStyleSheet(TABLE_STYLE)
        self.timeline_table.setColumnCount(4)
        self.timeline_table.setHorizontalHeaderLabels([
            "Time", "Type", "Summary", "Actions"
        ])
        self.timeline_table.setAlternatingRowColors(True)
        self.timeline_table.verticalHeader().setVisible(False)
        
        # Set column widths
        header = self.timeline_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        middle_panel.addWidget(self.timeline_table)
        middle_widget.setLayout(middle_panel)
        
        # Right Panel: Available Logs
        right_widget = QWidget()
        right_panel = QVBoxLayout()
        right_panel.setSpacing(10)
        
        # Log filter
        filter_group = QGroupBox("Filter Available Logs")
        filter_group.setFont(Fonts.LABEL)
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Type:"))
        self.log_type_filter = QComboBox()
        self.log_type_filter.setFont(Fonts.NORMAL)
        self.log_type_filter.setStyleSheet(DROPDOWN_STYLE)
        self.log_type_filter.addItems(["All", "Email", "Phone", "Radio", "Everbridge"])
        self.log_type_filter.currentTextChanged.connect(self.filter_logs)
        filter_layout.addWidget(self.log_type_filter)
        filter_layout.addStretch()
        
        filter_group.setLayout(filter_layout)
        right_panel.addWidget(filter_group)
        
        logs_label = QLabel("📝 Available Logs")
        logs_label.setFont(Fonts.SUBTITLE)
        right_panel.addWidget(logs_label)
        
        # Available logs table
        self.available_logs_table = QTableWidget()
        self.available_logs_table.setFont(Fonts.NORMAL)
        self.available_logs_table.setStyleSheet(TABLE_STYLE)
        self.available_logs_table.setColumnCount(3)
        self.available_logs_table.setHorizontalHeaderLabels([
            "Time", "Type", "Summary"
        ])
        self.available_logs_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.available_logs_table.setAlternatingRowColors(True)
        self.available_logs_table.verticalHeader().setVisible(False)
        
        # Set column widths
        header = self.available_logs_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        
        right_panel.addWidget(self.available_logs_table)
        
        self.attach_btn = QPushButton("⬅️ Add Selected Log to Event Chain")
        self.attach_btn.setFont(Fonts.BUTTON)
        self.attach_btn.setStyleSheet(get_button_style(Colors.PRIMARY, 50))
        self.attach_btn.clicked.connect(self.attach_selected_log)
        make_accessible(self.attach_btn, "Add the selected log to the current event chain")
        right_panel.addWidget(self.attach_btn)
        
        right_widget.setLayout(right_panel)
        
        # Add widgets to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(middle_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([350, 600, 450])
        
        main_layout.addWidget(splitter)
        central_widget.setLayout(main_layout)
        
        self.refresh_events()
        self.refresh_available_logs()

    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        QShortcut(QKeySequence("Ctrl+N"), self, self.prompt_create_event)
        QShortcut(QKeySequence("Ctrl+E"), self, self.edit_event_chain)
        QShortcut(QKeySequence("F5"), self, self.refresh_events)
        QShortcut(QKeySequence("Ctrl+L"), self, self.attach_selected_log)

    def refresh_events(self):
        self.event_list.clear()
        chains = get_event_chains()
        
        for chain in chains:
            # Get log count for this chain
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM event_links WHERE event_id = ?", (chain['id'],))
            log_count = c.fetchone()[0]
            conn.close()
            
            # Create list item with icon
            item_text = f"[ID: {chain['id']}] {chain['title']} ({log_count} logs)"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, chain)
            
            # Add color coding based on log count
            if log_count == 0:
                item.setBackground(Qt.GlobalColor.lightGray)
            elif log_count < 3:
                item.setBackground(Qt.GlobalColor.yellow)
            
            self.event_list.addItem(item)
        
        self.status_bar.showMessage(f"Loaded {len(chains)} event chains")

    def load_event_details(self):
        selected_item = self.event_list.currentItem()
        if not selected_item:
            self.edit_btn.setEnabled(False)
            return
        
        chain = selected_item.data(Qt.ItemDataRole.UserRole)
        self.current_event_id = chain['id']
        self.edit_btn.setEnabled(True)
        
        # Update timeline label
        self.timeline_label.setText(f"📅 Event Timeline: {chain['title']}")
        
        # Load timeline
        logs = get_event_chain_logs(self.current_event_id)
        
        self.timeline_table.setRowCount(0)
        for entry in logs:
            table, source_id, timestamp = entry
            
            # Get detailed info
            details = get_log_details(table, source_id)
            if details:
                row = self.timeline_table.rowCount()
                self.timeline_table.insertRow(row)
                
                # Time
                time_item = QTableWidgetItem(timestamp)
                time_item.setFont(QFont("Arial", 12))
                self.timeline_table.setItem(row, 0, time_item)
                
                # Type with color
                log_type = table.replace("_logs", "").title()
                type_item = QTableWidgetItem(log_type)
                type_item.setFont(Fonts.LABEL)
                
                # Color code by type
                if "email" in table:
                    type_item.setForeground(Qt.GlobalColor.blue)
                elif "phone" in table:
                    type_item.setForeground(Qt.GlobalColor.darkGreen)
                elif "radio" in table:
                    type_item.setForeground(Qt.GlobalColor.darkYellow)
                elif "everbridge" in table:
                    type_item.setForeground(Qt.GlobalColor.red)
                
                self.timeline_table.setItem(row, 1, type_item)
                
                # Summary
                summary = self.create_log_summary(table, details)
                summary_item = QTableWidgetItem(summary)
                self.timeline_table.setItem(row, 2, summary_item)
                
                # Actions button
                view_btn = QPushButton("👁️ View")
                view_btn.setFont(Fonts.BUTTON)
                view_btn.setStyleSheet(get_button_style(Colors.INFO, 35))
                view_btn.clicked.connect(lambda checked, t=table, i=source_id: self.view_log_details(t, i))
                self.timeline_table.setCellWidget(row, 3, view_btn)
        
        self.timeline_table.resizeRowsToContents()
        self.status_bar.showMessage(f"Loaded {len(logs)} logs in timeline")

    def create_log_summary(self, table, details):
        """Create a meaningful summary based on log type"""
        if table == "email_logs":
            return f"{details.get('log_type', 'Email')}: {details.get('subject', 'No subject')} from {details.get('sender', 'Unknown')}"
        elif table == "phone_logs":
            caller = details.get('caller_name', 'Unknown caller')
            call_type = details.get('call_type', 'Phone')
            if call_type == "Facilities" and details.get('issue_type'):
                return f"{call_type}: {caller} - {details['issue_type']}/{details.get('issue_subtype', '')}"
            elif details.get('site_code'):
                return f"{call_type}: {caller} - Site {details['site_code']}"
            else:
                return f"{call_type}: {caller}"
        elif table == "radio_logs":
            return f"Radio: {details.get('unit', 'Unknown')} to {details.get('location', 'Unknown')} - {details.get('reason', '')}"
        elif table == "everbridge_logs":
            return f"Everbridge: Site {details.get('site_code', 'Unknown')} - {details.get('message', '')[:50]}..."
        else:
            return f"{table} #{details.get('id', '')}"

    def refresh_available_logs(self):
        all_logs = load_all_logs()
        self.all_logs_cache = all_logs  # Cache for filtering
        self.populate_logs_table(all_logs)

    def populate_logs_table(self, logs):
        self.available_logs_table.setRowCount(0)
        
        for log in logs:
            # Get detailed info
            details = get_log_details(log['table'], log['id'])
            if details:
                row = self.available_logs_table.rowCount()
                self.available_logs_table.insertRow(row)
                
                # Time
                time_item = QTableWidgetItem(log['timestamp'])
                time_item.setFont(QFont("Arial", 12))
                self.available_logs_table.setItem(row, 0, time_item)
                
                # Type
                log_type = log['source']
                type_item = QTableWidgetItem(log_type)
                type_item.setFont(Fonts.LABEL)
                self.available_logs_table.setItem(row, 1, type_item)
                
                # Summary
                summary = self.create_log_summary(log['table'], details)
                summary_item = QTableWidgetItem(summary)
                self.available_logs_table.setItem(row, 2, summary_item)
                
                # Store log info in row
                self.available_logs_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, log)
        
        self.available_logs_table.resizeRowsToContents()

    def filter_logs(self):
        if not hasattr(self, 'all_logs_cache'):
            return
        
        log_type = self.log_type_filter.currentText()
        
        filtered_logs = []
        for log in self.all_logs_cache:
            if log_type != "All" and log['source'] != log_type:
                continue
            filtered_logs.append(log)
        
        self.populate_logs_table(filtered_logs)
        self.status_bar.showMessage(f"Showing {len(filtered_logs)} {log_type} logs")

    def attach_selected_log(self):
        if not self.current_event_id:
            show_error(self, "Please select an event chain first")
            return
        
        selected_row = self.available_logs_table.currentRow()
        if selected_row < 0:
            show_error(self, "Please select a log to attach")
            return
        
        # Get log info from selected row
        log = self.available_logs_table.item(selected_row, 0).data(Qt.ItemDataRole.UserRole)
        
        # Check if already linked
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            SELECT COUNT(*) FROM event_links 
            WHERE event_id = ? AND source_table = ? AND source_id = ?
        """, (self.current_event_id, log['table'], log['id']))
        
        if c.fetchone()[0] > 0:
            conn.close()
            show_error(self, "This log is already part of the event chain")
            return
        
        conn.close()
        
        # Link the log
        link_log_to_event(self.current_event_id, log['table'], log['id'], log['timestamp'])
        
        show_success(self, "Log successfully added to event chain!")
        self.load_event_details()
        self.refresh_available_logs()
        self.refresh_events()

    def view_log_details(self, table, log_id):
        dialog = LogDetailDialog(table, log_id, self)
        dialog.exec()

    def prompt_create_event(self):
        title, ok = QInputDialog.getText(
            self, 
            "Create New Event Chain", 
            "Event title:",
            QLineEdit.EchoMode.Normal,
            ""
        )
        if ok and title.strip():
            desc, ok2 = QInputDialog.getMultiLineText(
                self, 
                "Event Description", 
                "Description (optional):"
            )
            event_id = create_event_chain(title.strip(), desc if ok2 else "")
            self.refresh_events()
            
            # Select the new event
            for i in range(self.event_list.count()):
                item = self.event_list.item(i)
                if item.data(Qt.ItemDataRole.UserRole)['id'] == event_id:
                    self.event_list.setCurrentItem(item)
                    break
            
            show_success(self, f"Event chain '{title}' created successfully!")

    def edit_event_chain(self):
        if not self.current_event_id:
            return
        
        # Get current values
        selected_item = self.event_list.currentItem()
        chain = selected_item.data(Qt.ItemDataRole.UserRole)
        
        # Get description from database
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT description FROM event_chains WHERE id = ?", (self.current_event_id,))
        result = c.fetchone()
        current_desc = result[0] if result else ""
        conn.close()
        
        # Show edit dialog
        dialog = EventChainEditDialog(
            self.current_event_id, 
            chain['title'], 
            current_desc,
            self
        )
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_title, new_desc = dialog.get_values()
            
            # Update in database
            update_event_chain(self.current_event_id, new_title, new_desc)
            
            self.refresh_events()
            show_success(self, "Event chain updated successfully!")