from PyQt6.QtWidgets import QPushButton, QMessageBox
from PyQt6.QtCore import Qt
from ui.styles import get_button_style

class HelpButton(QPushButton):
    """A standardized help button that opens training for specific modules"""
    
    def __init__(self, module_name, training_id=None, parent=None):
        super().__init__("Help", parent)
        self.module_name = module_name
        self.training_id = training_id
        
        # Style the help button
        self.setFixedSize(60, 30)
        self.setStyleSheet("""
            QPushButton {
                background-color: #262626;
                color: #e0e0e0;
                border: 1px solid #4a4a4a;
                border-radius: 4px;
                font-size: 11px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #333333;
                border: 1px solid #5a5a5a;
            }
            QPushButton:pressed {
                background-color: #404040;
            }
        """)
        
        # Connect to open training
        self.clicked.connect(self.open_help)
    
    def open_help(self):
        """Open the training module for this specific page"""
        from ui.training_ui import TrainingPanel
        
        # Create training window
        self.training_window = TrainingPanel(direct_training_id=self.training_id)
        self.training_window.show()
        
        # If no specific training ID, show a message
        if not self.training_id:
            QMessageBox.information(
                self,
                "Help",
                f"Opening training center for: {self.module_name}\n\n"
                "Look for tutorials related to this module in the 'Application Help' category."
            )


