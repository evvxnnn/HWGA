from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from ui.email_ui import EmailPanel
from ui.phone_ui import PhonePanel
from ui.radio_ui import RadioPanel
from ui.everbridge_ui import EverbridgePanel

class HomeWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Security Ops Logger")
        self.setMinimumSize(400, 300)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Select Log Type")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self.buttons = {
            "Emails": QPushButton("📧 Emails"),
            "Phone": QPushButton("📞 Phone Calls"),
            "Radio": QPushButton("📻 Radio Dispatch"),
            "Everbridge": QPushButton("⚠️ Everbridge Alerts")
        }

        for btn in self.buttons.values():
            btn.setFixedHeight(50)
            layout.addWidget(btn)

        self.setLayout(layout)

        self.buttons["Emails"].clicked.connect(self.open_email_panel)
        self.buttons["Phone"].clicked.connect(self.open_phone_panel)
        self.buttons["Radio"].clicked.connect(self.open_radio_panel)
        self.buttons["Everbridge"].clicked.connect(self.open_everbridge_panel)

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
