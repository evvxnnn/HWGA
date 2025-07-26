# Configuration file for Security Ops Logger

import os

# Database path - using local database
DB_PATH = os.path.join("data", "ops_logger.db")

# User identification
CURRENT_USER = os.environ.get('USERNAME', 'Unknown User')

# Site codes for dropdown menus (customize as needed)
SITE_CODES = [
    "MAIN", "NORTH", "SOUTH", "EAST", "WEST",
    "DC1", "DC2", "HQ", "WAREHOUSE"
]

# Alarm types for phone logs
ALARM_TYPES = [
    "Burglar", "Fire", "Medical", "Panic", "Duress",
    "Environmental", "Equipment", "Test", "Other"
]