# Default training content for each module
DEFAULT_TRAININGS = {
    "app_home": {
        "id": "app_001",
        "title": "Using the Home Screen",
        "category": "Application Help",
        "description": """
<h2>Security Operations Logger - Home Screen Guide</h2>

<h3>Overview</h3>
<p>The home screen is your main dashboard for accessing all features of the Security Operations Logger. 
This guide will help you navigate and use the home screen effectively.</p>

<h3>Main Sections</h3>

<h4>1. Log New Activity Section</h4>
<p>This section contains four square buttons for logging different types of activities:</p>
<ul>
<li><b>Email (F1)</b> - Click to log email communications</li>
<li><b>Phone (F2)</b> - Click to log phone calls</li>
<li><b>Radio (F3)</b> - Click to log radio dispatches</li>
<li><b>Everbridge (F4)</b> - Click to log Everbridge alerts</li>
</ul>

<h4>2. Management Tools Section</h4>
<p>This section provides access to management and analysis tools:</p>
<ul>
<li><b>Event Manager (F5)</b> - Link related activities into event chains</li>
<li><b>Statistics (F6)</b> - View reports and analytics</li>
<li><b>View Logs (F7)</b> - Browse and export historical logs</li>
<li><b>Training (F8)</b> - Access training materials and help guides</li>
</ul>

<h3>Keyboard Shortcuts</h3>
<p>For faster access, you can use keyboard shortcuts:</p>
<ul>
<li>Press <b>F1-F8</b> to quickly open any module</li>
<li>Press <b>F11</b> to toggle fullscreen mode</li>
<li>Press <b>Ctrl+Q</b> to exit the application</li>
<li>Press <b>Ctrl+H</b> to view all keyboard shortcuts</li>
</ul>

<h3>Tips for New Users</h3>
<ul>
<li>Start with the Training module (F8) to learn about each feature</li>
<li>The square button layout makes it easy to click with a mouse or touchscreen</li>
<li>The dark theme reduces eye strain during long shifts</li>
<li>All text is sized for easy reading on standard monitors</li>
</ul>

<h3>Getting Started</h3>
<ol>
<li>Choose the type of activity you want to log</li>
<li>Click the appropriate button or press its function key</li>
<li>Fill out the form in the window that opens</li>
<li>Submit your entry when complete</li>
</ol>
        """,
        "duration": "10 minutes",
        "created_by": "System",
        "created_date": "2024-01-01",
        "video_url": "",
        "materials": ["Home_Screen_Guide.pdf"],
        "quiz_required": False
    },
    
    "app_email": {
        "id": "app_002",
        "title": "Logging Email Communications",
        "category": "Application Help",
        "description": """
<h2>Email Logging Module - Complete Guide</h2>

<h3>Overview</h3>
<p>The Email module allows you to log and categorize email communications for security operations tracking.</p>

<h3>Opening the Email Logger</h3>
<ul>
<li>Click the "Email" button on the home screen, or</li>
<li>Press the <b>F1</b> key from anywhere in the application</li>
</ul>

<h3>Using the Email Logger</h3>

<h4>Step 1: Import Email</h4>
<p>You have two options to import an email:</p>
<ol>
<li><b>Drag and Drop:</b> Drag a .msg file from Outlook directly onto the drop zone</li>
<li><b>Browse:</b> Click the drop zone to browse and select a .msg file</li>
</ol>

<h4>Step 2: Select Category</h4>
<p>Choose the appropriate category tab for your email:</p>
<ul>
<li><b>Data Request</b> - Requests for information or data</li>
<li><b>Incident Report</b> - Reports of security incidents</li>
<li><b>Muster Report</b> - Emergency muster communications</li>
<li><b>Parking Tag App</b> - Parking-related requests</li>
<li><b>Badge Deactivation</b> - Badge/access control requests</li>
<li><b>Everbridge Alert</b> - Everbridge system notifications</li>
<li><b>Notification</b> - General notifications</li>
<li><b>Other</b> - Anything not covered above</li>
</ul>

<h4>Step 3: Fill Required Fields</h4>
<p>Each category may have specific fields to complete:</p>
<ul>
<li><b>Site Code</b> - Select the relevant location</li>
<li><b>Priority</b> - Set the urgency level</li>
<li><b>Notes</b> - Add any additional context</li>
</ul>

<h4>Step 4: Submit</h4>
<p>Click the "Submit" button to save the email log entry</p>

<h3>Tips and Best Practices</h3>
<ul>
<li>Always select the most specific category for better reporting</li>
<li>Add notes for unusual situations or important context</li>
<li>The system automatically extracts sender, subject, and timestamp from .msg files</li>
<li>You can log multiple emails quickly by staying in the same window</li>
</ul>

<h3>Troubleshooting</h3>
<ul>
<li><b>Can't import .msg file:</b> Ensure Outlook is installed on your computer</li>
<li><b>Fields not auto-filling:</b> Check that the .msg file is not corrupted</li>
<li><b>Submit button disabled:</b> Make sure all required fields are completed</li>
</ul>

<h3>Keyboard Shortcuts</h3>
<ul>
<li><b>Tab</b> - Move to next field</li>
<li><b>Shift+Tab</b> - Move to previous field</li>
<li><b>Enter</b> - Submit form (when button is focused)</li>
<li><b>Escape</b> - Close the window</li>
</ul>
        """,
        "duration": "15 minutes",
        "created_by": "System",
        "created_date": "2024-01-01",
        "video_url": "",
        "materials": ["Email_Logger_Guide.pdf"],
        "quiz_required": True
    },
    
    "app_phone": {
        "id": "app_003",
        "title": "Logging Phone Calls",
        "category": "Application Help",
        "description": """
<h2>Phone Call Logging - Complete Guide</h2>

<h3>Overview</h3>
<p>The Phone module helps you document all phone communications for security operations.</p>

<h3>Opening the Phone Logger</h3>
<ul>
<li>Click the "Phone" button on the home screen, or</li>
<li>Press the <b>F2</b> key from anywhere in the application</li>
</ul>

<h3>Logging a Phone Call</h3>

<h4>Step 1: Caller Information</h4>
<p>Enter the caller details:</p>
<ul>
<li><b>Caller Name</b> - Full name if known, or "Unknown"</li>
<li><b>Phone Number</b> - Include area code</li>
<li><b>Company/Organization</b> - If applicable</li>
</ul>

<h4>Step 2: Call Details</h4>
<ul>
<li><b>Call Direction</b> - Select "Incoming" or "Outgoing"</li>
<li><b>Date/Time</b> - Automatically set to current time (can be adjusted)</li>
<li><b>Duration</b> - Approximate length of call</li>
</ul>

<h4>Step 3: Call Purpose</h4>
<p>Select the primary reason for the call:</p>
<ul>
<li>Information Request</li>
<li>Incident Report</li>
<li>Follow-up</li>
<li>Emergency</li>
<li>Complaint</li>
<li>Other</li>
</ul>

<h4>Step 4: Call Summary</h4>
<p>Provide a brief but complete summary of the conversation:</p>
<ul>
<li>Key points discussed</li>
<li>Any commitments made</li>
<li>Follow-up actions required</li>
<li>Names of other people mentioned</li>
</ul>

<h4>Step 5: Action Items</h4>
<p>Document any required follow-up:</p>
<ul>
<li>Tasks to complete</li>
<li>People to contact</li>
<li>Deadlines mentioned</li>
</ul>

<h3>Best Practices</h3>
<ul>
<li>Log calls immediately after they end while details are fresh</li>
<li>Be objective and factual in your summaries</li>
<li>Include direct quotes for important statements</li>
<li>Note the caller's emotional state if relevant (angry, confused, etc.)</li>
<li>Always get a callback number</li>
</ul>

<h3>Quick Entry Tips</h3>
<ul>
<li>Use templates for frequent call types</li>
<li>Keep the logger open during your shift for quick access</li>
<li>Use abbreviations consistently (document them in notes)</li>
</ul>

<h3>Important Reminders</h3>
<ul>
<li>All logged calls become part of the permanent record</li>
<li>Be professional in all descriptions</li>
<li>Never include personal opinions unless clearly marked as such</li>
<li>Include badge numbers or employee IDs when mentioned</li>
</ul>
        """,
        "duration": "15 minutes",
        "created_by": "System",
        "created_date": "2024-01-01",
        "video_url": "",
        "materials": ["Phone_Logger_Guide.pdf"],
        "quiz_required": True
    },
    
    "app_radio": {
        "id": "app_004",
        "title": "Logging Radio Dispatches",
        "category": "Application Help",
        "description": """
<h2>Radio Dispatch Logging - Complete Guide</h2>

<h3>Overview</h3>
<p>The Radio module is for logging all radio communications and dispatches.</p>

<h3>Opening the Radio Logger</h3>
<ul>
<li>Click the "Radio" button on the home screen, or</li>
<li>Press the <b>F3</b> key</li>
</ul>

<h3>Understanding Radio Logs</h3>
<p>Radio logs are critical for:</p>
<ul>
<li>Tracking security patrol activities</li>
<li>Documenting emergency responses</li>
<li>Recording dispatch instructions</li>
<li>Maintaining communication records</li>
</ul>

<h3>Logging Radio Communications</h3>

<h4>Required Information</h4>
<ul>
<li><b>Call Sign/Unit</b> - The radio identifier of the caller</li>
<li><b>Channel</b> - Which radio channel was used</li>
<li><b>Time</b> - Exact time of transmission</li>
<li><b>Type</b> - Dispatch, Response, Status Update, Emergency</li>
</ul>

<h4>Message Content</h4>
<p>Record the communication accurately:</p>
<ul>
<li>Use standard radio codes when applicable</li>
<li>Note the location mentioned</li>
<li>Include unit numbers responding</li>
<li>Document any special instructions</li>
</ul>

<h3>Radio Codes Reference</h3>
<ul>
<li><b>10-4</b> - Acknowledged/Understood</li>
<li><b>10-20</b> - Location</li>
<li><b>10-23</b> - Stand by</li>
<li><b>10-97</b> - Arrived at scene</li>
<li><b>Code 1</b> - Routine response</li>
<li><b>Code 3</b> - Emergency response</li>
</ul>

<h3>Priority Levels</h3>
<ul>
<li><b>Emergency</b> - Immediate threat to life or property</li>
<li><b>Urgent</b> - Requires quick response</li>
<li><b>Routine</b> - Standard operations</li>
<li><b>Information</b> - No action required</li>
</ul>

<h3>Best Practices</h3>
<ul>
<li>Log in real-time when possible</li>
<li>Use clear, concise language</li>
<li>Include all unit numbers involved</li>
<li>Note any cross-channel communications</li>
<li>Record exact times for emergency calls</li>
</ul>

<h3>Common Scenarios</h3>
<ul>
<li><b>Patrol Check-ins:</b> Record unit, location, and status</li>
<li><b>Incident Response:</b> Note all units dispatched and arrival times</li>
<li><b>Status Changes:</b> Document when units go on/off duty</li>
<li><b>Emergency Calls:</b> Record complete details immediately</li>
</ul>
        """,
        "duration": "20 minutes",
        "created_by": "System",
        "created_date": "2024-01-01",
        "video_url": "",
        "materials": ["Radio_Logger_Guide.pdf", "Radio_Codes_Reference.pdf"],
        "quiz_required": True
    },
    
    "app_everbridge": {
        "id": "app_005",
        "title": "Logging Everbridge Alerts",
        "category": "Application Help",
        "description": """
<h2>Everbridge Alert Logging - Complete Guide</h2>

<h3>Overview</h3>
<p>The Everbridge module tracks all emergency notification system alerts and responses.</p>

<h3>Opening the Everbridge Logger</h3>
<ul>
<li>Click the "Everbridge" button on the home screen, or</li>
<li>Press the <b>F4</b> key</li>
</ul>

<h3>Understanding Everbridge Alerts</h3>
<p>Everbridge is used for:</p>
<ul>
<li>Mass emergency notifications</li>
<li>Weather alerts</li>
<li>Security incidents</li>
<li>Facility emergencies</li>
<li>Test notifications</li>
</ul>

<h3>Logging an Alert</h3>

<h4>Alert Information</h4>
<ul>
<li><b>Alert Type</b> - Emergency, Weather, Test, Information</li>
<li><b>Severity</b> - Critical, High, Medium, Low</li>
<li><b>Launch Time</b> - When the alert was sent</li>
<li><b>Alert ID</b> - Everbridge system ID number</li>
</ul>

<h4>Message Details</h4>
<ul>
<li><b>Subject</b> - Alert headline</li>
<li><b>Message Body</b> - Complete alert text</li>
<li><b>Target Audience</b> - Who received the alert</li>
<li><b>Delivery Methods</b> - Email, SMS, Voice, App</li>
</ul>

<h4>Response Tracking</h4>
<ul>
<li><b>Confirmations</b> - Number of recipients who confirmed</li>
<li><b>Response Rate</b> - Percentage of successful deliveries</li>
<li><b>Follow-up Required</b> - Any non-responders to contact</li>
</ul>

<h3>Alert Categories</h3>

<h4>Emergency Alerts</h4>
<ul>
<li>Active shooter</li>
<li>Fire evacuation</li>
<li>Severe weather</li>
<li>Chemical spill</li>
<li>Medical emergency</li>
</ul>

<h4>Operational Alerts</h4>
<ul>
<li>Facility closure</li>
<li>Power outage</li>
<li>IT system issues</li>
<li>Parking changes</li>
</ul>

<h3>Best Practices</h3>
<ul>
<li>Log alerts immediately upon receipt</li>
<li>Include the complete message text</li>
<li>Track all follow-up actions</li>
<li>Note any delivery failures</li>
<li>Document test alerts clearly</li>
</ul>

<h3>Compliance Requirements</h3>
<ul>
<li>All emergency alerts must be logged</li>
<li>Include response statistics</li>
<li>Document any system issues</li>
<li>Maintain records for audit purposes</li>
</ul>
        """,
        "duration": "15 minutes",
        "created_by": "System",
        "created_date": "2024-01-01",
        "video_url": "",
        "materials": ["Everbridge_Guide.pdf"],
        "quiz_required": True
    },
    
    "app_events": {
        "id": "app_006",
        "title": "Using the Event Manager",
        "category": "Application Help",
        "description": """
<h2>Event Manager - Complete Guide</h2>

<h3>Overview</h3>
<p>The Event Manager links related activities into event chains for comprehensive incident tracking.</p>

<h3>Opening the Event Manager</h3>
<ul>
<li>Click "Event Manager" on the home screen, or</li>
<li>Press the <b>F5</b> key</li>
</ul>

<h3>Understanding Events</h3>
<p>An "event" is a collection of related activities such as:</p>
<ul>
<li>An initial phone call reporting an incident</li>
<li>Radio dispatches sending units to respond</li>
<li>Follow-up emails with details</li>
<li>Everbridge alerts sent to staff</li>
</ul>

<h3>Creating an Event</h3>

<h4>Step 1: Start New Event</h4>
<ul>
<li>Click "Create New Event"</li>
<li>Enter event name and description</li>
<li>Select event category</li>
<li>Set priority level</li>
</ul>

<h4>Step 2: Add Related Items</h4>
<ul>
<li>Search for existing logged items</li>
<li>Select items to link to the event</li>
<li>Items can be added from any module</li>
</ul>

<h4>Step 3: Create Timeline</h4>
<ul>
<li>System automatically orders items by timestamp</li>
<li>Review the sequence of activities</li>
<li>Add notes for context between items</li>
</ul>

<h4>Step 4: Close Event</h4>
<ul>
<li>Mark event as resolved</li>
<li>Add final summary</li>
<li>Generate event report if needed</li>
</ul>

<h3>Event Categories</h3>
<ul>
<li><b>Security Incident</b> - Theft, trespass, suspicious activity</li>
<li><b>Medical Emergency</b> - Injuries, illness, ambulance calls</li>
<li><b>Facility Issue</b> - Power outage, flooding, equipment failure</li>
<li><b>Weather Event</b> - Storms, closures, weather-related incidents</li>
<li><b>Fire/Evacuation</b> - Fire alarms, drills, actual fires</li>
</ul>

<h3>Best Practices</h3>
<ul>
<li>Create events for any incident requiring multiple activities</li>
<li>Link all related communications immediately</li>
<li>Keep event names clear and descriptive</li>
<li>Close events promptly when resolved</li>
<li>Use consistent naming conventions</li>
</ul>

<h3>Viewing Events</h3>
<ul>
<li>Filter by date range</li>
<li>Search by keyword</li>
<li>Sort by priority or status</li>
<li>Export event reports</li>
</ul>
        """,
        "duration": "20 minutes",
        "created_by": "System",
        "created_date": "2024-01-01",
        "video_url": "",
        "materials": ["Event_Manager_Guide.pdf"],
        "quiz_required": True
    },
    
    "app_stats": {
        "id": "app_007",
        "title": "Using Statistics & Reports",
        "category": "Application Help",
        "description": """
<h2>Statistics & Reports - Complete Guide</h2>

<h3>Overview</h3>
<p>The Statistics module provides analytics and reporting on all logged activities.</p>

<h3>Opening Statistics</h3>
<ul>
<li>Click "Statistics" on the home screen, or</li>
<li>Press the <b>F6</b> key</li>
</ul>

<h3>Available Reports</h3>

<h4>Activity Summary</h4>
<ul>
<li>Total activities by type</li>
<li>Daily/weekly/monthly trends</li>
<li>Peak activity times</li>
<li>Response time averages</li>
</ul>

<h4>Category Breakdown</h4>
<ul>
<li>Most common incident types</li>
<li>Distribution by location</li>
<li>Priority level analysis</li>
</ul>

<h4>Performance Metrics</h4>
<ul>
<li>Average response times</li>
<li>Resolution rates</li>
<li>Open vs closed events</li>
</ul>

<h3>Generating Reports</h3>

<h4>Step 1: Select Report Type</h4>
<ul>
<li>Daily Summary</li>
<li>Weekly Analysis</li>
<li>Monthly Report</li>
<li>Custom Date Range</li>
</ul>

<h4>Step 2: Choose Filters</h4>
<ul>
<li>Activity types to include</li>
<li>Specific locations</li>
<li>Priority levels</li>
<li>User/operator</li>
</ul>

<h4>Step 3: Export Options</h4>
<ul>
<li>View on screen</li>
<li>Export to PDF</li>
<li>Export to Excel</li>
<li>Print directly</li>
</ul>

<h3>Understanding Charts</h3>
<ul>
<li><b>Bar Charts</b> - Compare quantities across categories</li>
<li><b>Line Graphs</b> - Show trends over time</li>
<li><b>Pie Charts</b> - Display proportions</li>
<li><b>Tables</b> - Detailed data listings</li>
</ul>

<h3>Key Metrics Explained</h3>
<ul>
<li><b>Volume</b> - Total number of activities</li>
<li><b>Response Time</b> - Time from log to resolution</li>
<li><b>Distribution</b> - Spread across categories</li>
<li><b>Trends</b> - Changes over time periods</li>
</ul>

<h3>Using Reports Effectively</h3>
<ul>
<li>Run daily reports at shift end</li>
<li>Review weekly trends on Mondays</li>
<li>Generate monthly reports for management</li>
<li>Use filters to focus on specific issues</li>
</ul>
        """,
        "duration": "15 minutes",
        "created_by": "System",
        "created_date": "2024-01-01",
        "video_url": "",
        "materials": ["Statistics_Guide.pdf"],
        "quiz_required": False
    },
    
    "app_logs": {
        "id": "app_008",
        "title": "Using the Logs Viewer",
        "category": "Application Help",
        "description": """
<h2>Logs Viewer - Complete Guide</h2>

<h3>Overview</h3>
<p>The Logs Viewer allows you to browse, search, and export historical log data.</p>

<h3>Opening the Logs Viewer</h3>
<ul>
<li>Click "View Logs" on the home screen, or</li>
<li>Press the <b>F7</b> key</li>
</ul>

<h3>Available Log Types</h3>
<ul>
<li>Email Logs</li>
<li>Phone Call Logs</li>
<li>Radio Dispatch Logs</li>
<li>Everbridge Alert Logs</li>
<li>Incident Report Logs</li>
<li>Facilities Ticket Logs</li>
<li>Data Request Logs</li>
<li>Badge Deactivation Logs</li>
<li>Parking Tag Logs</li>
<li>Muster Report Logs</li>
</ul>

<h3>Viewing Logs</h3>

<h4>Step 1: Select Log Type</h4>
<ul>
<li>Choose from dropdown menu</li>
<li>Log loads automatically</li>
<li>Shows record count</li>
</ul>

<h4>Step 2: Filter Data</h4>
<ul>
<li><b>Date Range</b> - Select start and end dates</li>
<li><b>Search</b> - Enter keywords to find specific entries</li>
<li><b>Apply Filters</b> - Refine your view</li>
<li><b>Clear Filters</b> - Reset to show all</li>
</ul>

<h4>Step 3: Sort and Navigate</h4>
<ul>
<li>Click column headers to sort</li>
<li>Use scroll bars for large datasets</li>
<li>Resize columns as needed</li>
</ul>

<h3>Understanding the Display</h3>
<ul>
<li><b>Data View Tab</b> - Shows log entries in table format</li>
<li><b>Statistics Tab</b> - Displays summary information</li>
<li><b>Export Tab</b> - Options for exporting data</li>
</ul>

<h3>Searching Tips</h3>
<ul>
<li>Search looks through all columns</li>
<li>Use partial words for broader results</li>
<li>Search is not case-sensitive</li>
<li>Combine with date filters for best results</li>
</ul>

<h3>Exporting Data</h3>

<h4>Export Formats</h4>
<ul>
<li><b>Excel (.xlsx)</b> - Full spreadsheet functionality</li>
<li><b>CSV (.csv)</b> - Simple, compatible format</li>
<li><b>PDF Report</b> - Formatted for printing</li>
</ul>

<h4>Export Options</h4>
<ul>
<li><b>Current View</b> - Only filtered/displayed data</li>
<li><b>All Data</b> - Complete log file</li>
<li><b>Monthly Report</b> - Formatted summary report</li>
</ul>

<h3>Best Practices</h3>
<ul>
<li>Use date ranges to limit data size</li>
<li>Export filtered views for specific reports</li>
<li>Save exports with descriptive names</li>
<li>Regular exports for backup purposes</li>
</ul>

<h3>Common Tasks</h3>
<ul>
<li><b>Find specific incident:</b> Use search with date range</li>
<li><b>Monthly reporting:</b> Filter by month, export all</li>
<li><b>Audit trail:</b> Export complete logs for date range</li>
<li><b>Quick lookup:</b> Sort by relevant column</li>
</ul>
        """,
        "duration": "15 minutes",
        "created_by": "System",
        "created_date": "2024-01-01",
        "video_url": "",
        "materials": ["Logs_Viewer_Guide.pdf"],
        "quiz_required": False
    }
}


def get_help_training_id(module_name):
    """Get the training ID for a specific module"""
    training_map = {
        "home": "app_001",
        "email": "app_002",
        "phone": "app_003",
        "radio": "app_004",
        "everbridge": "app_005",
        "events": "app_006",
        "stats": "app_007",
        "logs": "app_008"
    }
    return training_map.get(module_name, None)