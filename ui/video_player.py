"""
Video player widget with fallback for systems without QtWebEngine
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox
from PyQt6.QtCore import Qt, QUrl
import os
import webbrowser

try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    HAS_WEBENGINE = True
except ImportError:
    HAS_WEBENGINE = False
    QWebEngineView = None


class VideoPlayer(QWidget):
    """Video player that works with or without QtWebEngine"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_url = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        if HAS_WEBENGINE:
            # Use embedded web view
            self.web_view = QWebEngineView()
            self.web_view.setMinimumHeight(350)
            self.web_view.setStyleSheet("background-color: #000000;")
            layout.addWidget(self.web_view)
        else:
            # Fallback UI without web engine
            self.fallback_label = QLabel("Video Player")
            self.fallback_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.fallback_label.setStyleSheet("""
                QLabel {
                    background-color: #1a1a1a;
                    color: #808080;
                    border: 1px solid #333333;
                    border-radius: 4px;
                    padding: 20px;
                    min-height: 300px;
                    font-size: 14px;
                }
            """)
            layout.addWidget(self.fallback_label)
            
            # Button to open in browser
            self.open_browser_btn = QPushButton("Open Video in Browser")
            self.open_browser_btn.setStyleSheet("""
                QPushButton {
                    background-color: #262626;
                    color: #e0e0e0;
                    border: 1px solid #4a4a4a;
                    border-radius: 4px;
                    padding: 8px;
                }
                QPushButton:hover {
                    background-color: #333333;
                }
            """)
            self.open_browser_btn.clicked.connect(self.open_in_browser)
            self.open_browser_btn.setEnabled(False)
            layout.addWidget(self.open_browser_btn)
        
        self.setLayout(layout)
    
    def load_video(self, url):
        """Load a video URL"""
        self.current_url = url
        
        if not url:
            self.clear_video()
            return
        
        if HAS_WEBENGINE:
            # Handle different video sources
            if 'youtube.com' in url or 'youtu.be' in url:
                # Embed YouTube video
                video_id = self.extract_youtube_id(url)
                if video_id:
                    embed_html = f'''
                    <html>
                    <body style="margin: 0; background-color: #000;">
                    <iframe width="100%" height="100%" 
                        src="https://www.youtube.com/embed/{video_id}" 
                        frameborder="0" 
                        allowfullscreen>
                    </iframe>
                    </body>
                    </html>
                    '''
                    self.web_view.setHtml(embed_html)
            elif url.startswith('http'):
                # Load external URL
                self.web_view.load(QUrl(url))
            else:
                # Load local file
                local_path = os.path.join('training_videos', url)
                if os.path.exists(local_path):
                    # Create HTML5 video player for local file
                    video_html = f'''
                    <html>
                    <body style="margin: 0; background-color: #000;">
                    <video width="100%" height="100%" controls>
                        <source src="file:///{os.path.abspath(local_path)}" type="video/mp4">
                        Your browser does not support the video tag.
                    </video>
                    </body>
                    </html>
                    '''
                    self.web_view.setHtml(video_html)
                else:
                    self.web_view.setHtml('<html><body style="background-color: #1a1a1a; color: #808080; text-align: center; padding: 20px;">Video file not found</body></html>')
        else:
            # Fallback mode - update label and enable button
            if 'youtube.com' in url or 'youtu.be' in url:
                self.fallback_label.setText(f"Video Available:\n\nClick 'Open Video in Browser' to watch\n\nURL: {url}")
                self.open_browser_btn.setEnabled(True)
            elif url.startswith('http'):
                self.fallback_label.setText(f"External Video:\n\n{url}\n\nClick 'Open Video in Browser' to watch")
                self.open_browser_btn.setEnabled(True)
            else:
                local_path = os.path.join('training_videos', url)
                if os.path.exists(local_path):
                    self.fallback_label.setText(f"Local Video:\n\n{url}\n\nVideo playback requires QtWebEngine.\nPlease install it or use an external player.")
                    self.open_browser_btn.setEnabled(False)
                else:
                    self.fallback_label.setText("Video file not found")
                    self.open_browser_btn.setEnabled(False)
    
    def clear_video(self):
        """Clear the video player"""
        if HAS_WEBENGINE:
            self.web_view.setHtml('<html><body style="background-color: #1a1a1a;"></body></html>')
        else:
            self.fallback_label.setText("No video available for this training")
            self.open_browser_btn.setEnabled(False)
    
    def open_in_browser(self):
        """Open video in external browser"""
        if self.current_url:
            webbrowser.open(self.current_url)
    
    def extract_youtube_id(self, url):
        """Extract YouTube video ID from URL"""
        if 'youtube.com' in url:
            if 'watch?v=' in url:
                return url.split('watch?v=')[-1].split('&')[0]
            elif '/embed/' in url:
                return url.split('/embed/')[-1].split('?')[0]
        elif 'youtu.be' in url:
            return url.split('/')[-1].split('?')[0]
        return None