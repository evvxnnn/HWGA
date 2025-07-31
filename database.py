"""
Database utilities for the Security Ops Logger.

This module provides initialization and CRUD helper functions for
the underlying SQLite database. Connections are managed using
context managers to ensure proper cleanup and commits. Errors
encountered during database operations are logged via the
``logger`` module.
"""

import sqlite3
import os
from datetime import datetime

from logger import get_logger

# Compute the path to the SQLite database. Storing the database
# within the ``data`` folder keeps user data separate from source
# code. Consumers of this module should not modify ``DB_PATH``
# directly; instead configure the ``data`` directory externally if
# necessary.
DB_PATH = os.path.join("data", "ops_logger.db")

# Set up a module-level logger. Using ``__name__`` means this
# logger will be namespaced under ``database`` when written to
# file. Handlers are added lazily by ``get_logger``.
logger = get_logger(__name__)

def init_db() -> None:
    """Initialize the SQLite database and create required tables.

    This function uses a context manager to open a connection
    and create tables if they do not already exist. Any errors
    encountered are logged, but re-raised to notify callers.
    """
    try:
        # Ensure the data directory exists
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()

            # Email logs table
            c.execute(
                """
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
                """
            )

            # Phone call logs table
            c.execute(
                """
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
                """
            )

            # Radio logs table
            c.execute(
                """
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
                """
            )

            # Everbridge alerts table
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS everbridge_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    site_code TEXT,
                    message TEXT,
                    timestamp TEXT,
                    created_at TEXT
                )
                """
            )

            # Event chains table
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS event_chains (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    description TEXT,
                    created_at TEXT
                )
                """
            )

            # Event links table
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS event_links (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id INTEGER,
                    source_table TEXT,
                    source_id INTEGER,
                    timestamp TEXT,
                    FOREIGN KEY (event_id) REFERENCES event_chains(id)
                )
                """
            )
            # Create indexes to speed up common queries. Indexes on timestamp
            # columns and foreign keys improve lookups and sorting when
            # retrieving large volumes of logs or linking events. These
            # statements are idempotent – SQLite will only create the
            # index if it does not already exist.
            c.execute(
                "CREATE INDEX IF NOT EXISTS idx_email_logs_timestamp ON email_logs(timestamp)"
            )
            c.execute(
                "CREATE INDEX IF NOT EXISTS idx_phone_logs_timestamp ON phone_logs(timestamp)"
            )
            c.execute(
                "CREATE INDEX IF NOT EXISTS idx_radio_logs_timestamp ON radio_logs(timestamp)"
            )
            c.execute(
                "CREATE INDEX IF NOT EXISTS idx_everbridge_logs_timestamp ON everbridge_logs(timestamp)"
            )
            c.execute(
                "CREATE INDEX IF NOT EXISTS idx_event_links_event_id ON event_links(event_id)"
            )

            # Commit occurs automatically on context exit
            logger.info("Database initialized successfully and indexes created")
    except Exception as exc:
        logger.exception("Failed to initialize database")
        raise

# Email insert already exists
def insert_email_log(
    log_type: str,
    sender: str | None,
    recipient: str | None,
    subject: str | None,
    timestamp: str,
    extra_field: str | None,
    msg_path: str,
) -> None:
    """Insert a new email log into the database.

    Parameters
    ----------
    log_type: str
        The selected type of email (e.g., ``Data Request``).
    sender: str or None
        The email sender if provided, else ``None``.
    recipient: str or None
        The recipient or contact name if applicable.
    subject: str or None
        The email subject line, if known.
    timestamp: str
        The date/time the email was sent or received.
    extra_field: str or None
        Additional information captured from dynamic fields.
    msg_path: str
        The original path to the .msg file or ``"Manual Entry"``.
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute(
                """
                INSERT INTO email_logs (
                    log_type, sender, recipient, subject, timestamp,
                    extra_field, msg_path, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    log_type,
                    sender,
                    recipient,
                    subject,
                    timestamp,
                    extra_field,
                    msg_path,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ),
            )
        logger.info("Inserted email log of type '%s'", log_type)
    except Exception:
        logger.exception("Failed to insert email log")
        raise

def insert_phone_log(
    call_type: str,
    caller_name: str | None,
    site_code: str | None,
    ticket_number: str | None,
    address: str | None,
    alarm_type: str | None,
    issue_type: str | None,
    issue_subtype: str | None,
    message: str | None,
    timestamp: str,
) -> None:
    """Insert a new phone call log into the database."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute(
                """
                INSERT INTO phone_logs (
                    call_type, caller_name, site_code, ticket_number, address,
                    alarm_type, issue_type, issue_subtype, message, timestamp, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    call_type,
                    caller_name,
                    site_code,
                    ticket_number,
                    address,
                    alarm_type,
                    issue_type,
                    issue_subtype,
                    message,
                    timestamp,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ),
            )
        logger.info("Inserted phone log of type '%s'", call_type)
    except Exception:
        logger.exception("Failed to insert phone log")
        raise

def insert_radio_log(
    unit: str,
    location: str,
    reason: str,
    arrived: bool,
    departed: bool,
    timestamp: str,
) -> None:
    """Insert a new radio dispatch log into the database."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute(
                """
                INSERT INTO radio_logs (
                    unit, location, reason, arrived, departed, timestamp, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    unit,
                    location,
                    reason,
                    int(arrived),
                    int(departed),
                    timestamp,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ),
            )
        logger.info("Inserted radio log for unit '%s'", unit)
    except Exception:
        logger.exception("Failed to insert radio log")
        raise

def insert_everbridge_log(
    site_code: str,
    message: str,
    timestamp: str,
) -> None:
    """Insert a new Everbridge alert log into the database."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute(
                """
                INSERT INTO everbridge_logs (
                    site_code, message, timestamp, created_at
                ) VALUES (?, ?, ?, ?)
                """,
                (
                    site_code,
                    message,
                    timestamp,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ),
            )
        logger.info("Inserted Everbridge log for site '%s'", site_code)
    except Exception:
        logger.exception("Failed to insert Everbridge log")
        raise

