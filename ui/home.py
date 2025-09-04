from PyQt6.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QLabel,
    QMessageBox, QMainWindow, QStatusBar, QMenu
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QKeySequence, QFont, QAction, QShortcut
from ui.help_utils import HelpButton, get_help_training_id
from ui.email_ui import EmailPanel
from ui.phone_ui import PhonePanel
from ui.radio_ui import RadioPanel
from ui.everbridge_ui import EverbridgePanel
from ui.event_manager_ui import EventManager
from ui.stats_ui import StatsPanel
from ui.launcher_config import LauncherButton
from datetime import datetime
import json

class HomeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Security Operations Logger")
        
        # Set minimum size for 1080p displays
        self.setMinimumSize(800, 600)
        
        # Start maximized
        self.showMaximized()
        
        # Load launcher configurations
        self.launcher_configs = self.load_launcher_configs()
        
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
        
        # Use grid layout for square buttons
        from PyQt6.QtWidgets import QGridLayout, QHBoxLayout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(50, 30, 50, 30)
        
        # Title with help button
        title_layout = QHBoxLayout()
        title_layout.addStretch()
        
        title = QLabel("Security Operations Logger")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        from ui.styles import Fonts
        title.setFont(Fonts.TITLE)
        title.setStyleSheet("color: #e0e0e0;")
        title_layout.addWidget(title)
        
        title_layout.addStretch()
        
        # Add help button
        help_btn = HelpButton("Home Screen", get_help_training_id("home"), self)
        title_layout.addWidget(help_btn)
        
        main_layout.addLayout(title_layout)
        
        # Subtitle with current user
        import os
        user = os.environ.get('USERNAME', 'Operator')
        subtitle = QLabel(f"Logged in as: {user}")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setFont(Fonts.NORMAL)
        subtitle.setStyleSheet("color: #808080; margin-bottom: 20px;")
        main_layout.addWidget(subtitle)
        
        # Logging section
        log_label = QLabel("Log New Activity")
        log_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        log_label.setFont(Fonts.SUBTITLE)
        log_label.setStyleSheet("color: #e0e0e0; margin-top: 20px; margin-bottom: 15px;")
        main_layout.addWidget(log_label)
        
        # Create grid for square buttons
        from app_settings import app_settings
        from ui.styles import get_button_style
        show_shortcuts = app_settings.get("show_shortcuts", True)
        
        # Grid layout for logging buttons
        log_grid = QGridLayout()
        log_grid.setSpacing(15)
        
        button_config = [
            ("Emails", "Email", "F1", 0, 0),
            ("Phone", "Phone", "F2", 0, 1),
            ("Radio", "Radio", "F3", 0, 2),
            ("Everbridge", "Everbridge", "F4", 0, 3),
            ("Facilities", "Facilities\nTicket", "Shift+F1", 1, 0)
        ]
        
        self.buttons = {}
        for key, text, shortcut, row, col in button_config:
            btn_text = f"{text}\n({shortcut})" if show_shortcuts else text
            btn = QPushButton(btn_text)
            btn.setFixedSize(120, 120)  # Square buttons
            btn.setFont(Fonts.BUTTON)
            btn.setStyleSheet(get_button_style())
            btn.setToolTip(f"Press {shortcut} to open {text} Log")
            self.buttons[key] = btn
            log_grid.addWidget(btn, row, col)
        
        # Center the grid
        grid_container = QWidget()
        grid_container.setLayout(log_grid)
        grid_container.setMaximumWidth(550)
        
        h_layout = QHBoxLayout()
        h_layout.addStretch()
        h_layout.addWidget(grid_container)
        h_layout.addStretch()
        main_layout.addLayout(h_layout)
        
        # Management section
        main_layout.addStretch()
        manage_label = QLabel("Management Tools")
        manage_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        manage_label.setFont(Fonts.SUBTITLE)
        manage_label.setStyleSheet("color: #e0e0e0; margin-top: 30px; margin-bottom: 15px;")
        main_layout.addWidget(manage_label)
        
        # Grid layout for management buttons
        manage_grid = QGridLayout()
        manage_grid.setSpacing(15)
        
        # Management buttons configuration
        manage_buttons = [
            ("event_manager", "Event\nManager", "F5", 0, 0),
            ("stats", "Statistics", "F6", 0, 1),
            ("logs", "View Logs", "F7", 0, 2),
            ("training", "Training", "F8", 0, 3)
        ]
        
        self.manage_buttons = {}
        for key, text, shortcut, row, col in manage_buttons:
            btn_text = f"{text}\n({shortcut})" if show_shortcuts else text
            btn = QPushButton(btn_text)
            btn.setFixedSize(120, 120)  # Square buttons
            btn.setFont(Fonts.BUTTON)
            btn.setStyleSheet(get_button_style())
            btn.setToolTip(f"Press {shortcut} to open {text}")
            self.manage_buttons[key] = btn
            manage_grid.addWidget(btn, row, col)
        
        # Center the management grid
        manage_container = QWidget()
        manage_container.setLayout(manage_grid)
        manage_container.setMaximumWidth(550)
        
        h_layout2 = QHBoxLayout()
        h_layout2.addStretch()
        h_layout2.addWidget(manage_container)
        h_layout2.addStretch()
        main_layout.addLayout(h_layout2)
        
        # Quick Launch section
        main_layout.addStretch()
        launch_label = QLabel("Quick Launch")
        launch_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        launch_label.setFont(Fonts.SUBTITLE)
        launch_label.setStyleSheet("color: #e0e0e0; margin-top: 30px; margin-bottom: 15px;")
        main_layout.addWidget(launch_label)
        
        # Grid layout for launcher buttons
        launcher_grid = QGridLayout()
        launcher_grid.setSpacing(15)
        
        # Create 8 launcher buttons (2 rows of 4)
        self.launcher_buttons = []
        for i in range(8):
            config = self.launcher_configs.get(str(i), {})
            launcher_btn = LauncherButton(config, self)
            launcher_btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            launcher_btn.customContextMenuRequested.connect(lambda pos, btn=launcher_btn: self.show_launcher_menu(btn))
            self.launcher_buttons.append(launcher_btn)
            launcher_grid.addWidget(launcher_btn, i // 4, i % 4)
        
        # Center the launcher grid
        launcher_container = QWidget()
        launcher_container.setLayout(launcher_grid)
        launcher_container.setMaximumWidth(550)
        
        h_layout3 = QHBoxLayout()
        h_layout3.addStretch()
        h_layout3.addWidget(launcher_container)
        h_layout3.addStretch()
        main_layout.addLayout(h_layout3)
        
        main_layout.addStretch()
        central_widget.setLayout(main_layout)
        
        # Connect logging buttons
        self.buttons["Emails"].clicked.connect(self.open_email_panel)
        self.buttons["Phone"].clicked.connect(self.open_phone_panel)
        self.buttons["Radio"].clicked.connect(self.open_radio_panel)
        self.buttons["Everbridge"].clicked.connect(self.open_everbridge_panel)
        self.buttons["Facilities"].clicked.connect(self.open_facilities_ticket)
        
        # Connect management buttons
        self.manage_buttons["event_manager"].clicked.connect(self.open_event_manager)
        self.manage_buttons["stats"].clicked.connect(self.open_stats_panel)
        self.manage_buttons["logs"].clicked.connect(self.open_logs_panel)
        self.manage_buttons["training"].clicked.connect(self.open_training_panel)

    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # F-key shortcuts
        QShortcut(QKeySequence("F1"), self, self.open_email_panel)
        QShortcut(QKeySequence("F2"), self, self.open_phone_panel)
        QShortcut(QKeySequence("F3"), self, self.open_radio_panel)
        QShortcut(QKeySequence("F4"), self, self.open_everbridge_panel)
        QShortcut(QKeySequence("F5"), self, self.open_event_manager)
        QShortcut(QKeySequence("F6"), self, self.open_stats_panel)
        QShortcut(QKeySequence("Shift+F1"), self, self.open_facilities_ticket)
        QShortcut(QKeySequence("F7"), self, self.open_logs_panel)
        QShortcut(QKeySequence("F8"), self, self.open_training_panel)
        
        # Additional shortcuts
        QShortcut(QKeySequence("Ctrl+Q"), self, self.close)
        QShortcut(QKeySequence("F11"), self, self.toggle_fullscreen)
        QShortcut(QKeySequence("Ctrl+H"), self, self.show_help)

    def setup_menu(self):
        """Setup menu bar"""
        menubar = self.menuBar()
        from ui.styles import Fonts
        menubar.setFont(Fonts.NORMAL)
        
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
        <tr><td><b>F7</b></td><td>Open Logs Viewer</td></tr>
        <tr><td><b>F8</b></td><td>Open Training</td></tr>
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
    
    def open_facilities_ticket(self):
        from ui.facilities_ticket_ui import FacilitiesTicketDialog
        dialog = FacilitiesTicketDialog(parent=self)
        dialog.exec()

    def open_event_manager(self):
        self.event_manager_window = EventManager()
        self.event_manager_window.show()

    def open_stats_panel(self):
        self.stats_window = StatsPanel()
        self.stats_window.show()
    
    def open_logs_panel(self):
        from ui.logs_viewer_ui import LogsViewerPanel
        self.logs_window = LogsViewerPanel()
        self.logs_window.show()
    
    def open_training_panel(self):
        from ui.training_ui import TrainingPanel
        self.training_window = TrainingPanel()
        self.training_window.show()
    
    def show_settings(self):
        """Show settings dialog"""
        from ui.settings_dialog import SettingsDialog
        dialog = SettingsDialog(self)
        dialog.exec()
    
    def show_launcher_menu(self, button):
        """Show context menu for launcher button"""
        menu = QMenu(self)
        
        # Configure action
        configure_action = QAction("Configure", self)
        configure_action.triggered.connect(button.edit_config)
        menu.addAction(configure_action)
        
        # Clear action
        if button.config.get('name'):
            clear_action = QAction("Clear", self)
            clear_action.triggered.connect(lambda: self.clear_launcher(button))
            menu.addAction(clear_action)
        
        menu.exec(button.mapToGlobal(button.rect().center()))
    
    def clear_launcher(self, button):
        """Clear a launcher button configuration"""
        button.set_config({})
        self.save_launcher_configs()
    
    def load_launcher_configs(self):
        """Load launcher configurations from file"""
        try:
            with open('launcher_configs.json', 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def save_launcher_configs(self):
        """Save launcher configurations to file"""
        configs = {}
        for i, btn in enumerate(self.launcher_buttons):
            if btn.config:
                configs[str(i)] = btn.config
        
        with open('launcher_configs.json', 'w') as f:
            json.dump(configs, f, indent=2)
    
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