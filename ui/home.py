from PyQt6.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QLabel,
    QMessageBox, QMainWindow, QStatusBar
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QKeySequence, QFont, QAction, QShortcut
from ui.email_ui import EmailPanel
from ui.phone_ui import PhonePanel
from ui.radio_ui import RadioPanel
from ui.everbridge_ui import EverbridgePanel
from ui.event_manager_ui import EventManager
from ui.stats_ui import StatsPanel
from datetime import datetime

class HomeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Security Operations Logger")
        
        # Set minimum size for 1080p displays
        self.setMinimumSize(800, 600)
        
        # Start maximized
        self.showMaximized()
        
        # Setup UI
        self.setup_ui()
        self.setup_shortcuts()
        self.setup_menu()
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.update_status()
        
        # Timer for clock
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(1000)  # Update every second

    def setup_ui(self):
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)  # More spacing between elements
        layout.setContentsMargins(50, 30, 50, 30)  # Larger margins
        
        # Title with larger font
        title = QLabel("Security Operations Logger")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont("Arial", 28, QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet("color: #1976D2; margin-bottom: 30px;")
        layout.addWidget(title)
        
        # Subtitle with current user
        import os
        user = os.environ.get('USERNAME', 'Operator')
        subtitle = QLabel(f"Logged in as: {user}")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_font = QFont("Arial", 14)
        subtitle.setFont(subtitle_font)
        subtitle.setStyleSheet("color: #666; margin-bottom: 20px;")
        layout.addWidget(subtitle)
        
        # Logging section
        log_label = QLabel("📝 Log New Activity")
        log_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        section_font = QFont("Arial", 18, QFont.Weight.Bold)
        log_label.setFont(section_font)
        log_label.setStyleSheet("margin-top: 20px; margin-bottom: 10px;")
        layout.addWidget(log_label)
        
        # Button configuration with shortcuts
        from app_settings import app_settings
        show_shortcuts = app_settings.get("show_shortcuts", True)
        button_config = {
            "Emails": ("📧 Emails", "F1", "#2196F3"),
            "Phone": ("📞 Phone Calls", "F2", "#4CAF50"),
            "Radio": ("📻 Radio Dispatch", "F3", "#FF9800"),
            "Everbridge": ("⚠️ Everbridge Alerts", "F4", "#F44336")
        }
        
        self.buttons = {}
        for key, (text, shortcut, color) in button_config.items():
            btn_text = f"{text}\n({shortcut})" if show_shortcuts else text
            btn = QPushButton(btn_text)
            btn.setFixedHeight(80)  # Larger buttons
            btn_font = QFont("Arial", 16)
            btn.setFont(btn_font)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    border-radius: 10px;
                    padding: 10px;
                }}
                QPushButton:hover {{
                    background-color: {color}CC;
                }}
                QPushButton:pressed {{
                    background-color: {color}99;
                }}
            """)
            btn.setToolTip(f"Press {shortcut} to open {text}")
            self.buttons[key] = btn
            layout.addWidget(btn)
        
        # Management section
        layout.addStretch()
        manage_label = QLabel("📊 Manage & Analyze")
        manage_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        manage_label.setFont(section_font)
        manage_label.setStyleSheet("margin-top: 30px; margin-bottom: 10px;")
        layout.addWidget(manage_label)
        
        # Event Manager button
        event_text = "🔗 Event Manager\n(F5)" if show_shortcuts else "🔗 Event Manager"
        self.event_manager_btn = QPushButton(event_text)
        self.event_manager_btn.setFixedHeight(80)
        self.event_manager_btn.setFont(btn_font)
        self.event_manager_btn.setStyleSheet("""
            QPushButton {
                background-color: #7E57C2;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #7E57C2CC;
            }
            QPushButton:pressed {
                background-color: #7E57C299;
            }
        """)
        self.event_manager_btn.setToolTip("Press F5 to open Event Manager")
        layout.addWidget(self.event_manager_btn)
        
        # Stats button
        stats_text = "📊 Statistics & Reports\n(F6)" if show_shortcuts else "📊 Statistics & Reports"
        self.stats_btn = QPushButton(stats_text)
        self.stats_btn.setFixedHeight(80)
        self.stats_btn.setFont(btn_font)
        self.stats_btn.setStyleSheet("""
            QPushButton {
                background-color: #00897B;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #00897BCC;
            }
            QPushButton:pressed {
                background-color: #00897B99;
            }
        """)
        self.stats_btn.setToolTip("Press F6 to open Statistics")
        layout.addWidget(self.stats_btn)
        
        layout.addStretch()
        central_widget.setLayout(layout)
        
        # Connect buttons
        self.buttons["Emails"].clicked.connect(self.open_email_panel)
        self.buttons["Phone"].clicked.connect(self.open_phone_panel)
        self.buttons["Radio"].clicked.connect(self.open_radio_panel)
        self.buttons["Everbridge"].clicked.connect(self.open_everbridge_panel)
        self.event_manager_btn.clicked.connect(self.open_event_manager)
        self.stats_btn.clicked.connect(self.open_stats_panel)

    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # F-key shortcuts
        QShortcut(QKeySequence("F1"), self, self.open_email_panel)
        QShortcut(QKeySequence("F2"), self, self.open_phone_panel)
        QShortcut(QKeySequence("F3"), self, self.open_radio_panel)
        QShortcut(QKeySequence("F4"), self, self.open_everbridge_panel)
        QShortcut(QKeySequence("F5"), self, self.open_event_manager)
        QShortcut(QKeySequence("F6"), self, self.open_stats_panel)
        
        # Additional shortcuts
        QShortcut(QKeySequence("Ctrl+Q"), self, self.close)
        QShortcut(QKeySequence("F11"), self, self.toggle_fullscreen)
        QShortcut(QKeySequence("Ctrl+H"), self, self.show_help)

    def setup_menu(self):
        """Setup menu bar"""
        menubar = self.menuBar()
        menubar.setFont(QFont("Arial", 12))
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        settings_action = QAction("&Settings...", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self.show_settings)
        file_menu.addAction(settings_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        fullscreen_action = QAction("&Full Screen", self)
        fullscreen_action.setShortcut("F11")
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(fullscreen_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        shortcuts_action = QAction("&Keyboard Shortcuts", self)
        shortcuts_action.setShortcut("Ctrl+H")
        shortcuts_action.triggered.connect(self.show_help)
        help_menu.addAction(shortcuts_action)
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showMaximized()
        else:
            self.showFullScreen()

    def show_help(self):
        help_text = """
        <h2>Keyboard Shortcuts</h2>
        <table>
        <tr><td><b>F1</b></td><td>Open Email Logger</td></tr>
        <tr><td><b>F2</b></td><td>Open Phone Logger</td></tr>
        <tr><td><b>F3</b></td><td>Open Radio Logger</td></tr>
        <tr><td><b>F4</b></td><td>Open Everbridge Logger</td></tr>
        <tr><td><b>F5</b></td><td>Open Event Manager</td></tr>
        <tr><td><b>F6</b></td><td>Open Statistics</td></tr>
        <tr><td><b>F11</b></td><td>Toggle Full Screen</td></tr>
        <tr><td><b>Ctrl+Q</b></td><td>Exit Application</td></tr>
        <tr><td><b>Ctrl+H</b></td><td>Show This Help</td></tr>
        </table>
        """
        QMessageBox.information(self, "Keyboard Shortcuts", help_text)

    def update_status(self):
        """Update status bar with time"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.status_bar.showMessage(f"Ready | Current Time: {current_time}")

    def open_email_panel(self):
        self.email_window = EmailPanel()
        self.email_window.show()

    def open_phone_panel(self):
        self.phone_window = PhonePanel()
        self.phone_window.show()

    def open_radio_panel(self):
        self.radio_window = RadioPanel()
        self.radio_window.show()

    def open_everbridge_panel(self):
        self.everbridge_window = EverbridgePanel()
        self.everbridge_window.show()

    def open_event_manager(self):
        self.event_manager_window = EventManager()
        self.event_manager_window.show()

    def open_stats_panel(self):
        self.stats_window = StatsPanel()
        self.stats_window.show()
    
    def show_settings(self):
        """Show settings dialog"""
        from ui.settings_dialog import SettingsDialog
        dialog = SettingsDialog(self)
        dialog.exec()
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
        <h2>Security Operations Logger</h2>
        <p>Version 2.0</p>
        <p>A comprehensive logging system for security operations centers.</p>
        <br>
        <p><b>Features:</b></p>
        <ul>
        <li>Email, Phone, Radio, and Everbridge logging</li>
        <li>Event chain management</li>
        <li>Response time analytics</li>
        <li>Full keyboard navigation</li>
        <li>Customizable display scaling</li>
        </ul>
        <br>
        <p>Designed for ease of use by all operators.</p>
        """
        QMessageBox.about(self, "About Security Ops Logger", about_text)
    
    def closeEvent(self, event):
        """Handle window close event"""
        from app_settings import app_settings
        if app_settings.get("confirm_exit", True):
            reply = QMessageBox.question(
                self,
                "Confirm Exit",
                "Are you sure you want to exit?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()