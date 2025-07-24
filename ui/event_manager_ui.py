from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton,
    QHBoxLayout, QTextEdit, QLineEdit, QInputDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from logic.event_handler import (
    get_event_chains, get_event_chain_logs, get_log_summary,
    create_event_chain, load_all_logs, link_log_to_event
)

class EventManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Event Manager")
        self.setMinimumSize(900, 500)
        self.current_event_id = None
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()

        # Left Panel: Event List
        left_panel = QVBoxLayout()
        left_panel.addWidget(QLabel("Event Chains"))

        self.event_list = QListWidget()
        self.event_list.itemSelectionChanged.connect(self.load_event_timeline)
        left_panel.addWidget(self.event_list)

        self.create_btn = QPushButton("➕ Create New Event Chain")
        self.create_btn.clicked.connect(self.prompt_create_event)
        left_panel.addWidget(self.create_btn)

        # Right Panel: Timeline + Attach Logs
        right_panel = QVBoxLayout()

        self.timeline_label = QLabel("Event Timeline")
        right_panel.addWidget(self.timeline_label)

        self.timeline_box = QTextEdit()
        self.timeline_box.setReadOnly(True)
        right_panel.addWidget(self.timeline_box)

        self.available_logs_label = QLabel("Attach Additional Logs")
        right_panel.addWidget(self.available_logs_label)

        self.unlinked_log_list = QListWidget()
        self.unlinked_log_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        right_panel.addWidget(self.unlinked_log_list)

        self.attach_btn = QPushButton("Attach Selected Log to Event")
        self.attach_btn.clicked.connect(self.attach_selected_log)
        right_panel.addWidget(self.attach_btn)

        # Assemble
        layout.addLayout(left_panel, 3)
        layout.addLayout(right_panel, 7)
        self.setLayout(layout)

        self.refresh_events()

    def refresh_events(self):
        self.event_list.clear()
        chains = get_event_chains()
        for chain in chains:
            self.event_list.addItem(f"{chain['id']}: {chain['title']}")

    def load_event_timeline(self):
        selected_item = self.event_list.currentItem()
        if not selected_item:
            return

        event_id = int(selected_item.text().split(":")[0])
        self.current_event_id = event_id
        logs = get_event_chain_logs(event_id)

        self.timeline_box.clear()
        for entry in logs:
            table, source_id, timestamp = entry
            summary = get_log_summary(table, source_id)
            self.timeline_box.append(f"[{timestamp}] [{table}] #{source_id} — {summary}")

        self.refresh_unlinked_logs()

    def refresh_unlinked_logs(self):
        self.unlinked_log_list.clear()
        all_logs = load_all_logs()
        # Optional: Filter out logs already linked if needed
        for log in all_logs:
            summary = f"[{log['timestamp']}] {log['source']} #{log['id']} ({log['table']})"
            self.unlinked_log_list.addItem(summary)

    def attach_selected_log(self):
        selected = self.unlinked_log_list.currentItem()
        if not selected or not self.current_event_id:
            return

        text = selected.text()
        table_start = text.find("(") + 1
        table_end = text.find(")")
        table = text[table_start:table_end]
        log_id = int(text.split("#")[1].split()[0])
        timestamp = text.split("]")[0][1:]

        link_log_to_event(self.current_event_id, table, log_id, timestamp)
        QMessageBox.information(self, "Linked", "Log linked to event successfully.")
        self.load_event_timeline()

    def prompt_create_event(self):
        title, ok = QInputDialog.getText(self, "Create New Event", "Event title:")
        if ok and title.strip():
            create_event_chain(title.strip())
            self.refresh_events()