# New helper function to get log details (for the improved Event Manager)
def get_log_details(table: str, log_id: int) -> dict | None:
    """Retrieve all column values for a specific log entry.

    This helper queries the given table for the row matching
    ``log_id`` and returns a dictionary keyed by column names. If
    the row does not exist or an error occurs, ``None`` is
    returned.

    Parameters
    ----------
    table: str
        The name of the table to query (e.g., ``'email_logs'``).
    log_id: int
        The primary key of the log entry.

    Returns
    -------
    dict or None
        A mapping of column names to values, or ``None`` if the
        entry cannot be found.
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            # Configure row factory to return rows as dictionaries
            conn.row_factory = sqlite3.Row
            c = conn.cursor()

            # Ensure the requested table exists by checking its info
            c.execute(f"PRAGMA table_info({table})")
            columns_info = c.fetchall()
            if not columns_info:
                logger.warning("Table '%s' does not exist", table)
                return None
            columns = [col[1] for col in columns_info]

            c.execute(f"SELECT * FROM {table} WHERE id = ?", (log_id,))
            row = c.fetchone()
            if row:
                # ``row`` acts like a mapping thanks to row_factory
                return {col: row[col] for col in columns}
            return None
    except Exception:
        logger.exception("Failed to get log details for table '%s' id %s", table, log_id)
        return None


def export_table_to_csv(table: str, dest_path: str) -> None:
    """Export all records from a given table into a CSV file.

    This utility function writes the contents of an entire table
    to a comma-separated values (CSV) file. Column headers are
    included as the first row. If the table contains no data,
    the destination file will be created with only the header row.

    Parameters
    ----------
    table: str
        The table name to export (e.g., ``'email_logs'``).
    dest_path: str
        The filesystem path where the CSV should be written.
    """
    try:
        import csv  # Imported here to avoid unnecessary dependency at module import time
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            # Verify table exists
            c.execute(f"PRAGMA table_info({table})")
            columns_info = c.fetchall()
            if not columns_info:
                logger.warning("Table '%s' does not exist; skipping export", table)
                return
            c.execute(f"SELECT * FROM {table}")
            rows = c.fetchall()
            # Open destination file for writing
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            with open(dest_path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                # Write header
                header = [col[1] for col in columns_info]
                writer.writerow(header)
                # Write each row
                for row in rows:
                    writer.writerow([row[col] for col in header])
        logger.info("Exported %d records from table '%s' to %s", len(rows), table, dest_path)
    except Exception:
        logger.exception("Failed to export table '%s' to CSV", table)
        raise