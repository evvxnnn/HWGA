from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton,
    QHBoxLayout, QTextEdit, QLineEdit, QInputDialog, QMessageBox,
    QTableWidget, QTableWidgetItem, QSplitter, QGroupBox,
    QComboBox, QDialog, QDialogButtonBox, QListWidgetItem
)
from PyQt6.QtCore import Qt
from logic.event_handler import (
    get_event_chains, get_event_chain_logs, get_log_summary,
    create_event_chain, load_all_logs, link_log_to_event,
    update_event_chain
)
from database import get_log_details
import sqlite3
from database import DB_PATH

class EventChainEditDialog(QDialog):
    def __init__(self, event_id, current_title, current_description, parent=None):
        super().__init__(parent)
        self.event_id = event_id
        self.setWindowTitle("Edit Event Chain")
        self.setModal(True)
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # Title field
        layout.addWidget(QLabel("Event Title:"))
        self.title_edit = QLineEdit(current_title)
        layout.addWidget(self.title_edit)
        
        # Description field
        layout.addWidget(QLabel("Description:"))
        self.desc_edit = QTextEdit()
        self.desc_edit.setPlainText(current_description or "")
        self.desc_edit.setMaximumHeight(100)
        layout.addWidget(self.desc_edit)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
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
        self.setMinimumSize(500, 400)
        
        layout = QVBoxLayout()
        
        # Get log details
        details = get_log_details(table, log_id)
        
        if details:
            # Create a table to show all fields
            table_widget = QTableWidget()
            table_widget.setColumnCount(2)
            table_widget.setHorizontalHeaderLabels(["Field", "Value"])
            table_widget.horizontalHeader().setStretchLastSection(True)
            
            # Skip some internal fields
            skip_fields = ['id']
            
            for field, value in details.items():
                if field not in skip_fields and value is not None:
                    row = table_widget.rowCount()
                    table_widget.insertRow(row)
                    
                    # Format field name
                    field_name = field.replace('_', ' ').title()
                    table_widget.setItem(row, 0, QTableWidgetItem(field_name))
                    table_widget.setItem(row, 1, QTableWidgetItem(str(value)))
            
            layout.addWidget(table_widget)
        else:
            layout.addWidget(QLabel("Could not load log details"))
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)

class EventManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Event Manager")
        self.setMinimumSize(1200, 700)
        self.current_event_id = None
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout()
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left Panel: Event Chains
        left_widget = QWidget()
        left_panel = QVBoxLayout()
        
        left_panel.addWidget(QLabel("Event Chains"))
        
        self.event_list = QListWidget()
        self.event_list.itemSelectionChanged.connect(self.load_event_details)
        left_panel.addWidget(self.event_list)
        
        # Event chain buttons
        chain_btn_layout = QHBoxLayout()
        self.create_btn = QPushButton("➕ New")
        self.create_btn.clicked.connect(self.prompt_create_event)
        chain_btn_layout.addWidget(self.create_btn)
        
        self.edit_btn = QPushButton("✏️ Edit")
        self.edit_btn.clicked.connect(self.edit_event_chain)
        self.edit_btn.setEnabled(False)
        chain_btn_layout.addWidget(self.edit_btn)
        
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.refresh_events)
        chain_btn_layout.addWidget(self.refresh_btn)
        
        left_panel.addLayout(chain_btn_layout)
        left_widget.setLayout(left_panel)
        
        # Middle Panel: Event Timeline
        middle_widget = QWidget()
        middle_panel = QVBoxLayout()
        
        self.timeline_label = QLabel("Event Timeline")
        middle_panel.addWidget(self.timeline_label)
        
        # Timeline table for better display
        self.timeline_table = QTableWidget()
        self.timeline_table.setColumnCount(4)
        self.timeline_table.setHorizontalHeaderLabels([
            "Time", "Type", "Summary", "Actions"
        ])
        self.timeline_table.setAlternatingRowColors(True)
        middle_panel.addWidget(self.timeline_table)
        
        middle_widget.setLayout(middle_panel)
        
        # Right Panel: Available Logs
        right_widget = QWidget()
        right_panel = QVBoxLayout()
        
        # Log filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Type:"))
        self.log_type_filter = QComboBox()
        self.log_type_filter.addItems(["All", "Email", "Phone", "Radio", "Everbridge"])
        self.log_type_filter.currentTextChanged.connect(self.filter_logs)
        filter_layout.addWidget(self.log_type_filter)
        right_panel.addLayout(filter_layout)
        
        right_panel.addWidget(QLabel("Available Logs"))
        
        # Available logs table
        self.available_logs_table = QTableWidget()
        self.available_logs_table.setColumnCount(3)
        self.available_logs_table.setHorizontalHeaderLabels([
            "Time", "Type", "Summary"
        ])
        self.available_logs_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        right_panel.addWidget(self.available_logs_table)
        
        self.attach_btn = QPushButton("⬅️ Attach Selected Log to Event")
        self.attach_btn.clicked.connect(self.attach_selected_log)
        right_panel.addWidget(self.attach_btn)
        
        right_widget.setLayout(right_panel)
        
        # Add widgets to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(middle_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([300, 500, 400])
        
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)
        
        self.refresh_events()
        self.refresh_available_logs()

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
            
            # Create list item
            item_text = f"[{chain['id']}] {chain['title']} ({log_count} logs)"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, chain)
            self.event_list.addItem(item)

    def load_event_details(self):
        selected_item = self.event_list.currentItem()
        if not selected_item:
            self.edit_btn.setEnabled(False)
            return
        
        chain = selected_item.data(Qt.ItemDataRole.UserRole)
        self.current_event_id = chain['id']
        self.edit_btn.setEnabled(True)
        
        # Update timeline label
        self.timeline_label.setText(f"Event Timeline: {chain['title']}")
        
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
                self.timeline_table.setItem(row, 0, QTableWidgetItem(timestamp))
                
                # Type
                log_type = table.replace("_logs", "").title()
                self.timeline_table.setItem(row, 1, QTableWidgetItem(log_type))
                
                # Summary
                summary = self.create_log_summary(table, details)
                self.timeline_table.setItem(row, 2, QTableWidgetItem(summary))
                
                # Actions button
                view_btn = QPushButton("View")
                view_btn.clicked.connect(lambda checked, t=table, i=source_id: self.view_log_details(t, i))
                self.timeline_table.setCellWidget(row, 3, view_btn)
        
        self.timeline_table.resizeColumnsToContents()

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
                self.available_logs_table.setItem(row, 0, QTableWidgetItem(log['timestamp']))
                
                # Type
                log_type = log['source']
                self.available_logs_table.setItem(row, 1, QTableWidgetItem(log_type))
                
                # Summary
                summary = self.create_log_summary(log['table'], details)
                self.available_logs_table.setItem(row, 2, QTableWidgetItem(summary))
                
                # Store log info in row
                self.available_logs_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, log)

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

    def attach_selected_log(self):
        if not self.current_event_id:
            QMessageBox.warning(self, "No Event Selected", "Please select an event chain first.")
            return
        
        selected_row = self.available_logs_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "No Log Selected", "Please select a log to attach.")
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
            QMessageBox.information(self, "Already Linked", "This log is already part of the event chain.")
            return
        
        conn.close()
        
        # Link the log
        link_log_to_event(self.current_event_id, log['table'], log['id'], log['timestamp'])
        
        QMessageBox.information(self, "Linked", "Log successfully added to event chain.")
        self.load_event_details()
        self.refresh_available_logs()

    def view_log_details(self, table, log_id):
        dialog = LogDetailDialog(table, log_id, self)
        dialog.exec()

    def prompt_create_event(self):
        title, ok = QInputDialog.getText(self, "Create New Event Chain", "Event title:")
        if ok and title.strip():
            desc, ok2 = QInputDialog.getMultiLineText(self, "Event Description", "Description (optional):")
            event_id = create_event_chain(title.strip(), desc if ok2 else "")
            self.refresh_events()
            
            # Select the new event
            for i in range(self.event_list.count()):
                item = self.event_list.item(i)
                if item.data(Qt.ItemDataRole.UserRole)['id'] == event_id:
                    self.event_list.setCurrentItem(item)
                    break

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
            QMessageBox.information(self, "Updated", "Event chain updated successfully.")