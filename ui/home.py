from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from ui.email_ui import EmailPanel
from ui.phone_ui import PhonePanel
from ui.radio_ui import RadioPanel
from ui.everbridge_ui import EverbridgePanel
from ui.event_manager_ui import EventManager
from ui.stats_ui import StatsPanel

class HomeWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Security Ops Logger")
        self.setMinimumSize(400, 450)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Security Operations Logger")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title)

        # Logging section
        log_label = QLabel("Log New Activity:")
        log_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        log_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(log_label)

        self.buttons = {
            "Emails": QPushButton("📧 Emails"),
            "Phone": QPushButton("📞 Phone Calls"),
            "Radio": QPushButton("📻 Radio Dispatch"),
            "Everbridge": QPushButton("⚠️ Everbridge Alerts")
        }

        for btn in self.buttons.values():
            btn.setFixedHeight(50)
            layout.addWidget(btn)

        # Management section
        manage_label = QLabel("Manage & Analyze:")
        manage_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        manage_label.setStyleSheet("font-weight: bold; margin-top: 20px;")
        layout.addWidget(manage_label)

        self.event_manager_btn = QPushButton("🔗 Event Manager")
        self.event_manager_btn.setFixedHeight(50)
        self.event_manager_btn.setStyleSheet("background-color: #2196F3; color: white;")
        layout.addWidget(self.event_manager_btn)

        self.stats_btn = QPushButton("📊 Statistics & Reports")
        self.stats_btn.setFixedHeight(50)
        self.stats_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        layout.addWidget(self.stats_btn)

        self.setLayout(layout)

        # Connect buttons
        self.buttons["Emails"].clicked.connect(self.open_email_panel)
        self.buttons["Phone"].clicked.connect(self.open_phone_panel)
        self.buttons["Radio"].clicked.connect(self.open_radio_panel)
        self.buttons["Everbridge"].clicked.connect(self.open_everbridge_panel)
        self.event_manager_btn.clicked.connect(self.open_event_manager)
        self.stats_btn.clicked.connect(self.open_stats_panel)

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