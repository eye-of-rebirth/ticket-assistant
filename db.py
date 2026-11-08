from pathlib import Path

import sqlite3

def init_db(db_path):
    schema_path = Path(__file__).resolve().parent / "schema.sql"
    sql = schema_path.read_text(encoding="utf-8")
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(sql)
    finally:
        conn.close()

def insert_ticket(db_path, text, status="open"):
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            "INSERT INTO tickets (text, status) VALUES (?, ?)",
            (text, status),
        )
        conn.commit()
    finally:
        conn.close()

def list_tickets(db_path):
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.execute("SELECT id, text, status FROM tickets ORDER BY id")
        rows = cursor.fetchall()
        return rows
    finally:
        conn.close()