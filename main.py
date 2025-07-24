from PyQt6.QtWidgets import QApplication
from ui.home import HomeWindow
from database import init_db
import sys
import os

def main():
    # Ensure data directory exists
    if not os.path.exists("data"):
        os.makedirs("data")
    
    # Initialize database
    init_db()
    
    # Start application
    app = QApplication(sys.argv)
    window = HomeWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()