from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QComboBox,
    QFileDialog, QMessageBox, QHeaderView, QTabWidget,
    QGroupBox, QTextEdit, QLineEdit, QListWidget, QListWidgetItem,
    QStackedWidget, QCheckBox, QProgressBar, QSplitter, QDialog,
    QDialogButtonBox, QSpinBox, QDateTimeEdit, QFrame
)
from PyQt6.QtCore import Qt, QDateTime, pyqtSignal, QUrl
from PyQt6.QtGui import QFont, QShortcut, QKeySequence
from ui.video_player import VideoPlayer
from ui.styles import Fonts, get_button_style, TABLE_STYLE, DROPDOWN_STYLE, LIST_STYLE
import json
import os
from datetime import datetime

class TrainingPanel(QMainWindow):
    def __init__(self, direct_training_id=None):
        super().__init__()
        self.setWindowTitle("Training Center")
        self.setMinimumSize(1200, 800)
        self.showMaximized()
        
        # Store direct training ID if provided (from help button)
        self.direct_training_id = direct_training_id
        
        # Temporary user role (will be replaced with actual auth later)
        # Roles: 'employee', 'trainer', 'manager'
        self.user_role = 'manager'  # For testing, set to manager
        self.user_name = os.environ.get('USERNAME', 'User')
        
        # Training data storage
        self.trainings = self.load_trainings()
        self.user_progress = self.load_user_progress()
        
        self.init_ui()
        self.setup_shortcuts()
        self.load_training_list()
        
        # If opened with specific training, display it
        if self.direct_training_id:
            self.open_specific_training(self.direct_training_id)
    
    def init_ui(self):
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header with title and user info
        header_layout = QHBoxLayout()
        
        title = QLabel("Security Operations Training Center")
        title.setFont(Fonts.TITLE)
        title.setStyleSheet("color: #e0e0e0;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # User info
        user_info = QLabel(f"Logged in as: {self.user_name} ({self.user_role.title()})")
        user_info.setStyleSheet("color: #808080;")
        header_layout.addWidget(user_info)
        
        layout.addLayout(header_layout)
        
        # Create main splitter
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Training list
        left_panel = self.create_left_panel()
        self.splitter.addWidget(left_panel)
        
        # Right panel - Content area
        right_panel = self.create_right_panel()
        self.splitter.addWidget(right_panel)
        
        # Set splitter sizes (30% left, 70% right)
        self.splitter.setSizes([400, 800])
        
        layout.addWidget(self.splitter)
        
        central_widget.setLayout(layout)
    
    def create_left_panel(self):
        """Create the left panel with training list and filters"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Filter section
        filter_group = QGroupBox("Filters")
        filter_group.setStyleSheet("""
            QGroupBox {
                color: #e0e0e0;
                border: 1px solid #333333;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                background-color: #0d0d0d;
            }
        """)
        
        filter_layout = QVBoxLayout()
        
        # Category filter
        self.category_combo = QComboBox()
        self.category_combo.addItems([
            "All Categories",
            "Application Help",  # Added for app-specific trainings
            "Security Procedures",
            "Software Training",
            "Emergency Response",
            "Equipment Usage",
            "Compliance",
            "General Help"
        ])
        self.category_combo.setStyleSheet(DROPDOWN_STYLE)
        self.category_combo.currentTextChanged.connect(self.filter_trainings)
        filter_layout.addWidget(QLabel("Category:"))
        filter_layout.addWidget(self.category_combo)
        
        # Status filter
        self.status_combo = QComboBox()
        self.status_combo.addItems([
            "All Status",
            "Not Started",
            "In Progress",
            "Completed",
            "Overdue"
        ])
        self.status_combo.setStyleSheet(DROPDOWN_STYLE)
        self.status_combo.currentTextChanged.connect(self.filter_trainings)
        filter_layout.addWidget(QLabel("Status:"))
        filter_layout.addWidget(self.status_combo)
        
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)
        
        # Training list
        list_label = QLabel("Available Trainings")
        list_label.setFont(Fonts.SUBTITLE)
        list_label.setStyleSheet("color: #e0e0e0; margin-top: 10px;")
        layout.addWidget(list_label)
        
        self.training_list = QListWidget()
        self.training_list.setStyleSheet(LIST_STYLE)
        self.training_list.itemClicked.connect(self.on_training_selected)
        layout.addWidget(self.training_list)
        
        # Action buttons for managers/trainers
        if self.user_role in ['manager', 'trainer']:
            button_layout = QHBoxLayout()
            
            self.new_training_btn = QPushButton("New Training")
            self.new_training_btn.setStyleSheet(get_button_style())
            self.new_training_btn.clicked.connect(self.create_new_training)
            button_layout.addWidget(self.new_training_btn)
            
            self.edit_training_btn = QPushButton("Edit")
            self.edit_training_btn.setStyleSheet(get_button_style())
            self.edit_training_btn.setEnabled(False)
            self.edit_training_btn.clicked.connect(self.edit_training)
            button_layout.addWidget(self.edit_training_btn)
            
            self.delete_training_btn = QPushButton("Delete")
            self.delete_training_btn.setStyleSheet(get_button_style())
            self.delete_training_btn.setEnabled(False)
            self.delete_training_btn.clicked.connect(self.delete_training)
            button_layout.addWidget(self.delete_training_btn)
            
            layout.addLayout(button_layout)
        
        widget.setLayout(layout)
        return widget
    
    def create_right_panel(self):
        """Create the right panel with training content"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Create stacked widget for different views
        self.content_stack = QStackedWidget()
        
        # Welcome view (shown when no training selected)
        welcome_widget = QWidget()
        welcome_layout = QVBoxLayout()
        welcome_label = QLabel("Select a training from the list to begin")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setStyleSheet("color: #808080; font-size: 14px;")
        welcome_layout.addWidget(welcome_label)
        welcome_widget.setLayout(welcome_layout)
        self.content_stack.addWidget(welcome_widget)
        
        # Training view
        self.training_view = self.create_training_view()
        self.content_stack.addWidget(self.training_view)
        
        # Statistics view (for managers)
        if self.user_role == 'manager':
            self.stats_view = self.create_stats_view()
            self.content_stack.addWidget(self.stats_view)
        
        layout.addWidget(self.content_stack)
        
        widget.setLayout(layout)
        return widget
    
    def create_training_view(self):
        """Create the training content view"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Training header
        self.training_title = QLabel("")
        self.training_title.setFont(Fonts.SUBTITLE)
        self.training_title.setStyleSheet("color: #e0e0e0;")
        layout.addWidget(self.training_title)
        
        # Training info
        self.training_info = QLabel("")
        self.training_info.setStyleSheet("color: #808080;")
        layout.addWidget(self.training_info)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #1a1a1a;
                border: 1px solid #333333;
                border-radius: 4px;
                text-align: center;
                color: #e0e0e0;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #4a4a4a;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Content tabs
        self.content_tabs = QTabWidget()
        self.content_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #333333;
                background-color: #0d0d0d;
            }
            QTabBar::tab {
                padding: 8px 16px;
                background-color: #1a1a1a;
                color: #808080;
                border: 1px solid #262626;
            }
            QTabBar::tab:selected {
                background-color: #0d0d0d;
                color: #e0e0e0;
                border-bottom: 2px solid #5a5a5a;
            }
        """)
        
        # Overview tab with video support
        overview_tab = QWidget()
        overview_layout = QVBoxLayout()
        
        # Video player section
        self.video_frame = QFrame()
        self.video_frame.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border: 1px solid #333333;
                border-radius: 4px;
                min-height: 400px;
            }
        """)
        video_layout = QVBoxLayout()
        
        self.video_label = QLabel("Video Tutorial")
        self.video_label.setFont(Fonts.LABEL)
        self.video_label.setStyleSheet("color: #e0e0e0; padding: 5px;")
        video_layout.addWidget(self.video_label)
        
        # Video player widget
        self.video_player = VideoPlayer()
        self.video_player.setMinimumHeight(350)
        video_layout.addWidget(self.video_player)
        
        # Video controls
        video_controls = QHBoxLayout()
        self.play_video_btn = QPushButton("Play Video")
        self.play_video_btn.setStyleSheet(get_button_style())
        self.play_video_btn.clicked.connect(self.play_video)
        video_controls.addWidget(self.play_video_btn)
        
        self.no_video_label = QLabel("No video available for this training")
        self.no_video_label.setStyleSheet("color: #808080; padding: 10px;")
        video_controls.addWidget(self.no_video_label)
        video_controls.addStretch()
        
        video_layout.addLayout(video_controls)
        self.video_frame.setLayout(video_layout)
        overview_layout.addWidget(self.video_frame)
        
        # Text content section
        self.overview_text = QTextEdit()
        self.overview_text.setReadOnly(True)
        self.overview_text.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a;
                color: #e0e0e0;
                border: 1px solid #333333;
                border-radius: 4px;
                padding: 10px;
            }
        """)
        overview_layout.addWidget(self.overview_text)
        overview_tab.setLayout(overview_layout)
        self.content_tabs.addTab(overview_tab, "Overview")
        
        # Materials tab
        materials_tab = QWidget()
        materials_layout = QVBoxLayout()
        self.materials_list = QListWidget()
        self.materials_list.setStyleSheet(LIST_STYLE)
        materials_layout.addWidget(QLabel("Training Materials:"))
        materials_layout.addWidget(self.materials_list)
        
        self.download_btn = QPushButton("Download Selected")
        self.download_btn.setStyleSheet(get_button_style())
        self.download_btn.clicked.connect(self.download_material)
        materials_layout.addWidget(self.download_btn)
        
        materials_tab.setLayout(materials_layout)
        self.content_tabs.addTab(materials_tab, "Materials")
        
        # Quiz tab (if applicable)
        quiz_tab = QWidget()
        quiz_layout = QVBoxLayout()
        self.quiz_area = QTextEdit()
        self.quiz_area.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a;
                color: #e0e0e0;
                border: 1px solid #333333;
                border-radius: 4px;
                padding: 10px;
            }
        """)
        quiz_layout.addWidget(self.quiz_area)
        
        self.submit_quiz_btn = QPushButton("Submit Quiz")
        self.submit_quiz_btn.setStyleSheet(get_button_style())
        self.submit_quiz_btn.clicked.connect(self.submit_quiz)
        quiz_layout.addWidget(self.submit_quiz_btn)
        
        quiz_tab.setLayout(quiz_layout)
        self.content_tabs.addTab(quiz_tab, "Quiz")
        
        # Completion tab
        completion_tab = QWidget()
        completion_layout = QVBoxLayout()
        
        self.completion_status = QLabel("")
        self.completion_status.setStyleSheet("color: #e0e0e0; font-size: 14px; padding: 20px;")
        completion_layout.addWidget(self.completion_status)
        
        self.mark_complete_btn = QPushButton("Mark as Complete")
        self.mark_complete_btn.setStyleSheet(get_button_style())
        self.mark_complete_btn.clicked.connect(self.mark_training_complete)
        completion_layout.addWidget(self.mark_complete_btn)
        
        completion_layout.addStretch()
        completion_tab.setLayout(completion_layout)
        self.content_tabs.addTab(completion_tab, "Completion")
        
        layout.addWidget(self.content_tabs)
        
        widget.setLayout(layout)
        return widget
    
    def create_stats_view(self):
        """Create statistics view for managers"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel("Training Statistics")
        title.setFont(Fonts.SUBTITLE)
        title.setStyleSheet("color: #e0e0e0;")
        layout.addWidget(title)
        
        # Stats table
        self.stats_table = QTableWidget()
        self.stats_table.setStyleSheet(TABLE_STYLE)
        self.stats_table.setColumnCount(5)
        self.stats_table.setHorizontalHeaderLabels([
            "Training", "Total Users", "Completed", "In Progress", "Completion Rate"
        ])
        layout.addWidget(self.stats_table)
        
        # Export button
        self.export_stats_btn = QPushButton("Export Statistics")
        self.export_stats_btn.setStyleSheet(get_button_style())
        self.export_stats_btn.clicked.connect(self.export_statistics)
        layout.addWidget(self.export_stats_btn)
        
        widget.setLayout(layout)
        return widget
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        QShortcut(QKeySequence("Ctrl+N"), self, self.create_new_training if self.user_role in ['manager', 'trainer'] else lambda: None)
        QShortcut(QKeySequence("Ctrl+R"), self, self.load_training_list)
        QShortcut(QKeySequence("Escape"), self, self.close)
    
    def load_trainings(self):
        """Load training data from file"""
        from ui.help_utils import DEFAULT_TRAININGS
        
        trainings_file = "data/trainings.json"
        if os.path.exists(trainings_file):
            with open(trainings_file, 'r') as f:
                trainings = json.load(f)
                # Add default app trainings if not present
                existing_ids = [t['id'] for t in trainings.get('trainings', [])]
                for key, training in DEFAULT_TRAININGS.items():
                    if training['id'] not in existing_ids:
                        trainings['trainings'].append(training)
                return trainings
        else:
            # Start with default app training data
            app_trainings = list(DEFAULT_TRAININGS.values())
            
            # Add general training data
            general_trainings = [
                {
                    "id": "001",
                    "title": "Security Operations Overview",
                    "category": "Security Procedures",
                    "description": "Introduction to security operations procedures and protocols",
                    "duration": "2 hours",
                    "created_by": "Admin",
                    "created_date": "2024-01-01",
                    "video_url": "",
                    "materials": ["SOC_Manual.pdf", "Quick_Reference.docx"],
                    "quiz_required": True
                },
                {
                    "id": "002",
                    "title": "Emergency Response Procedures",
                    "category": "Emergency Response",
                    "description": "How to respond to various emergency situations",
                    "duration": "1.5 hours",
                    "created_by": "Admin",
                    "created_date": "2024-01-01",
                    "video_url": "",
                    "materials": ["Emergency_Guide.pdf"],
                    "quiz_required": True
                }
            ]
            
            return {"trainings": app_trainings + general_trainings}
    
    def load_user_progress(self):
        """Load user progress data"""
        progress_file = f"data/user_progress_{self.user_name}.json"
        if os.path.exists(progress_file):
            with open(progress_file, 'r') as f:
                return json.load(f)
        else:
            return {}
    
    def save_trainings(self):
        """Save training data to file"""
        os.makedirs("data", exist_ok=True)
        with open("data/trainings.json", 'w') as f:
            json.dump(self.trainings, f, indent=2)
    
    def save_user_progress(self):
        """Save user progress data"""
        os.makedirs("data", exist_ok=True)
        with open(f"data/user_progress_{self.user_name}.json", 'w') as f:
            json.dump(self.user_progress, f, indent=2)
    
    def load_training_list(self):
        """Load trainings into the list widget"""
        self.training_list.clear()
        
        for training in self.trainings.get("trainings", []):
            # Create list item
            item_text = f"{training['title']}\n{training['category']} - {training['duration']}"
            item = QListWidgetItem(item_text)
            
            # Check completion status
            progress = self.user_progress.get(training['id'], {})
            if progress.get('completed'):
                item.setBackground(Qt.GlobalColor.darkGreen)
            elif progress.get('started'):
                item.setBackground(Qt.GlobalColor.darkYellow)
            
            item.setData(Qt.ItemDataRole.UserRole, training)
            self.training_list.addItem(item)
    
    def filter_trainings(self):
        """Filter training list based on selected criteria"""
        category_filter = self.category_combo.currentText()
        status_filter = self.status_combo.currentText()
        
        for i in range(self.training_list.count()):
            item = self.training_list.item(i)
            training = item.data(Qt.ItemDataRole.UserRole)
            
            show = True
            
            # Apply category filter
            if category_filter != "All Categories":
                if training['category'] != category_filter:
                    show = False
            
            # Apply status filter
            if status_filter != "All Status":
                progress = self.user_progress.get(training['id'], {})
                if status_filter == "Completed" and not progress.get('completed'):
                    show = False
                elif status_filter == "In Progress" and not progress.get('started'):
                    show = False
                elif status_filter == "Not Started" and progress.get('started'):
                    show = False
            
            item.setHidden(not show)
    
    def on_training_selected(self, item):
        """Handle training selection"""
        training = item.data(Qt.ItemDataRole.UserRole)
        self.current_training = training
        
        # Enable edit/delete buttons for managers
        if self.user_role in ['manager', 'trainer']:
            self.edit_training_btn.setEnabled(True)
            self.delete_training_btn.setEnabled(True)
        
        # Display training content
        self.display_training(training)
        self.content_stack.setCurrentIndex(1)  # Show training view
    
    def display_training(self, training):
        """Display selected training content"""
        self.training_title.setText(training.get('title', 'Untitled'))
        
        # Build info string with available fields
        info_parts = []
        if 'category' in training:
            info_parts.append(f"Category: {training['category']}")
        if 'duration' in training:
            info_parts.append(f"Duration: {training['duration']}")
        if 'created_by' in training:
            info_parts.append(f"Created by: {training['created_by']}")
        if 'created_date' in training:
            info_parts.append(f"Date: {training['created_date']}")
        
        self.training_info.setText(" | ".join(info_parts) if info_parts else "No additional information")
        
        # Set overview text (supports HTML)
        description = training.get('description', 'No description available')
        # Check if it's HTML or plain text
        if '<' in description and '>' in description:
            self.overview_text.setHtml(description)
        else:
            self.overview_text.setPlainText(description)
        
        # Handle video
        video_url = training.get('video_url', '')
        if video_url:
            self.current_video_url = video_url
            self.play_video_btn.setEnabled(True)
            self.no_video_label.hide()
            # Auto-play if it's a YouTube or embedded video
            if 'youtube.com' in video_url or 'youtu.be' in video_url:
                self.play_video()
        else:
            self.current_video_url = None
            self.play_video_btn.setEnabled(False)
            self.no_video_label.show()
            self.video_player.clear_video()
        
        # Load materials
        self.materials_list.clear()
        for material in training.get('materials', []):
            self.materials_list.addItem(material)
        
        # Check progress
        progress = self.user_progress.get(training['id'], {})
        if progress.get('completed'):
            self.progress_bar.setValue(100)
            self.completion_status.setText("✓ Training Completed")
            self.mark_complete_btn.setEnabled(False)
        elif progress.get('started'):
            self.progress_bar.setValue(50)
            self.completion_status.setText("Training in progress...")
            self.mark_complete_btn.setEnabled(True)
        else:
            self.progress_bar.setValue(0)
            self.completion_status.setText("Training not started")
            self.mark_complete_btn.setEnabled(True)
            
            # Mark as started
            if training['id'] not in self.user_progress:
                self.user_progress[training['id']] = {'started': True, 'start_date': datetime.now().isoformat()}
                self.save_user_progress()
    
    def create_new_training(self):
        """Create a new training (managers/trainers only)"""
        dialog = TrainingDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_training = dialog.get_training_data()
            self.trainings['trainings'].append(new_training)
            self.save_trainings()
            self.load_training_list()
            QMessageBox.information(self, "Success", "Training created successfully")
    
    def edit_training(self):
        """Edit selected training"""
        if hasattr(self, 'current_training'):
            dialog = TrainingDialog(self, self.current_training)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                updated_training = dialog.get_training_data()
                # Update the training in the list
                for i, training in enumerate(self.trainings['trainings']):
                    if training['id'] == self.current_training['id']:
                        self.trainings['trainings'][i] = updated_training
                        break
                self.save_trainings()
                self.load_training_list()
                QMessageBox.information(self, "Success", "Training updated successfully")
    
    def delete_training(self):
        """Delete selected training"""
        if hasattr(self, 'current_training'):
            reply = QMessageBox.question(
                self, "Confirm Delete",
                f"Are you sure you want to delete '{self.current_training['title']}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.trainings['trainings'] = [
                    t for t in self.trainings['trainings']
                    if t['id'] != self.current_training['id']
                ]
                self.save_trainings()
                self.load_training_list()
                self.content_stack.setCurrentIndex(0)  # Show welcome view
                QMessageBox.information(self, "Success", "Training deleted successfully")
    
    def mark_training_complete(self):
        """Mark current training as complete"""
        if hasattr(self, 'current_training'):
            training_id = self.current_training['id']
            self.user_progress[training_id] = {
                'started': True,
                'completed': True,
                'completion_date': datetime.now().isoformat()
            }
            self.save_user_progress()
            self.display_training(self.current_training)
            self.load_training_list()
            QMessageBox.information(self, "Success", "Training marked as complete!")
    
    def download_material(self):
        """Download selected training material"""
        current_item = self.materials_list.currentItem()
        if current_item:
            material_name = current_item.text()
            QMessageBox.information(self, "Download", f"Downloading {material_name}...")
    
    def play_video(self):
        """Play the training video"""
        if self.current_video_url:
            self.video_player.load_video(self.current_video_url)
    
    def open_specific_training(self, training_id):
        """Open a specific training by ID"""
        # Find and display the training
        for training in self.trainings.get('trainings', []):
            if training['id'] == training_id:
                # Find the item in the list
                for i in range(self.training_list.count()):
                    item = self.training_list.item(i)
                    item_training = item.data(Qt.ItemDataRole.UserRole)
                    if item_training['id'] == training_id:
                        self.training_list.setCurrentItem(item)
                        self.on_training_selected(item)
                        # Switch to Application Help category
                        self.category_combo.setCurrentText("Application Help")
                        self.filter_trainings()
                        break
                break
    
    def submit_quiz(self):
        """Submit training quiz"""
        QMessageBox.information(self, "Quiz", "Quiz submission functionality will be implemented")
    
    def export_statistics(self):
        """Export training statistics"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Statistics", "", "Excel Files (*.xlsx);;CSV Files (*.csv)"
        )
        if file_path:
            QMessageBox.information(self, "Export", f"Statistics exported to {file_path}")


class TrainingDialog(QDialog):
    """Dialog for creating/editing training"""
    def __init__(self, parent=None, training=None):
        super().__init__(parent)
        self.training = training
        self.setWindowTitle("Edit Training" if training else "New Training")
        self.setMinimumSize(600, 500)
        self.init_ui()
        
        if training:
            self.load_training_data(training)
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        layout.addWidget(QLabel("Title:"))
        self.title_input = QLineEdit()
        self.title_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                background-color: #1a1a1a;
                color: #e0e0e0;
                border: 1px solid #333333;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.title_input)
        
        # Category
        layout.addWidget(QLabel("Category:"))
        self.category_combo = QComboBox()
        self.category_combo.addItems([
            "Security Procedures",
            "Software Training",
            "Emergency Response",
            "Equipment Usage",
            "Compliance",
            "General Help"
        ])
        self.category_combo.setStyleSheet(DROPDOWN_STYLE)
        layout.addWidget(self.category_combo)
        
        # Description
        layout.addWidget(QLabel("Description:"))
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)
        self.description_input.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a;
                color: #e0e0e0;
                border: 1px solid #333333;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        layout.addWidget(self.description_input)
        
        # Duration
        layout.addWidget(QLabel("Duration:"))
        self.duration_input = QLineEdit()
        self.duration_input.setPlaceholderText("e.g., 2 hours, 45 minutes")
        self.duration_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                background-color: #1a1a1a;
                color: #e0e0e0;
                border: 1px solid #333333;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.duration_input)
        
        # Video URL
        layout.addWidget(QLabel("Video URL (optional):"))
        video_layout = QHBoxLayout()
        self.video_url_input = QLineEdit()
        self.video_url_input.setPlaceholderText("YouTube URL or local video filename")
        self.video_url_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                background-color: #1a1a1a;
                color: #e0e0e0;
                border: 1px solid #333333;
                border-radius: 4px;
            }
        """)
        video_layout.addWidget(self.video_url_input)
        
        self.browse_video_btn = QPushButton("Browse")
        self.browse_video_btn.setStyleSheet(get_button_style())
        self.browse_video_btn.clicked.connect(self.browse_video)
        video_layout.addWidget(self.browse_video_btn)
        layout.addLayout(video_layout)
        
        # Quiz required
        self.quiz_checkbox = QCheckBox("Quiz Required")
        self.quiz_checkbox.setStyleSheet("color: #e0e0e0;")
        layout.addWidget(self.quiz_checkbox)
        
        # Button box
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_box.setStyleSheet(get_button_style())
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def load_training_data(self, training):
        """Load existing training data into form"""
        self.title_input.setText(training.get('title', ''))
        self.category_combo.setCurrentText(training.get('category', 'General Help'))
        self.description_input.setText(training.get('description', ''))
        self.duration_input.setText(training.get('duration', ''))
        self.video_url_input.setText(training.get('video_url', ''))
        self.quiz_checkbox.setChecked(training.get('quiz_required', False))
    
    def get_training_data(self):
        """Get training data from form"""
        return {
            'id': self.training.get('id', str(datetime.now().timestamp())) if self.training else str(datetime.now().timestamp()),
            'title': self.title_input.text(),
            'category': self.category_combo.currentText(),
            'description': self.description_input.toPlainText(),
            'duration': self.duration_input.text(),
            'video_url': self.video_url_input.text(),
            'created_by': os.environ.get('USERNAME', 'User'),
            'created_date': self.training.get('created_date', datetime.now().strftime('%Y-%m-%d')) if self.training else datetime.now().strftime('%Y-%m-%d'),
            'materials': self.training.get('materials', []) if self.training else [],
            'quiz_required': self.quiz_checkbox.isChecked()
        }
    
    def browse_video(self):
        """Browse for local video file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Video File",
            "",
            "Video Files (*.mp4 *.avi *.mov *.wmv *.webm);;All Files (*.*)"
        )
        if file_path:
            # Copy to training_videos folder
            import shutil
            os.makedirs('training_videos', exist_ok=True)
            filename = os.path.basename(file_path)
            dest_path = os.path.join('training_videos', filename)
            shutil.copy2(file_path, dest_path)
            self.video_url_input.setText(filename)