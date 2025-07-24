from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QTextEdit,
    QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt
from datetime import datetime
from database import insert_everbridge_log

class EverbridgePanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Everbridge Alert Log")
        self.setMinimumSize(500, 300)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Timestamp
        self.timestamp_field = QLineEdit(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.timestamp_field.setPlaceholderText("Timestamp")
        layout.addWidget(QLabel("Timestamp"))
        layout.addWidget(self.timestamp_field)

        # Site Code
        self.site_code_field = QLineEdit()
        self.site_code_field.setPlaceholderText("Site Code")
        layout.addWidget(QLabel("Site Code"))
        layout.addWidget(self.site_code_field)

        # Message
        self.message_box = QTextEdit()
        self.message_box.setPlaceholderText("Enter message that was sent")
        layout.addWidget(QLabel("Alert Message"))
        layout.addWidget(self.message_box)

        # Save button
        self.save_btn = QPushButton("Save Alert Log")
        self.save_btn.clicked.connect(self.save_log)
        layout.addWidget(self.save_btn)

        self.setLayout(layout)

    def save_log(self):
        site_code = self.site_code_field.text()
        message = self.message_box.toPlainText()
        timestamp = self.timestamp_field.text()

        insert_everbridge_log(site_code, message, timestamp)

        QMessageBox.information(self, "Saved", "Everbridge alert log saved successfully.")
        self.close()
