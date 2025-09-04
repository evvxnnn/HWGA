"""
Customizable launcher button configuration and management
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QListWidget, QListWidgetItem,
    QGroupBox, QDialogButtonBox, QFileDialog, QMessageBox,
    QTabWidget, QWidget, QTextEdit, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from ui.styles import Fonts, get_button_style, DROPDOWN_STYLE
import json
import os
import subprocess
import webbrowser


class LauncherButton(QPushButton):
    """A customizable launcher button"""
    
    def __init__(self, config=None, parent=None):
        super().__init__(parent)
        self.config = config or {}
        self.update_display()
        self.clicked.connect(self.launch)
        
        # Style for launcher buttons
        self.setFixedSize(120, 120)
        self.setStyleSheet("""
            QPushButton {
                background-color: #1a1a1a;
                color: #e0e0e0;
                border: 2px dashed #333333;
                border-radius: 4px;
                padding: 8px;
                font-size: 11px;
                font-weight: 500;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #262626;
                border: 2px dashed #4a4a4a;
            }
            QPushButton:pressed {
                background-color: #333333;
            }
        """)
    
    def update_display(self):
        """Update button display based on configuration"""
        if self.config.get('name'):
            self.setText(self.config['name'])
            self.setToolTip(self.config.get('description', ''))
            # Solid border for configured buttons
            self.setStyleSheet("""
                QPushButton {
                    background-color: #1a1a1a;
                    color: #e0e0e0;
                    border: 1px solid #333333;
                    border-radius: 4px;
                    padding: 8px;
                    font-size: 11px;
                    font-weight: 500;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: #262626;
                    border: 1px solid #4a4a4a;
                }
                QPushButton:pressed {
                    background-color: #333333;
                }
            """)
        else:
            self.setText("+ Add\nShortcut")
            self.setToolTip("Click to configure this launcher")
    
    def set_config(self, config):
        """Set button configuration"""
        self.config = config
        self.update_display()
    
    def launch(self):
        """Launch the configured action"""
        if not self.config.get('name'):
            # Open configuration dialog
            dialog = LauncherConfigDialog(self.config, self.parent())
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.config = dialog.get_config()
                self.update_display()
                # Save configuration
                if hasattr(self.parent(), 'save_launcher_configs'):
                    self.parent().save_launcher_configs()
                else:
                    # Save directly if parent doesn't have the method
                    self.save_config_directly()
            return
        
        launch_type = self.config.get('type', 'none')
        
        if launch_type == 'program':
            # Launch program/exe
            path = self.config.get('path', '')
            if path:
                try:
                    # Check if it's a full path that exists
                    if os.path.exists(path):
                        if os.name == 'nt':  # Windows
                            # Use the start command which works for most file types
                            # The empty quotes are for the window title
                            cmd = f'start "" "{path}"'
                            subprocess.run(cmd, shell=True, check=False)
                        else:
                            os.startfile(path) if hasattr(os, 'startfile') else subprocess.run([path])
                    else:
                        # Try as a system command (for calc.exe, notepad.exe, etc)
                        if os.name == 'nt':
                            # Try to run directly (for system PATH commands)
                            subprocess.run(path, shell=True, check=False)
                        else:
                            subprocess.run([path], check=False)
                except Exception as e:
                    QMessageBox.critical(None, "Launch Error", f"Failed to launch {path}:\n{str(e)}")
        
        elif launch_type == 'single_link':
            # Open single URL
            url = self.config.get('url', '')
            if url:
                if not url.startswith(('http://', 'https://')):
                    url = 'https://' + url
                webbrowser.open(url)
        
        elif launch_type == 'multi_link':
            # Open multiple URLs
            urls = self.config.get('urls', [])
            for url in urls:
                if url:
                    if not url.startswith(('http://', 'https://')):
                        url = 'https://' + url
                    webbrowser.open_new_tab(url)
        
        elif launch_type == 'folder':
            # Open folder in explorer
            path = self.config.get('path', '')
            if path and os.path.exists(path):
                os.startfile(path)
            else:
                QMessageBox.warning(None, "Not Found", f"Folder not found: {path}")
    
    def save_config_directly(self):
        """Save configuration directly to file"""
        try:
            # Load existing configs
            try:
                with open('launcher_configs.json', 'r') as f:
                    configs = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                configs = {}
            
            # Find button index
            if hasattr(self.parent(), 'launcher_buttons'):
                for i, btn in enumerate(self.parent().launcher_buttons):
                    if btn == self:
                        configs[str(i)] = self.config
                        break
            
            # Save to file
            with open('launcher_configs.json', 'w') as f:
                json.dump(configs, f, indent=2)
        except Exception as e:
            print(f"Error saving launcher config: {e}")
    
    def edit_config(self):
        """Edit button configuration"""
        dialog = LauncherConfigDialog(self.config, self.parent())
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.config = dialog.get_config()
            self.update_display()
            # Save configuration
            if hasattr(self.parent(), 'save_launcher_configs'):
                self.parent().save_launcher_configs()
            else:
                self.save_config_directly()


class LauncherConfigDialog(QDialog):
    """Dialog for configuring launcher buttons"""
    
    def __init__(self, config=None, parent=None):
        super().__init__(parent)
        self.config = config or {}
        self.setWindowTitle("Configure Launcher Button")
        self.setMinimumSize(600, 500)
        self.init_ui()
        self.load_config()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Name and description
        layout.addWidget(QLabel("Button Name:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., Outlook, Reports, Tools")
        self.name_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                background-color: #1a1a1a;
                color: #e0e0e0;
                border: 1px solid #333333;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.name_input)
        
        layout.addWidget(QLabel("Description (tooltip):"))
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Optional description shown on hover")
        self.desc_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                background-color: #1a1a1a;
                color: #e0e0e0;
                border: 1px solid #333333;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.desc_input)
        
        # Launch type
        layout.addWidget(QLabel("Launch Type:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "None (Empty)",
            "Program/Application",
            "Single Website",
            "Multiple Websites",
            "Folder"
        ])
        self.type_combo.setStyleSheet(DROPDOWN_STYLE)
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        layout.addWidget(self.type_combo)
        
        # Stacked widget for different configurations
        self.config_tabs = QTabWidget()
        self.config_tabs.setStyleSheet("""
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
            }
        """)
        
        # Program configuration
        self.program_widget = self.create_program_config()
        self.config_tabs.addTab(self.program_widget, "Program")
        
        # Single link configuration
        self.single_link_widget = self.create_single_link_config()
        self.config_tabs.addTab(self.single_link_widget, "Single Link")
        
        # Multi link configuration
        self.multi_link_widget = self.create_multi_link_config()
        self.config_tabs.addTab(self.multi_link_widget, "Multiple Links")
        
        # Folder configuration
        self.folder_widget = self.create_folder_config()
        self.config_tabs.addTab(self.folder_widget, "Folder")
        
        layout.addWidget(self.config_tabs)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        # Clear button
        clear_btn = QPushButton("Clear Configuration")
        clear_btn.setStyleSheet(get_button_style())
        clear_btn.clicked.connect(self.clear_config)
        button_box.addButton(clear_btn, QDialogButtonBox.ButtonRole.ActionRole)
        
        layout.addWidget(button_box)
        self.setLayout(layout)
    
    def create_program_config(self):
        """Create program configuration widget"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Program Path:"))
        path_layout = QHBoxLayout()
        
        self.program_path = QLineEdit()
        self.program_path.setPlaceholderText("C:\\Program Files\\Application\\app.exe")
        self.program_path.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                background-color: #1a1a1a;
                color: #e0e0e0;
                border: 1px solid #333333;
                border-radius: 4px;
            }
        """)
        path_layout.addWidget(self.program_path)
        
        browse_btn = QPushButton("Browse")
        browse_btn.setStyleSheet(get_button_style())
        browse_btn.clicked.connect(self.browse_program)
        path_layout.addWidget(browse_btn)
        
        layout.addLayout(path_layout)
        
        # Common programs
        layout.addWidget(QLabel("Common Programs:"))
        common_programs = [
            ("Calculator", "calc.exe"),
            ("Notepad", "notepad.exe"),
            ("Command Prompt", "cmd.exe"),
            ("PowerShell", "powershell.exe"),
            ("File Explorer", "explorer.exe"),
            ("Task Manager", "taskmgr.exe")
        ]
        
        programs_grid = QGridLayout()
        for i, (name, path) in enumerate(common_programs):
            btn = QPushButton(name)
            btn.setStyleSheet(get_button_style())
            btn.clicked.connect(lambda checked, p=path, n=name: self.set_common_program(p, n))
            programs_grid.addWidget(btn, i // 2, i % 2)
        
        layout.addLayout(programs_grid)
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def create_single_link_config(self):
        """Create single link configuration widget"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Website URL:"))
        self.single_url = QLineEdit()
        self.single_url.setPlaceholderText("https://example.com or example.com")
        self.single_url.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                background-color: #1a1a1a;
                color: #e0e0e0;
                border: 1px solid #333333;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.single_url)
        
        # Common links
        layout.addWidget(QLabel("Common Links:"))
        common_links = [
            ("Google", "https://google.com"),
            ("Gmail", "https://gmail.com"),
            ("Outlook", "https://outlook.com"),
            ("Teams", "https://teams.microsoft.com"),
            ("SharePoint", "https://sharepoint.com"),
            ("Company Portal", "")
        ]
        
        links_grid = QGridLayout()
        for i, (name, url) in enumerate(common_links):
            if url:
                btn = QPushButton(name)
                btn.setStyleSheet(get_button_style())
                btn.clicked.connect(lambda checked, u=url, n=name: self.set_single_link(u, n))
                links_grid.addWidget(btn, i // 2, i % 2)
        
        layout.addLayout(links_grid)
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def create_multi_link_config(self):
        """Create multi link configuration widget"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Website URLs (one per line):"))
        self.multi_urls = QTextEdit()
        self.multi_urls.setPlaceholderText("https://example1.com\nhttps://example2.com\nhttps://example3.com")
        self.multi_urls.setStyleSheet("""
            QTextEdit {
                padding: 8px;
                background-color: #1a1a1a;
                color: #e0e0e0;
                border: 1px solid #333333;
                border-radius: 4px;
            }
        """)
        self.multi_urls.setMaximumHeight(150)
        layout.addWidget(self.multi_urls)
        
        # Preset groups
        layout.addWidget(QLabel("Preset Link Groups:"))
        preset_groups = [
            ("Daily Reports", ["https://reports.example.com", "https://analytics.example.com"]),
            ("Communication", ["https://gmail.com", "https://teams.microsoft.com", "https://slack.com"]),
            ("News", ["https://cnn.com", "https://bbc.com", "https://reuters.com"]),
            ("Security Tools", ["https://virustotal.com", "https://haveibeenpwned.com"])
        ]
        
        for name, urls in preset_groups:
            btn = QPushButton(f"Load {name}")
            btn.setStyleSheet(get_button_style())
            btn.clicked.connect(lambda checked, u=urls, n=name: self.set_multi_links(u, n))
            layout.addWidget(btn)
        
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def create_folder_config(self):
        """Create folder configuration widget"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Folder Path:"))
        path_layout = QHBoxLayout()
        
        self.folder_path = QLineEdit()
        self.folder_path.setPlaceholderText("C:\\Users\\Documents")
        self.folder_path.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                background-color: #1a1a1a;
                color: #e0e0e0;
                border: 1px solid #333333;
                border-radius: 4px;
            }
        """)
        path_layout.addWidget(self.folder_path)
        
        browse_btn = QPushButton("Browse")
        browse_btn.setStyleSheet(get_button_style())
        browse_btn.clicked.connect(self.browse_folder)
        path_layout.addWidget(browse_btn)
        
        layout.addLayout(path_layout)
        
        # Quick folders
        layout.addWidget(QLabel("Quick Access:"))
        quick_folders = [
            ("Documents", os.path.expanduser("~/Documents")),
            ("Downloads", os.path.expanduser("~/Downloads")),
            ("Desktop", os.path.expanduser("~/Desktop")),
            ("C: Drive", "C:\\"),
            ("Program Files", "C:\\Program Files"),
            ("Temp", os.environ.get('TEMP', ''))
        ]
        
        folders_grid = QGridLayout()
        for i, (name, path) in enumerate(quick_folders):
            btn = QPushButton(name)
            btn.setStyleSheet(get_button_style())
            btn.clicked.connect(lambda checked, p=path, n=name: self.set_folder(p, n))
            folders_grid.addWidget(btn, i // 2, i % 2)
        
        layout.addLayout(folders_grid)
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def on_type_changed(self, text):
        """Handle launch type change"""
        if "Program" in text:
            self.config_tabs.setCurrentIndex(0)
        elif "Single" in text:
            self.config_tabs.setCurrentIndex(1)
        elif "Multiple" in text:
            self.config_tabs.setCurrentIndex(2)
        elif "Folder" in text:
            self.config_tabs.setCurrentIndex(3)
    
    def browse_program(self):
        """Browse for program file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Program or Shortcut",
            "C:\\Program Files",
            "Programs (*.exe *.lnk *.bat *.cmd);;Executable Files (*.exe);;Shortcuts (*.lnk);;All Files (*.*)"
        )
        if file_path:
            self.program_path.setText(file_path)
            # Auto-fill name if empty
            if not self.name_input.text():
                name = os.path.splitext(os.path.basename(file_path))[0]
                self.name_input.setText(name)
    
    def browse_folder(self):
        """Browse for folder"""
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Select Folder",
            os.path.expanduser("~")
        )
        if folder_path:
            self.folder_path.setText(folder_path)
            # Auto-fill name if empty
            if not self.name_input.text():
                self.name_input.setText(os.path.basename(folder_path) or "Folder")
    
    def set_common_program(self, path, name):
        """Set a common program"""
        # For system commands like calc.exe, just use the command name
        # They're in the system PATH and don't need full paths
        self.program_path.setText(path)
        if not self.name_input.text():
            self.name_input.setText(name)
    
    def set_single_link(self, url, name):
        """Set a single link"""
        self.single_url.setText(url)
        if not self.name_input.text():
            self.name_input.setText(name)
    
    def set_multi_links(self, urls, name):
        """Set multiple links"""
        self.multi_urls.setText("\n".join(urls))
        if not self.name_input.text():
            self.name_input.setText(name)
    
    def set_folder(self, path, name):
        """Set folder path"""
        self.folder_path.setText(path)
        if not self.name_input.text():
            self.name_input.setText(name)
    
    def clear_config(self):
        """Clear all configuration"""
        self.name_input.clear()
        self.desc_input.clear()
        self.type_combo.setCurrentIndex(0)
        self.program_path.clear()
        self.single_url.clear()
        self.multi_urls.clear()
        self.folder_path.clear()
    
    def load_config(self):
        """Load existing configuration"""
        if self.config:
            self.name_input.setText(self.config.get('name', ''))
            self.desc_input.setText(self.config.get('description', ''))
            
            launch_type = self.config.get('type', 'none')
            if launch_type == 'program':
                self.type_combo.setCurrentText("Program/Application")
                self.program_path.setText(self.config.get('path', ''))
            elif launch_type == 'single_link':
                self.type_combo.setCurrentText("Single Website")
                self.single_url.setText(self.config.get('url', ''))
            elif launch_type == 'multi_link':
                self.type_combo.setCurrentText("Multiple Websites")
                urls = self.config.get('urls', [])
                self.multi_urls.setText("\n".join(urls))
            elif launch_type == 'folder':
                self.type_combo.setCurrentText("Folder")
                self.folder_path.setText(self.config.get('path', ''))
    
    def get_config(self):
        """Get the current configuration"""
        config = {
            'name': self.name_input.text(),
            'description': self.desc_input.text()
        }
        
        type_text = self.type_combo.currentText()
        if "Program" in type_text:
            config['type'] = 'program'
            config['path'] = self.program_path.text()
        elif "Single" in type_text:
            config['type'] = 'single_link'
            config['url'] = self.single_url.text()
        elif "Multiple" in type_text:
            config['type'] = 'multi_link'
            urls_text = self.multi_urls.toPlainText()
            config['urls'] = [url.strip() for url in urls_text.split('\n') if url.strip()]
        elif "Folder" in type_text:
            config['type'] = 'folder'
            config['path'] = self.folder_path.text()
        else:
            config['type'] = 'none'
        
        return config