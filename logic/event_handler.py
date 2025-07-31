"""
Event handling utilities for linking and summarizing log entries.

This module provides functions to load logs across tables,
create and update event chains, and produce succinct summaries
for display in the UI. It utilizes context managers for all
database access and logs errors using the application logger.
"""

import sqlite3
from datetime import datetime
from database import DB_PATH, get_log_details
from logger import get_logger

logger = get_logger(__name__)

# Load all logs with timestamp from all tables
def load_all_logs() -> list[dict]:
    """Load all logs from every source table.

    Returns a list of dictionaries with the keys ``source``,
    ``table``, ``id`` and ``timestamp``. Logs are sorted by
    timestamp. Errors encountered during database access are
    logged and result in an empty list being returned.
    """
    logs: list[dict] = []
    sources = {
        "email_logs": "Email",
        "phone_logs": "Phone",
        "radio_logs": "Radio",
        "everbridge_logs": "Everbridge",
    }
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            for table, label in sources.items():
                c.execute(f"SELECT id, timestamp FROM {table}")
                rows = c.fetchall()
                for row_id, timestamp in rows:
                    logs.append(
                        {
                            "source": label,
                            "table": table,
                            "id": row_id,
                            "timestamp": timestamp,
                        }
                    )
        logs.sort(key=lambda x: x["timestamp"])
        return logs
    except Exception:
        logger.exception("Failed to load logs from database")
        return []

# Create a new event chain
def create_event_chain(title: str, description: str = "") -> int:
    """Create a new event chain and return its ID."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute(
                """
                INSERT INTO event_chains (title, description, created_at)
                VALUES (?, ?, ?)
                """,
                (title, description, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            )
            event_id = c.lastrowid
        logger.info("Created new event chain '%s' with id %s", title, event_id)
        return event_id
    except Exception:
        logger.exception("Failed to create event chain '%s'", title)
        raise

# Link a log to an event chain
def link_log_to_event(event_id: int, table: str, source_id: int, timestamp: str) -> None:
    """Link a log entry to an event chain."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute(
                """
                INSERT INTO event_links (event_id, source_table, source_id, timestamp)
                VALUES (?, ?, ?, ?)
                """,
                (event_id, table, source_id, timestamp),
            )
        logger.info(
            "Linked log id %s from %s to event chain %s", source_id, table, event_id
        )
    except Exception:
        logger.exception(
            "Failed to link log id %s from %s to event chain %s", source_id, table, event_id
        )
        raise

# Get all existing event chains
def get_event_chains() -> list[dict]:
    """Return a list of existing event chains sorted by creation date."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute(
                "SELECT id, title, created_at FROM event_chains ORDER BY created_at DESC"
            )
            results = c.fetchall()
            return [
                {"id": r[0], "title": r[1], "created_at": r[2]} for r in results
            ]
    except Exception:
        logger.exception("Failed to load event chains")
        return []

# Get all logs linked to a specific chain
def get_event_chain_logs(event_id: int) -> list[tuple[str, int, str]]:
    """Return a list of (table, source_id, timestamp) entries for an event chain."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute(
                """
                SELECT source_table, source_id, timestamp
                FROM event_links
                WHERE event_id = ?
                ORDER BY timestamp
                """,
                (event_id,),
            )
            return c.fetchall()
    except Exception:
        logger.exception("Failed to get logs for event chain %s", event_id)
        return []

# Get summary of a log by source_table and id
def get_log_summary(table: str, log_id: int) -> str:
    """Return a concise summary string for a given log entry.

    If the log does not exist, a placeholder string is returned.
    """
    details = get_log_details(table, log_id)
    if not details:
        return "(No summary available)"

    try:
        if table == "email_logs":
            return f"{details.get('log_type', 'Email')}: {details.get('subject', 'No subject')}"
        elif table == "phone_logs":
            caller = details.get('caller_name', 'Unknown')
            call_type = details.get('call_type', 'Phone')
            site_code = details.get('site_code')
            return (
                f"{call_type} from {caller} - Site {site_code}"
                if site_code
                else f"{call_type} from {caller}"
            )
        elif table == "radio_logs":
            return f"{details.get('unit', 'Unit')} - {details.get('reason', 'Unknown reason')}"
        elif table == "everbridge_logs":
            message = details.get('message', '') or ''
            return (message[:50] + "...") if len(message) > 50 else message
        else:
            return "(Unknown log type)"
    except Exception:
        logger.exception("Failed to summarize log id %s from %s", log_id, table)
        return "(Summary unavailable)"

# Update event chain (for editing)
def update_event_chain(event_id: int, title: str, description: str) -> None:
    """Update the title and description of an existing event chain."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute(
                """
                UPDATE event_chains
                SET title = ?, description = ?
                WHERE id = ?
                """,
                (title, description, event_id),
            )
        logger.info("Updated event chain %s", event_id)
    except Exception:
        logger.exception("Failed to update event chain %s", event_id)
        raise