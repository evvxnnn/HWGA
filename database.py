import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join("data", "ops_logger.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Email logs
    c.execute("""
        CREATE TABLE IF NOT EXISTS email_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            log_type TEXT,
            sender TEXT,
            recipient TEXT,
            subject TEXT,
            timestamp TEXT,
            extra_field TEXT,
            msg_path TEXT,
            created_at TEXT
        )
    """)

    # Phone call logs
    c.execute("""
        CREATE TABLE IF NOT EXISTS phone_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            call_type TEXT,
            caller_name TEXT,
            site_code TEXT,
            ticket_number TEXT,
            address TEXT,
            alarm_type TEXT,
            issue_type TEXT,
            issue_subtype TEXT,
            message TEXT,
            timestamp TEXT,
            created_at TEXT
        )
    """)

    # Radio logs
    c.execute("""
        CREATE TABLE IF NOT EXISTS radio_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            unit TEXT,
            location TEXT,
            reason TEXT,
            arrived BOOLEAN,
            departed BOOLEAN,
            timestamp TEXT,
            created_at TEXT
        )
    """)

    # Everbridge alerts
    c.execute("""
        CREATE TABLE IF NOT EXISTS everbridge_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            site_code TEXT,
            message TEXT,
            timestamp TEXT,
            created_at TEXT
        )
    """)

    # Event chains
    c.execute("""
        CREATE TABLE IF NOT EXISTS event_chains (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            created_at TEXT
        )
    """)

    # Event links
    c.execute("""
        CREATE TABLE IF NOT EXISTS event_links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER,
            source_table TEXT,
            source_id INTEGER,
            timestamp TEXT,
            FOREIGN KEY (event_id) REFERENCES event_chains(id)
        )
    """)

    conn.commit()
    conn.close()

# Email insert already exists
def insert_email_log(log_type, sender, recipient, subject, timestamp, extra_field, msg_path):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO email_logs (log_type, sender, recipient, subject, timestamp, extra_field, msg_path, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        log_type, sender, recipient, subject, timestamp, extra_field, msg_path,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()

def insert_phone_log(call_type, caller_name, site_code, ticket_number, address, alarm_type, issue_type, issue_subtype, message, timestamp):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO phone_logs (
            call_type, caller_name, site_code, ticket_number, address,
            alarm_type, issue_type, issue_subtype, message, timestamp, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        call_type, caller_name, site_code, ticket_number, address,
        alarm_type, issue_type, issue_subtype, message, timestamp,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()

def insert_radio_log(unit, location, reason, arrived, departed, timestamp):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO radio_logs (
            unit, location, reason, arrived, departed, timestamp, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        unit, location, reason, int(arrived), int(departed), timestamp,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()

def insert_everbridge_log(site_code, message, timestamp):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO everbridge_logs (
            site_code, message, timestamp, created_at
        ) VALUES (?, ?, ?, ?)
    """, (
        site_code, message, timestamp,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()

# New helper function to get log details (for the improved Event Manager)
def get_log_details(table, log_id):
    """Get full details of a specific log entry"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Get column names
    c.execute(f"PRAGMA table_info({table})")
    columns = [col[1] for col in c.fetchall()]
    
    # Get the log data
    c.execute(f"SELECT * FROM {table} WHERE id = ?", (log_id,))
    row = c.fetchone()
    
    conn.close()
    
    if row:
        return dict(zip(columns, row))
    return None