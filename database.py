"""
Research History Database using SQLite.
Saves every research query and result for history viewing.
"""

import sqlite3
import json
import os
from datetime import datetime

# Use /tmp/ for both Azure and Hugging Face (writable directory)
DB_PATH = os.getenv("DB_PATH", "/tmp/research_history.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS research_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            answer TEXT NOT NULL,
            sources TEXT NOT NULL,
            queries TEXT NOT NULL,
            num_sources INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_research(topic: str, answer: str, sources: list, queries: list) -> int:
    conn = get_connection()
    cursor = conn.execute(
        """INSERT INTO research_history
           (topic, answer, sources, queries, num_sources, created_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (
            topic,
            answer,
            json.dumps(sources),
            json.dumps(queries),
            len(sources),
            datetime.now().strftime("%Y-%m-%d %H:%M"),
        ),
    )
    conn.commit()
    record_id = cursor.lastrowid
    conn.close()
    return record_id


def get_history(limit: int = 20) -> list:
    conn = get_connection()
    rows = conn.execute(
        """SELECT id, topic, num_sources, created_at
           FROM research_history
           ORDER BY id DESC LIMIT ?""",
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_research_by_id(record_id: int) -> dict:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM research_history WHERE id = ?",
        (record_id,),
    ).fetchone()
    conn.close()
    if row:
        result = dict(row)
        result["sources"] = json.loads(result["sources"])
        result["queries"] = json.loads(result["queries"])
        return result
    return {}


def delete_research(record_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM research_history WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()


# Initialize database on import
init_db()
