# Application Settings for Security Ops Logger
# Handles display scaling and user preferences

import json
import os

from logger import get_logger

# Don't import Qt-related items at module level to avoid initialization issues
app_settings = None

# Module-level logger for settings persistence
logger = get_logger(__name__)

class AppSettings:
    """Manage application settings and preferences"""
    
    def __init__(self):
        # Use simple file-based settings instead of QSettings
        self.config_file = "user_preferences.json"
        self.load_settings()
    
    def load_settings(self):
        """Load settings from file or defaults"""
        defaults = {
            "display_scale": 1.0,
            "start_fullscreen": True,
            "show_shortcuts": True,
            "theme": "dark",  # Default to dark theme
            "auto_timestamp": True,
            "confirm_exit": True,
            "default_site": "",
            "window_positions": {},
            "dropdown_options": {}  # For customizable dropdowns
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                    defaults.update(saved)
            except Exception as exc:
                # Log but continue with defaults
                logger.warning(
                    "Failed to load user preferences from %s: %s", self.config_file, exc
                )
        
        self.preferences = defaults
    
    def save_settings(self):
        """Save current settings to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.preferences, f, indent=2)
        except Exception as exc:
            logger.warning("Failed to save user preferences to %s: %s", self.config_file, exc)
    
    def get(self, key, default=None):
        """Get a setting value"""
        return self.preferences.get(key, default)
    
    def set(self, key, value):
        """Set a setting value"""
        self.preferences[key] = value
        self.save_settings()
    
    def get_display_scale(self):
        """Get display scale factor"""
        return self.preferences.get("display_scale", 1.0)
    
    def set_display_scale(self, scale):
        """Set display scale factor"""
        self.set("display_scale", scale)

# Create global instance
app_settings = AppSettings()

def apply_display_scaling(app):
    """Apply display scaling to the application"""
    scale = app_settings.get_display_scale()
    
    if scale != 1.0:
        # Set environment variable for Qt scaling
        os.environ["QT_SCALE_FACTOR"] = str(scale)
        
        # For high DPI displays
        from PyQt6.QtCore import Qt
        app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
        app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

def get_window_geometry(window_name):
    """Get saved window position and size"""
    positions = app_settings.get("window_positions", {})
    return positions.get(window_name, None)

def save_window_geometry(window_name, geometry):
    """Save window position and size"""
    positions = app_settings.get("window_positions", {})
    positions[window_name] = {
        "x": geometry.x(),
        "y": geometry.y(),
        "width": geometry.width(),
        "height": geometry.height()
    }
    app_settings.set("window_positions", positions)