"""
Database setup using SQLite.
Handles users and mission logs.
"""

import sqlite3
import os

DB_PATH = os.getenv("DB_PATH", "/workspace/backend/gcs.db")


def get_connection():
    """Get a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'viewer'
        )
    """)

    # Mission logs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mission_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            username TEXT NOT NULL,
            action TEXT NOT NULL,
            details TEXT,
            result TEXT
        )
    """)

    conn.commit()
    conn.close()
    print("Database initialised.")


def log_mission(username: str, action: str, details: str, result: str):
    """Save a command to the mission log."""
    from datetime import datetime

    conn = get_connection()
    conn.execute(
        """INSERT INTO mission_logs 
           (timestamp, username, action, details, result)
           VALUES (?, ?, ?, ?, ?)""",
        (datetime.utcnow().isoformat(), username, action, details, result),
    )
    conn.commit()
    conn.close()
