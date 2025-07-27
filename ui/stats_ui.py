from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QTableWidget,
    QTableWidgetItem, QPushButton, QHBoxLayout, QGroupBox,
    QTextEdit, QTabWidget, QMainWindow, QStatusBar,
    QHeaderView, QProgressBar
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QShortcut, QKeySequence
import sqlite3
from datetime import datetime, timedelta
from database import DB_PATH
from ui.styles import (
    Fonts, Colors,
    INPUT_STYLE, TABLE_STYLE, LIST_STYLE, DROPDOWN_STYLE, TAB_STYLE,
    get_button_style, make_accessible,
    show_error, show_success
)



class StatsPanel(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Statistics & Reports")
        self.setMinimumSize(1200, 800)
        self.showMaximized()
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Loading statistics...")
        
        self.init_ui()
        self.setup_shortcuts()

    def init_ui(self):
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 20, 30, 20)

        # Title
        title = QLabel("📊 Statistics & Reports")
        title.setFont(Fonts.TITLE)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"color: {Colors.STATS}; margin-bottom: 20px;")
        layout.addWidget(title)

        # Create tabs for different stats views
        self.tabs = QTabWidget()
        self.tabs.setFont(Fonts.NORMAL)
        self.tabs.setStyleSheet(TAB_STYLE)
        
        # Response Times Tab
        self.response_tab = QWidget()
        self.setup_response_times_tab()
        self.tabs.addTab(self.response_tab, "⏱️ Response Times")

        # Activity Summary Tab
        self.summary_tab = QWidget()
        self.setup_summary_tab()
        self.tabs.addTab(self.summary_tab, "📈 Activity Summary")

        # Event Analysis Tab
        self.event_tab = QWidget()
        self.setup_event_analysis_tab()
        self.tabs.addTab(self.event_tab, "🔍 Event Analysis")

        layout.addWidget(self.tabs)
        self.setLayout(layout)
        
        central_widget.setLayout(layout)

    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        QShortcut(QKeySequence("F5"), self, self.refresh_current_tab)
        QShortcut(QKeySequence("Ctrl+P"), self, self.print_report)

    def setup_response_times_tab(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Event Chain selector
        chain_group = QGroupBox("Select Event Chain")
        chain_group.setFont(Fonts.LABEL)
        chain_layout = QHBoxLayout()
        
        self.chain_combo = QComboBox()
        self.chain_combo.setFont(Fonts.NORMAL)
        self.chain_combo.setStyleSheet(DROPDOWN_STYLE)
        self.chain_combo.setMinimumHeight(45)
        self.chain_combo.currentIndexChanged.connect(self.analyze_chain)
        chain_layout.addWidget(self.chain_combo)
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setFont(Fonts.BUTTON)
        refresh_btn.setStyleSheet(get_button_style(Colors.INFO, 45))
        refresh_btn.clicked.connect(self.load_event_chains)
        chain_layout.addWidget(refresh_btn)
        
        chain_layout.addStretch()
        chain_group.setLayout(chain_layout)
        layout.addWidget(chain_group)

        # Response times table
        self.response_table = QTableWidget()
        self.response_table.setFont(Fonts.NORMAL)
        self.response_table.setStyleSheet(TABLE_STYLE)
        self.response_table.setColumnCount(5)
        self.response_table.setHorizontalHeaderLabels([
            "From Event", "To Event", "Response Time", "From Type", "To Type"
        ])
        self.response_table.setAlternatingRowColors(True)
        self.response_table.verticalHeader().setVisible(False)
        
        # Set column stretching
        header = self.response_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.response_table)

        # Stats summary with visual indicators
        self.stats_group = QGroupBox("Response Time Statistics")
        self.stats_group.setFont(Fonts.LABEL)
        stats_layout = QVBoxLayout()
        
        # Average response time with progress bar
        avg_layout = QHBoxLayout()
        avg_label = QLabel("Average Response Time:")
        avg_label.setFont(Fonts.LABEL)
        avg_layout.addWidget(avg_label)
        
        self.avg_progress = QProgressBar()
        self.avg_progress.setMinimum(0)
        self.avg_progress.setMaximum(60)  # 60 minutes max
        self.avg_progress.setTextVisible(True)
        self.avg_progress.setFormat("%v minutes")
        self.avg_progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #4CAF50;
                border-radius: 5px;
                text-align: center;
                font-size: 14px;
                height: 30px;
                color: white;
                background-color: #2d2d30;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)
        avg_layout.addWidget(self.avg_progress)
        stats_layout.addLayout(avg_layout)
        
        # Stats text
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setFont(Fonts.NORMAL)
        self.stats_text.setMaximumHeight(200)
        self.stats_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #DDD;
                border-radius: 5px;
                padding: 10px;
                background-color: #F5F5F5;
            }
        """)
        stats_layout.addWidget(self.stats_text)
        
        self.stats_group.setLayout(stats_layout)
        layout.addWidget(self.stats_group)

        self.response_tab.setLayout(layout)
        self.load_event_chains()

    def setup_summary_tab(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Summary info
        info_group = QGroupBox("Activity Summary Information")
        info_group.setFont(Fonts.LABEL)
        info_layout = QVBoxLayout()
        
        info_text = QLabel("Overview of all logged activities in the system")
        info_text.setFont(Fonts.NORMAL)
        info_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(info_text)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # Summary table
        self.summary_table = QTableWidget()
        self.summary_table.setFont(Fonts.NORMAL)
        self.summary_table.setStyleSheet(TABLE_STYLE)
        self.summary_table.setColumnCount(5)
        self.summary_table.setHorizontalHeaderLabels([
            "Log Type", "Total Count", "Today", "This Week", "Average per Day"
        ])
        self.summary_table.setAlternatingRowColors(True)
        self.summary_table.verticalHeader().setVisible(False)
        
        # Set column stretching
        header = self.summary_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.summary_table)

        # Visual summary
        self.visual_group = QGroupBox("Quick Statistics")
        self.visual_group.setFont(Fonts.LABEL)
        visual_layout = QHBoxLayout()
        
        # Create stat cards
        self.email_card = self.create_stat_card("📧 Emails", "0", Colors.EMAIL)
        self.phone_card = self.create_stat_card("📞 Calls", "0", Colors.PHONE)
        self.radio_card = self.create_stat_card("📻 Radio", "0", Colors.RADIO)
        self.everbridge_card = self.create_stat_card("⚠️ Alerts", "0", Colors.EVERBRIDGE)
        
        visual_layout.addWidget(self.email_card)
        visual_layout.addWidget(self.phone_card)
        visual_layout.addWidget(self.radio_card)
        visual_layout.addWidget(self.everbridge_card)
        
        self.visual_group.setLayout(visual_layout)
        layout.addWidget(self.visual_group)

        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh Summary")
        refresh_btn.setFont(Fonts.BUTTON)
        refresh_btn.setStyleSheet(get_button_style(Colors.INFO, 50))
        refresh_btn.clicked.connect(self.load_summary_stats)
        layout.addWidget(refresh_btn)

        self.summary_tab.setLayout(layout)
        self.load_summary_stats()

    def create_stat_card(self, title, value, color):
        """Create a visual statistics card"""
        card = QGroupBox()
        card.setStyleSheet(f"""
            QGroupBox {{
                border: 3px solid {color};
                border-radius: 10px;
                padding: 20px;
                background-color: white;
            }}
        """)
        
        layout = QVBoxLayout()
        
        title_label = QLabel(title)
        title_label.setFont(Fonts.LABEL)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(f"color: {color};")
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 36, QFont.Weight.Bold))
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setObjectName(f"{title}_value")  # For updating later
        layout.addWidget(value_label)
        
        card.setLayout(layout)
        return card

    def setup_event_analysis_tab(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Analysis info
        info_label = QLabel("Analysis of all event chains in the system")
        info_label.setFont(Fonts.NORMAL)
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("color: #666; margin-bottom: 10px;")
        layout.addWidget(info_label)

        # Analysis table
        self.analysis_table = QTableWidget()
        self.analysis_table.setFont(Fonts.NORMAL)
        self.analysis_table.setStyleSheet(TABLE_STYLE)
        self.analysis_table.setColumnCount(6)
        self.analysis_table.setHorizontalHeaderLabels([
            "Event Chain", "Total Logs", "Duration", "Avg Response", "Status", "Created"
        ])
        self.analysis_table.setAlternatingRowColors(True)
        self.analysis_table.verticalHeader().setVisible(False)
        
        # Set column stretching
        header = self.analysis_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for i in range(1, 6):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.analysis_table)

        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh Analysis")
        refresh_btn.setFont(Fonts.BUTTON)
        refresh_btn.setStyleSheet(get_button_style(Colors.INFO, 50))
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

        self.chain_combo.addItem("Select an event chain...", None)
        for chain_id, title in chains:
            self.chain_combo.addItem(f"[{chain_id}] {title}", chain_id)
        
        self.status_bar.showMessage(f"Loaded {len(chains)} event chains")

    def analyze_chain(self):
        if self.chain_combo.currentIndex() <= 0:
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
            self.stats_text.setText("Not enough events to calculate response times.\n\nAt least 2 logs must be linked to calculate response times.")
            self.avg_progress.setValue(0)
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
                
                # Format the display
                from_display = f"{from_log[0].replace('_logs', '').title()} #{from_log[1]}"
                to_display = f"{to_log[0].replace('_logs', '').title()} #{to_log[1]}"
                
                self.response_table.setItem(row, 0, QTableWidgetItem(from_display))
                self.response_table.setItem(row, 1, QTableWidgetItem(to_display))
                
                # Response time with color coding
                time_item = QTableWidgetItem(f"{minutes:.1f} minutes")
                if minutes < 5:
                    time_item.setForeground(QColor("#4CAF50"))  # Green for fast
                elif minutes < 15:
                    time_item.setForeground(QColor("#FF9800"))  # Orange for moderate
                else:
                    time_item.setForeground(QColor("#F44336"))  # Red for slow
                
                self.response_table.setItem(row, 2, time_item)
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

            # Update progress bar
            self.avg_progress.setValue(int(min(avg_response, 60)))

            # Color code the progress bar
            if avg_response < 5:
                self.avg_progress.setStyleSheet("""
                    QProgressBar::chunk { background-color: #4CAF50; }
                """)
            elif avg_response < 15:
                self.avg_progress.setStyleSheet("""
                    QProgressBar::chunk { background-color: #FF9800; }
                """)
            else:
                self.avg_progress.setStyleSheet("""
                    QProgressBar::chunk { background-color: #F44336; }
                """)

            stats_text = f"""📊 RESPONSE TIME ANALYSIS
            
Average Response Time: {avg_response:.1f} minutes
Fastest Response: {min_response:.1f} minutes
Slowest Response: {max_response:.1f} minutes

Total Events in Chain: {len(logs)}
Response Times Calculated: {len(response_times)}

Performance Rating: {self.get_performance_rating(avg_response)}"""
            
            self.stats_text.setText(stats_text)

    def get_performance_rating(self, avg_minutes):
        """Get performance rating based on average response time"""
        if avg_minutes < 5:
            return "⭐⭐⭐⭐⭐ Excellent"
        elif avg_minutes < 10:
            return "⭐⭐⭐⭐ Very Good"
        elif avg_minutes < 15:
            return "⭐⭐⭐ Good"
        elif avg_minutes < 30:
            return "⭐⭐ Fair"
        else:
            return "⭐ Needs Improvement"

    def load_summary_stats(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        self.summary_table.setRowCount(0)
        
        # Current date for calculations
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)

        # Get counts for each log type
        log_types = [
            ("Email Logs", "email_logs", Colors.EMAIL),
            ("Phone Logs", "phone_logs", Colors.PHONE),
            ("Radio Logs", "radio_logs", Colors.RADIO),
            ("Everbridge Logs", "everbridge_logs", Colors.EVERBRIDGE)
        ]

        totals = {"emails": 0, "calls": 0, "radio": 0, "alerts": 0}

        for display_name, table_name, color in log_types:
            # Total count
            c.execute(f"SELECT COUNT(*) FROM {table_name}")
            total_count = c.fetchone()[0]

            # Today's count
            c.execute(f"""
                SELECT COUNT(*) FROM {table_name} 
                WHERE DATE(created_at) = DATE('now', 'localtime')
            """)
            today_count = c.fetchone()[0]

            # This week's count
            c.execute(f"""
                SELECT COUNT(*) FROM {table_name} 
                WHERE DATE(created_at) >= DATE('now', '-7 days', 'localtime')
            """)
            week_count = c.fetchone()[0]

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
                        avg_per_day = f"{total_count / days:.1f}"
                except:
                    pass

            row = self.summary_table.rowCount()
            self.summary_table.insertRow(row)
            
            # Add colored log type
            type_item = QTableWidgetItem(display_name)
            type_item.setForeground(QColor(color))
            type_item.setFont(Fonts.LABEL)
            self.summary_table.setItem(row, 0, type_item)
            
            self.summary_table.setItem(row, 1, QTableWidgetItem(str(total_count)))
            self.summary_table.setItem(row, 2, QTableWidgetItem(str(today_count)))
            self.summary_table.setItem(row, 3, QTableWidgetItem(str(week_count)))
            self.summary_table.setItem(row, 4, QTableWidgetItem(avg_per_day))

            # Update stat cards
            if "Email" in display_name:
                self.email_card.findChild(QLabel, "📧 Emails_value").setText(str(total_count))
            elif "Phone" in display_name:
                self.phone_card.findChild(QLabel, "📞 Calls_value").setText(str(total_count))
            elif "Radio" in display_name:
                self.radio_card.findChild(QLabel, "📻 Radio_value").setText(str(total_count))
            elif "Everbridge" in display_name:
                self.everbridge_card.findChild(QLabel, "⚠️ Alerts_value").setText(str(total_count))

        conn.close()
        self.status_bar.showMessage("Summary statistics updated")

    def load_event_analysis(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        self.analysis_table.setRowCount(0)

        # Get all event chains
        c.execute("SELECT id, title, created_at FROM event_chains")
        chains = c.fetchall()

        for chain_id, title, created_at in chains:
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
            status = "Empty"

            if log_count > 1 and result[1] and result[2]:
                try:
                    start = datetime.strptime(result[1], "%Y-%m-%d %H:%M:%S")
                    end = datetime.strptime(result[2], "%Y-%m-%d %H:%M:%S")
                    duration_mins = (end - start).total_seconds() / 60
                    
                    if duration_mins < 60:
                        duration = f"{duration_mins:.1f} min"
                    else:
                        hours = duration_mins / 60
                        duration = f"{hours:.1f} hrs"
                    
                    # Calculate average response time
                    avg_response_mins = duration_mins / (log_count - 1)
                    avg_response = f"{avg_response_mins:.1f} min"
                    
                    # Determine status
                    if avg_response_mins < 10:
                        status = "✅ Excellent"
                    elif avg_response_mins < 20:
                        status = "⚠️ Good"
                    else:
                        status = "❌ Slow"
                except:
                    pass
            elif log_count == 1:
                status = "📝 Single Log"

            row = self.analysis_table.rowCount()
            self.analysis_table.insertRow(row)
            
            self.analysis_table.setItem(row, 0, QTableWidgetItem(title))
            self.analysis_table.setItem(row, 1, QTableWidgetItem(str(log_count)))
            self.analysis_table.setItem(row, 2, QTableWidgetItem(duration))
            self.analysis_table.setItem(row, 3, QTableWidgetItem(avg_response))
            
            status_item = QTableWidgetItem(status)
            if "Excellent" in status:
                status_item.setForeground(QColor("#4CAF50"))
            elif "Good" in status:
                status_item.setForeground(QColor("#FF9800"))
            elif "Slow" in status:
                status_item.setForeground(QColor("#F44336"))
            
            self.analysis_table.setItem(row, 4, status_item)
            self.analysis_table.setItem(row, 5, QTableWidgetItem(created_at[:10]))  # Date only

        conn.close()
        self.status_bar.showMessage(f"Analyzed {len(chains)} event chains")

    def refresh_current_tab(self):
        """Refresh the current tab"""
        current_index = self.tabs.currentIndex()
        if current_index == 0:
            self.load_event_chains()
        elif current_index == 1:
            self.load_summary_stats()
        elif current_index == 2:
            self.load_event_analysis()

    def print_report(self):
        """Placeholder for print functionality"""
        show_success(self, "Print feature coming soon!\n\nFor now, you can take screenshots of the statistics.")