from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QSlider, QCheckBox, QGroupBox,
    QComboBox, QLineEdit, QDialogButtonBox,
    QMessageBox, QApplication
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from app_settings import app_settings

# Import styles only when needed to avoid circular imports
def get_styles():
    try:
        from ui.styles import Fonts
        return Fonts
    except ImportError:
        # Fallback if styles aren't available
        class FallbackFonts:
            TITLE = QFont("Arial", 20, QFont.Weight.Bold)
            LABEL = QFont("Arial", 14, QFont.Weight.Bold)
            NORMAL = QFont("Arial", 12)
        return FallbackFonts

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.setMinimumSize(600, 500)
        self.Fonts = get_styles()
        self.init_ui()
        self.load_current_settings()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Title
        title = QLabel("⚙️ Application Settings")
        title.setFont(self.Fonts.TITLE)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Display Settings
        display_group = QGroupBox("Display Settings")
        display_group.setFont(self.Fonts.LABEL)
        display_layout = QVBoxLayout()
        
        # Theme selector
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Theme:"))
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        self.theme_combo.setFont(self.Fonts.NORMAL)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        
        display_layout.addLayout(theme_layout)
        
        # Display Scale
        scale_layout = QHBoxLayout()
        scale_layout.addWidget(QLabel("Display Scale:"))
        
        self.scale_slider = QSlider(Qt.Orientation.Horizontal)
        self.scale_slider.setRange(75, 150)  # 75% to 150%
        self.scale_slider.setSingleStep(5)
        self.scale_slider.setPageStep(25)
        self.scale_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.scale_slider.setTickInterval(25)
        self.scale_slider.valueChanged.connect(self.update_scale_label)
        scale_layout.addWidget(self.scale_slider)
        
        self.scale_label = QLabel("100%")
        self.scale_label.setMinimumWidth(50)
        scale_layout.addWidget(self.scale_label)
        
        display_layout.addLayout(scale_layout)
        
        # Scale presets
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("Quick presets:"))
        
        for text, value in [("Small (75%)", 75), ("Normal (100%)", 100), ("Large (125%)", 125), ("Extra Large (150%)", 150)]:
            btn = QPushButton(text)
            btn.clicked.connect(lambda checked, v=value: self.scale_slider.setValue(v))
            preset_layout.addWidget(btn)
        
        display_layout.addLayout(preset_layout)
        
        # Fullscreen option
        self.fullscreen_check = QCheckBox("Start in fullscreen mode")
        self.fullscreen_check.setFont(self.Fonts.NORMAL)
        display_layout.addWidget(self.fullscreen_check)
        
        display_group.setLayout(display_layout)
        layout.addWidget(display_group)
        
        # Behavior Settings
        behavior_group = QGroupBox("Behavior Settings")
        behavior_group.setFont(self.Fonts.LABEL)
        behavior_layout = QVBoxLayout()
        
        self.shortcuts_check = QCheckBox("Show keyboard shortcuts in buttons")
        self.shortcuts_check.setFont(self.Fonts.NORMAL)
        behavior_layout.addWidget(self.shortcuts_check)
        
        self.timestamp_check = QCheckBox("Auto-fill timestamp with current time")
        self.timestamp_check.setFont(self.Fonts.NORMAL)
        behavior_layout.addWidget(self.timestamp_check)
        
        self.confirm_exit_check = QCheckBox("Confirm before exiting application")
        self.confirm_exit_check.setFont(self.Fonts.NORMAL)
        behavior_layout.addWidget(self.confirm_exit_check)
        
        behavior_group.setLayout(behavior_layout)
        layout.addWidget(behavior_group)
        
        # Default Values
        defaults_group = QGroupBox("Default Values")
        defaults_group.setFont(self.Fonts.LABEL)
        defaults_layout = QVBoxLayout()
        
        site_layout = QHBoxLayout()
        site_layout.addWidget(QLabel("Default Site Code:"))
        self.default_site_edit = QLineEdit()
        self.default_site_edit.setPlaceholderText("e.g., MAIN, DC1")
        self.default_site_edit.setFont(self.Fonts.NORMAL)
        site_layout.addWidget(self.default_site_edit)
        defaults_layout.addLayout(site_layout)
        
        defaults_group.setLayout(defaults_layout)
        layout.addWidget(defaults_group)
        
        # Note about display scaling
        note = QLabel("Note: Display scale changes will take effect after restarting the application.")
        note.setWordWrap(True)
        note.setStyleSheet("color: #666; font-style: italic; padding: 10px;")
        layout.addWidget(note)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.RestoreDefaults
        )
        buttons.accepted.connect(self.save_settings)
        buttons.rejected.connect(self.reject)
        
        restore_btn = buttons.button(QDialogButtonBox.StandardButton.RestoreDefaults)
        restore_btn.clicked.connect(self.restore_defaults)
        
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def update_scale_label(self, value):
        self.scale_label.setText(f"{value}%")
    
    def load_current_settings(self):
        """Load current settings into UI"""
        scale = int(app_settings.get_display_scale() * 100)
        self.scale_slider.setValue(scale)
        
        theme = app_settings.get("theme", "dark")
        self.theme_combo.setCurrentText(theme.capitalize())
        
        self.fullscreen_check.setChecked(app_settings.get("start_fullscreen", True))
        self.shortcuts_check.setChecked(app_settings.get("show_shortcuts", True))
        self.timestamp_check.setChecked(app_settings.get("auto_timestamp", True))
        self.confirm_exit_check.setChecked(app_settings.get("confirm_exit", True))
        self.default_site_edit.setText(app_settings.get("default_site", ""))
    
    def save_settings(self):
        """Save settings"""
        # Check if scale changed
        old_scale = app_settings.get_display_scale()
        new_scale = self.scale_slider.value() / 100.0
        
        # Check if theme changed
        old_theme = app_settings.get("theme", "dark")
        new_theme = self.theme_combo.currentText().lower()
        
        app_settings.set_display_scale(new_scale)
        app_settings.set("theme", new_theme)
        app_settings.set("start_fullscreen", self.fullscreen_check.isChecked())
        app_settings.set("show_shortcuts", self.shortcuts_check.isChecked())
        app_settings.set("auto_timestamp", self.timestamp_check.isChecked())
        app_settings.set("confirm_exit", self.confirm_exit_check.isChecked())
        app_settings.set("default_site", self.default_site_edit.text())
        
        if old_scale != new_scale:
            QMessageBox.information(
                self,
                "Restart Required",
                "Display scale has been changed. Please restart the application for the changes to take effect."
            )
        
        if old_theme != new_theme:
            # Apply theme immediately
            from ui.themes import get_theme_stylesheet
            app = QApplication.instance()
            app.setStyleSheet(get_theme_stylesheet(new_theme))
        
        self.accept()
    
    def restore_defaults(self):
        """Restore default settings"""
        reply = QMessageBox.question(
            self,
            "Restore Defaults",
            "This will reset all settings to their default values. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.scale_slider.setValue(100)
            self.theme_combo.setCurrentText("Dark")
            self.fullscreen_check.setChecked(True)
            self.shortcuts_check.setChecked(True)
            self.timestamp_check.setChecked(True)
            self.confirm_exit_check.setChecked(True)
            self.default_site_edit.clear()