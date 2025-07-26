import sqlite3
import os
from datetime import datetime
from database import DB_PATH, get_log_details

# Load all logs with timestamp from all tables
def load_all_logs():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    logs = []

    sources = {
        "email_logs": "Email",
        "phone_logs": "Phone",
        "radio_logs": "Radio",
        "everbridge_logs": "Everbridge"
    }

    for table, label in sources.items():
        c.execute(f"SELECT id, timestamp FROM {table}")
        rows = c.fetchall()
        for row in rows:
            logs.append({
                "source": label,
                "table": table,
                "id": row[0],
                "timestamp": row[1]
            })

    logs.sort(key=lambda x: x["timestamp"])
    conn.close()
    return logs

# Create a new event chain
def create_event_chain(title, description=""):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        INSERT INTO event_chains (title, description, created_at)
        VALUES (?, ?, ?)
    """, (title, description, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    event_id = c.lastrowid
    conn.commit()
    conn.close()
    return event_id

# Link a log to an event chain
def link_log_to_event(event_id, table, source_id, timestamp):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        INSERT INTO event_links (event_id, source_table, source_id, timestamp)
        VALUES (?, ?, ?, ?)
    """, (event_id, table, source_id, timestamp))

    conn.commit()
    conn.close()

# Get all existing event chains
def get_event_chains():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT id, title, created_at FROM event_chains ORDER BY created_at DESC")
    results = c.fetchall()

    conn.close()
    return [{"id": r[0], "title": r[1], "created_at": r[2]} for r in results]

# Get all logs linked to a specific chain
def get_event_chain_logs(event_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        SELECT source_table, source_id, timestamp
        FROM event_links
        WHERE event_id = ?
        ORDER BY timestamp
    """, (event_id,))

    rows = c.fetchall()
    conn.close()
    return rows

# Get summary of a log by source_table and id
def get_log_summary(table, log_id):
    """Get a meaningful summary of the log"""
    details = get_log_details(table, log_id)
    if not details:
        return "(No summary available)"
    
    if table == "email_logs":
        return f"{details.get('log_type', 'Email')}: {details.get('subject', 'No subject')}"
    elif table == "phone_logs":
        caller = details.get('caller_name', 'Unknown')
        call_type = details.get('call_type', 'Phone')
        if details.get('site_code'):
            return f"{call_type} from {caller} - Site {details['site_code']}"
        else:
            return f"{call_type} from {caller}"
    elif table == "radio_logs":
        return f"{details.get('unit', 'Unit')} - {details.get('reason', 'Unknown reason')}"
    elif table == "everbridge_logs":
        message = details.get('message', '')
        return message[:50] + "..." if len(message) > 50 else message
    else:
        return "(Unknown log type)"

# Update event chain (for editing)
def update_event_chain(event_id, title, description):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("""
        UPDATE event_chains 
        SET title = ?, description = ?
        WHERE id = ?
    """, (title, description, event_id))
    
    conn.commit()
    conn.close()