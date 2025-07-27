from PyQt6.QtWidgets import (
    QWidget,     # ← add this
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QSlider, QCheckBox, QGroupBox,
    QComboBox, QLineEdit, QDialogButtonBox,
    QMessageBox, QApplication, QTabWidget,
    QListWidget, QTextEdit, QListWidgetItem
)

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from app_settings import app_settings
import json

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

class DropdownCustomizationWidget(QWidget):
    """Widget for customizing dropdown options"""
    def __init__(self, title, key, items, parent=None):
        super().__init__(parent)
        self.key = key
        self.title = title
        self.Fonts = get_styles()
        
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel(title)
        title_label.setFont(self.Fonts.LABEL)
        layout.addWidget(title_label)
        
        # List widget for items
        self.list_widget = QListWidget()
        self.list_widget.setFont(self.Fonts.NORMAL)
        self.list_widget.addItems(items)
        self.list_widget.setMaximumHeight(200)
        layout.addWidget(self.list_widget)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        # Add item input
        self.new_item_input = QLineEdit()
        self.new_item_input.setPlaceholderText("Add new item...")
        self.new_item_input.setFont(self.Fonts.NORMAL)
        controls_layout.addWidget(self.new_item_input)
        
        # Add button
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self.add_item)
        controls_layout.addWidget(add_btn)
        
        # Remove button
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self.remove_item)
        controls_layout.addWidget(remove_btn)
        
        # Move up/down buttons
        up_btn = QPushButton("↑")
        up_btn.clicked.connect(self.move_up)
        controls_layout.addWidget(up_btn)
        
        down_btn = QPushButton("↓")
        down_btn.clicked.connect(self.move_down)
        controls_layout.addWidget(down_btn)
        
        layout.addLayout(controls_layout)
        self.setLayout(layout)
    
    def add_item(self):
        text = self.new_item_input.text().strip()
        if text:
            self.list_widget.addItem(text)
            self.new_item_input.clear()
    
    def remove_item(self):
        current_row = self.list_widget.currentRow()
        if current_row >= 0:
            self.list_widget.takeItem(current_row)
    
    def move_up(self):
        current_row = self.list_widget.currentRow()
        if current_row > 0:
            item = self.list_widget.takeItem(current_row)
            self.list_widget.insertItem(current_row - 1, item)
            self.list_widget.setCurrentRow(current_row - 1)
    
    def move_down(self):
        current_row = self.list_widget.currentRow()
        if current_row < self.list_widget.count() - 1:
            item = self.list_widget.takeItem(current_row)
            self.list_widget.insertItem(current_row + 1, item)
            self.list_widget.setCurrentRow(current_row + 1)
    
    def get_items(self):
        return [self.list_widget.item(i).text() for i in range(self.list_widget.count())]

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.setMinimumSize(800, 600)
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
        
        # Create tabs
        self.tabs = QTabWidget()
        self.tabs.setFont(self.Fonts.NORMAL)
        
        # General tab
        self.general_tab = QWidget()
        self.setup_general_tab()
        self.tabs.addTab(self.general_tab, "General")
        
        # Theme tab
        self.theme_tab = QWidget()
        self.setup_theme_tab()
        self.tabs.addTab(self.theme_tab, "Theme")
        
        # Dropdown Options tab
        self.dropdown_tab = QWidget()
        self.setup_dropdown_tab()
        self.tabs.addTab(self.dropdown_tab, "Dropdown Options")
        
        layout.addWidget(self.tabs)
        
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
    
    def setup_general_tab(self):
        """Setup the general settings tab"""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Display Settings
        display_group = QGroupBox("Display Settings")
        display_group.setFont(self.Fonts.LABEL)
        display_layout = QVBoxLayout()
        
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
        
        layout.addStretch()
        self.general_tab.setLayout(layout)
    
    def setup_theme_tab(self):
        """Setup the theme customization tab"""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Theme selector
        theme_group = QGroupBox("Theme Selection")
        theme_group.setFont(self.Fonts.LABEL)
        theme_layout = QVBoxLayout()
        
        theme_select_layout = QHBoxLayout()
        theme_select_layout.addWidget(QLabel("Current Theme:"))
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        self.theme_combo.setFont(self.Fonts.NORMAL)
        self.theme_combo.currentTextChanged.connect(self.preview_theme)
        theme_select_layout.addWidget(self.theme_combo)
        theme_select_layout.addStretch()
        
        theme_layout.addLayout(theme_select_layout)
        
        # Preview button
        preview_btn = QPushButton("🎨 Preview Theme")
        preview_btn.clicked.connect(self.preview_theme)
        theme_layout.addWidget(preview_btn)
        
        # Apply button
        apply_btn = QPushButton("✅ Apply Theme Now")
        apply_btn.clicked.connect(self.apply_theme_immediately)
        theme_layout.addWidget(apply_btn)
        
        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)
        
        # Theme preview area
        preview_group = QGroupBox("Theme Preview")
        preview_group.setFont(self.Fonts.LABEL)
        preview_layout = QVBoxLayout()
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(150)
        self.preview_text.setPlainText(
            "This is a preview of the selected theme.\n\n"
            "The theme will be applied to all windows and dialogs.\n"
            "Dark theme is recommended for low-light environments.\n"
            "Light theme is better for bright environments."
        )
        preview_layout.addWidget(self.preview_text)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        layout.addStretch()
        self.theme_tab.setLayout(layout)
    
    def setup_dropdown_tab(self):
        """Setup the dropdown customization tab"""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Info
        info = QLabel("Customize dropdown options for different log types")
        info.setFont(self.Fonts.NORMAL)
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)
        
        # Load current dropdown values
        dropdown_settings = app_settings.get("dropdown_options", {})
        
        # Site codes
        from config import SITE_CODES
        current_sites = dropdown_settings.get("site_codes", SITE_CODES)
        self.site_codes_widget = DropdownCustomizationWidget(
            "Site Codes", "site_codes", current_sites
        )
        layout.addWidget(self.site_codes_widget)
        
        # Radio units
        from ui.radio_ui import UNITS
        current_units = dropdown_settings.get("radio_units", list(UNITS.keys()))
        self.radio_units_widget = DropdownCustomizationWidget(
            "Radio Units", "radio_units", current_units
        )
        layout.addWidget(self.radio_units_widget)
        
        # Radio reasons
        from ui.radio_ui import REASONS
        current_reasons = dropdown_settings.get("radio_reasons", REASONS)
        self.radio_reasons_widget = DropdownCustomizationWidget(
            "Radio Dispatch Reasons", "radio_reasons", current_reasons
        )
        layout.addWidget(self.radio_reasons_widget)
        
        # Phone call types
        from ui.phone_ui import CALL_TYPES
        current_call_types = dropdown_settings.get("phone_call_types", CALL_TYPES)
        self.call_types_widget = DropdownCustomizationWidget(
            "Phone Call Types", "phone_call_types", current_call_types
        )
        layout.addWidget(self.call_types_widget)
        
        layout.addStretch()
        self.dropdown_tab.setLayout(layout)
    
    def update_scale_label(self, value):
        self.scale_label.setText(f"{value}%")
    
    def preview_theme(self):
        """Preview the selected theme"""
        theme = self.theme_combo.currentText().lower()
        # Update preview text styling based on theme
        if theme == "dark":
            self.preview_text.setStyleSheet("""
                QTextEdit {
                    background-color: #2d2d30;
                    color: #ffffff;
                    border: 1px solid #3e3e42;
                }
            """)
        else:
            self.preview_text.setStyleSheet("""
                QTextEdit {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #d0d0d0;
                }
            """)
    
    def apply_theme_immediately(self):
        """Apply theme without saving settings"""
        theme = self.theme_combo.currentText().lower()
        from ui.themes import get_theme_stylesheet
        app = QApplication.instance()
        app.setStyleSheet(get_theme_stylesheet(theme))
        QMessageBox.information(self, "Theme Applied", f"{theme.capitalize()} theme has been applied!")
    
    def load_current_settings(self):
        """Load current settings into UI"""
        # General settings
        scale = int(app_settings.get_display_scale() * 100)
        self.scale_slider.setValue(scale)
        
        self.fullscreen_check.setChecked(app_settings.get("start_fullscreen", True))
        self.shortcuts_check.setChecked(app_settings.get("show_shortcuts", True))
        self.timestamp_check.setChecked(app_settings.get("auto_timestamp", True))
        self.confirm_exit_check.setChecked(app_settings.get("confirm_exit", True))
        self.default_site_edit.setText(app_settings.get("default_site", ""))
        
        # Theme settings
        theme = app_settings.get("theme", "dark")
        self.theme_combo.setCurrentText(theme.capitalize())
        self.preview_theme()
    
    def save_settings(self):
        """Save all settings"""
        # General settings
        old_scale = app_settings.get_display_scale()
        new_scale = self.scale_slider.value() / 100.0
        
        old_theme = app_settings.get("theme", "dark")
        new_theme = self.theme_combo.currentText().lower()
        
        app_settings.set_display_scale(new_scale)
        app_settings.set("theme", new_theme)
        app_settings.set("start_fullscreen", self.fullscreen_check.isChecked())
        app_settings.set("show_shortcuts", self.shortcuts_check.isChecked())
        app_settings.set("auto_timestamp", self.timestamp_check.isChecked())
        app_settings.set("confirm_exit", self.confirm_exit_check.isChecked())
        app_settings.set("default_site", self.default_site_edit.text())
        
        # Save dropdown options
        dropdown_options = {
            "site_codes": self.site_codes_widget.get_items(),
            "radio_units": self.radio_units_widget.get_items(),
            "radio_reasons": self.radio_reasons_widget.get_items(),
            "phone_call_types": self.call_types_widget.get_items()
        }
        app_settings.set("dropdown_options", dropdown_options)
        
        # Apply theme if changed
        if old_theme != new_theme:
            from ui.themes import get_theme_stylesheet
            app = QApplication.instance()
            app.setStyleSheet(get_theme_stylesheet(new_theme))
        
        # Show restart message if scale changed
        if old_scale != new_scale:
            QMessageBox.information(
                self,
                "Restart Required",
                "Display scale has been changed. Please restart the application for the changes to take effect."
            )
        
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
            # General tab
            self.scale_slider.setValue(100)
            self.theme_combo.setCurrentText("Dark")
            self.fullscreen_check.setChecked(True)
            self.shortcuts_check.setChecked(True)
            self.timestamp_check.setChecked(True)
            self.confirm_exit_check.setChecked(True)
            self.default_site_edit.clear()
            
            # Reset dropdown options to defaults
            from config import SITE_CODES
            from ui.radio_ui import UNITS, REASONS
            from ui.phone_ui import CALL_TYPES
            
            # Clear and repopulate lists
            self.site_codes_widget.list_widget.clear()
            self.site_codes_widget.list_widget.addItems(SITE_CODES)
            
            self.radio_units_widget.list_widget.clear()
            self.radio_units_widget.list_widget.addItems(list(UNITS.keys()))
            
            self.radio_reasons_widget.list_widget.clear()
            self.radio_reasons_widget.list_widget.addItems(REASONS)
            
            self.call_types_widget.list_widget.clear()
            self.call_types_widget.list_widget.addItems(CALL_TYPES)