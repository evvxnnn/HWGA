from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QLineEdit,
    QPushButton, QHBoxLayout, QCheckBox, QMessageBox
)
from PyQt6.QtCore import Qt
from datetime import datetime
from database import insert_radio_log

UNITS = {
    "Unit A": ["Front Gate", "Rear Lot", "Loading Dock"],
    "Unit B": ["Warehouse", "East Fence", "Break Area"],
    "Unit C": ["Main Lobby", "Parking Garage", "Server Room"]
}

REASONS = ["Routine Patrol", "Suspicious Activity", "Access Check", "Escort", "Alarm Response"]

class RadioPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Radio Dispatch Log")
        self.setMinimumSize(600, 300)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Timestamp
        self.timestamp_field = QLineEdit(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.timestamp_field.setReadOnly(False)
        self.timestamp_field.setPlaceholderText("Timestamp")
        layout.addWidget(self.timestamp_field)

        # Unit dropdown
        self.unit_dropdown = QComboBox()
        self.unit_dropdown.addItems(UNITS.keys())
        self.unit_dropdown.currentIndexChanged.connect(self.update_locations)
        layout.addWidget(QLabel("Unit"))
        layout.addWidget(self.unit_dropdown)

        # Location dropdown
        self.location_dropdown = QComboBox()
        layout.addWidget(QLabel("Location"))
        layout.addWidget(self.location_dropdown)
        self.update_locations()

        # Reason dropdown
        self.reason_dropdown = QComboBox()
        self.reason_dropdown.addItems(REASONS)
        layout.addWidget(QLabel("Reason"))
        layout.addWidget(self.reason_dropdown)

        # Arrived / Departed checkboxes
        self.arrived_checkbox = QCheckBox("Arrived")
        self.departed_checkbox = QCheckBox("Departed")
        checkbox_layout = QHBoxLayout()
        checkbox_layout.addWidget(self.arrived_checkbox)
        checkbox_layout.addWidget(self.departed_checkbox)
        layout.addLayout(checkbox_layout)

        # Save button
        self.save_btn = QPushButton("Save Dispatch Log")
        self.save_btn.clicked.connect(self.save_log)
        layout.addWidget(self.save_btn)

        self.setLayout(layout)

    def update_locations(self):
        unit = self.unit_dropdown.currentText()
        self.location_dropdown.clear()
        self.location_dropdown.addItems(UNITS.get(unit, []))

    def save_log(self):
        unit = self.unit_dropdown.currentText()
        location = self.location_dropdown.currentText()
        reason = self.reason_dropdown.currentText()
        arrived = self.arrived_checkbox.isChecked()
        departed = self.departed_checkbox.isChecked()
        timestamp = self.timestamp_field.text()

        insert_radio_log(unit, location, reason, arrived, departed, timestamp)

        QMessageBox.information(self, "Saved", "Radio dispatch log saved successfully.")
        self.close()
