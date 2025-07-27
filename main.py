from PyQt6.QtWidgets import QApplication, QLabel, QMessageBox
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from ui.home import HomeWindow
from database import init_db
from app_settings import apply_display_scaling, app_settings
import sys
import os

def show_splash():
    """Show splash screen while loading"""
    splash_widget = QLabel("Security Operations Logger")
    splash_widget.setWindowFlags(Qt.WindowType.SplashScreen | Qt.WindowType.FramelessWindowHint)
    splash_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
    splash_widget.setStyleSheet("""
        QLabel {
            background-color: #1976D2;
            color: white;
            font-size: 36px;
            font-weight: bold;
            padding: 100px;
        }
    """)
    splash_widget.setMinimumSize(600, 400)
    splash_widget.show()
    
    return splash_widget

def main():
    # Create application
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Security Ops Logger")
    app.setOrganizationName("Security Operations")
    
    # Apply display scaling
    apply_display_scaling(app)
    
    # Set global application style
    app.setStyle("Fusion")  # Modern look across platforms
    
    # Global stylesheet for consistent look
    app.setStyleSheet("""
        QMainWindow {
            background-color: #FAFAFA;
        }
        QWidget {
            font-family: Arial, sans-serif;
        }
        QMessageBox {
            background-color: white;
        }
        QMessageBox QPushButton {
            min-width: 100px;
            min-height: 40px;
            font-size: 14px;
        }
        QToolTip {
            background-color: #1976D2;
            color: white;
            border: none;
            padding: 8px;
            font-size: 14px;
        }
    """)
    
    # Show splash screen
    splash = show_splash()
    app.processEvents()
    
    # Ensure data directory exists
    if not os.path.exists("data"):
        os.makedirs("data")
    
    # Initialize database
    try:
        init_db()
    except Exception as e:
        splash.close()
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.critical(None, "Database Error", 
                           f"Failed to initialize database:\n\n{str(e)}")
        return
    
    # Create main window
    window = HomeWindow()
    
    # Close splash and show main window
    QTimer.singleShot(1000, splash.close)
    QTimer.singleShot(1100, window.show)
    
    # Handle application exit
    app.aboutToQuit.connect(lambda: handle_exit(window))
    
    sys.exit(app.exec())

def handle_exit(window):
    """Handle application exit"""
    # Save window geometry
    from app_settings import save_window_geometry
    save_window_geometry("main", window.geometry())
    
    # Any other cleanup
    print("Security Ops Logger closed")

if __name__ == "__main__":
    main()