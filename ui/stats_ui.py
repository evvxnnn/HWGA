from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QTableWidget,
    QTableWidgetItem, QPushButton, QHBoxLayout, QGroupBox,
    QTextEdit, QTabWidget
)
from PyQt6.QtCore import Qt
import sqlite3
from datetime import datetime
from database import DB_PATH

class StatsPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Statistics & Reports")
        self.setMinimumSize(1000, 600)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Create tabs for different stats views
        self.tabs = QTabWidget()
        
        # Response Times Tab
        self.response_tab = QWidget()
        self.setup_response_times_tab()
        self.tabs.addTab(self.response_tab, "Response Times")

        # Activity Summary Tab
        self.summary_tab = QWidget()
        self.setup_summary_tab()
        self.tabs.addTab(self.summary_tab, "Activity Summary")

        # Event Analysis Tab
        self.event_tab = QWidget()
        self.setup_event_analysis_tab()
        self.tabs.addTab(self.event_tab, "Event Analysis")

        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def setup_response_times_tab(self):
        layout = QVBoxLayout()

        # Event Chain selector
        chain_layout = QHBoxLayout()
        chain_layout.addWidget(QLabel("Select Event Chain:"))
        self.chain_combo = QComboBox()
        self.chain_combo.currentIndexChanged.connect(self.analyze_chain)
        chain_layout.addWidget(self.chain_combo)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_event_chains)
        chain_layout.addWidget(refresh_btn)
        chain_layout.addStretch()
        
        layout.addLayout(chain_layout)

        # Response times table
        self.response_table = QTableWidget()
        self.response_table.setColumnCount(5)
        self.response_table.setHorizontalHeaderLabels([
            "From Event", "To Event", "Response Time", "From Type", "To Type"
        ])
        self.response_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.response_table)

        # Stats summary
        self.stats_group = QGroupBox("Response Time Statistics")
        stats_layout = QVBoxLayout()
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setMaximumHeight(150)
        stats_layout.addWidget(self.stats_text)
        self.stats_group.setLayout(stats_layout)
        layout.addWidget(self.stats_group)

        self.response_tab.setLayout(layout)
        self.load_event_chains()

    def setup_summary_tab(self):
        layout = QVBoxLayout()

        # Date range selector could go here
        layout.addWidget(QLabel("Activity Summary"))

        # Summary table
        self.summary_table = QTableWidget()
        self.summary_table.setColumnCount(3)
        self.summary_table.setHorizontalHeaderLabels(["Log Type", "Count", "Average per Day"])
        layout.addWidget(self.summary_table)

        # Refresh button
        refresh_btn = QPushButton("Refresh Summary")
        refresh_btn.clicked.connect(self.load_summary_stats)
        layout.addWidget(refresh_btn)

        self.summary_tab.setLayout(layout)
        self.load_summary_stats()

    def setup_event_analysis_tab(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Event Chain Analysis"))

        # Analysis table
        self.analysis_table = QTableWidget()
        self.analysis_table.setColumnCount(4)
        self.analysis_table.setHorizontalHeaderLabels([
            "Event Chain", "Total Logs", "Duration", "Avg Response Time"
        ])
        layout.addWidget(self.analysis_table)

        # Refresh button
        refresh_btn = QPushButton("Refresh Analysis")
        refresh_btn.clicked.connect(self.load_event_analysis)
        layout.addWidget(refresh_btn)

        self.event_tab.setLayout(layout)
        self.load_event_analysis()

    def load_event_chains(self):
        self.chain_combo.clear()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id, title FROM event_chains ORDER BY created_at DESC")
        chains = c.fetchall()
        conn.close()

        for chain_id, title in chains:
            self.chain_combo.addItem(f"{chain_id}: {title}", chain_id)

    def analyze_chain(self):
        if self.chain_combo.currentIndex() < 0:
            return

        event_id = self.chain_combo.currentData()
        if not event_id:
            return

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # Get all logs in this chain ordered by timestamp
        c.execute("""
            SELECT el.source_table, el.source_id, el.timestamp
            FROM event_links el
            WHERE el.event_id = ?
            ORDER BY el.timestamp
        """, (event_id,))
        
        logs = c.fetchall()
        conn.close()

        # Clear table
        self.response_table.setRowCount(0)

        if len(logs) < 2:
            self.stats_text.setText("Not enough events to calculate response times.")
            return

        # Calculate response times between consecutive events
        response_times = []
        for i in range(len(logs) - 1):
            from_log = logs[i]
            to_log = logs[i + 1]

            # Parse timestamps
            try:
                from_time = datetime.strptime(from_log[2], "%Y-%m-%d %H:%M:%S")
                to_time = datetime.strptime(to_log[2], "%Y-%m-%d %H:%M:%S")
                
                # Calculate difference
                diff = to_time - from_time
                minutes = diff.total_seconds() / 60

                # Add to table
                row = self.response_table.rowCount()
                self.response_table.insertRow(row)
                self.response_table.setItem(row, 0, QTableWidgetItem(f"{from_log[0]} #{from_log[1]}"))
                self.response_table.setItem(row, 1, QTableWidgetItem(f"{to_log[0]} #{to_log[1]}"))
                self.response_table.setItem(row, 2, QTableWidgetItem(f"{minutes:.1f} minutes"))
                self.response_table.setItem(row, 3, QTableWidgetItem(from_log[0].replace("_logs", "")))
                self.response_table.setItem(row, 4, QTableWidgetItem(to_log[0].replace("_logs", "")))

                response_times.append(minutes)
            except Exception as e:
                print(f"Error parsing timestamps: {e}")

        # Calculate statistics
        if response_times:
            avg_response = sum(response_times) / len(response_times)
            min_response = min(response_times)
            max_response = max(response_times)

            stats_text = f"""Average Response Time: {avg_response:.1f} minutes
Fastest Response: {min_response:.1f} minutes
Slowest Response: {max_response:.1f} minutes
Total Events in Chain: {len(logs)}
Response Times Calculated: {len(response_times)}"""
            
            self.stats_text.setText(stats_text)

    def load_summary_stats(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        self.summary_table.setRowCount(0)

        # Get counts for each log type
        log_types = [
            ("Email Logs", "email_logs"),
            ("Phone Logs", "phone_logs"),
            ("Radio Logs", "radio_logs"),
            ("Everbridge Logs", "everbridge_logs")
        ]

        for display_name, table_name in log_types:
            c.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = c.fetchone()[0]

            # Get date range for average calculation
            c.execute(f"""
                SELECT MIN(created_at), MAX(created_at) 
                FROM {table_name} 
                WHERE created_at IS NOT NULL
            """)
            date_range = c.fetchone()

            avg_per_day = "N/A"
            if date_range[0] and date_range[1]:
                try:
                    start = datetime.strptime(date_range[0], "%Y-%m-%d %H:%M:%S")
                    end = datetime.strptime(date_range[1], "%Y-%m-%d %H:%M:%S")
                    days = (end - start).days + 1
                    if days > 0:
                        avg_per_day = f"{count / days:.1f}"
                except:
                    pass

            row = self.summary_table.rowCount()
            self.summary_table.insertRow(row)
            self.summary_table.setItem(row, 0, QTableWidgetItem(display_name))
            self.summary_table.setItem(row, 1, QTableWidgetItem(str(count)))
            self.summary_table.setItem(row, 2, QTableWidgetItem(avg_per_day))

        conn.close()

    def load_event_analysis(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        self.analysis_table.setRowCount(0)

        # Get all event chains
        c.execute("SELECT id, title FROM event_chains")
        chains = c.fetchall()

        for chain_id, title in chains:
            # Get log count
            c.execute("""
                SELECT COUNT(*), MIN(timestamp), MAX(timestamp)
                FROM event_links
                WHERE event_id = ?
            """, (chain_id,))
            
            result = c.fetchone()
            log_count = result[0]
            
            duration = "N/A"
            avg_response = "N/A"

            if log_count > 1 and result[1] and result[2]:
                try:
                    start = datetime.strptime(result[1], "%Y-%m-%d %H:%M:%S")
                    end = datetime.strptime(result[2], "%Y-%m-%d %H:%M:%S")
                    duration_mins = (end - start).total_seconds() / 60
                    duration = f"{duration_mins:.1f} min"
                    
                    # Calculate average response time
                    avg_response_mins = duration_mins / (log_count - 1)
                    avg_response = f"{avg_response_mins:.1f} min"
                except:
                    pass

            row = self.analysis_table.rowCount()
            self.analysis_table.insertRow(row)
            self.analysis_table.setItem(row, 0, QTableWidgetItem(title))
            self.analysis_table.setItem(row, 1, QTableWidgetItem(str(log_count)))
            self.analysis_table.setItem(row, 2, QTableWidgetItem(duration))
            self.analysis_table.setItem(row, 3, QTableWidgetItem(avg_response))

        conn.close()