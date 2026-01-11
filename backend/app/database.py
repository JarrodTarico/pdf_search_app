import sqlite3
from datetime import datetime
from typing import Optional
from contextlib import contextmanager

DATABASE_PATH = "pdf_search.db"


def get_connection() -> sqlite3.Connection:
    """Get a database connection with row factory."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def get_db():
    """Context manager for database connections."""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    """Initialize the database with required tables."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pdfs (
                id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                text_content TEXT NOT NULL,
                upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                file_size INTEGER NOT NULL
            )
        """)


def insert_pdf(pdf_id: str, filename: str, text_content: str, file_size: int) -> None:
    """Insert a new PDF record into the database."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO pdfs (id, filename, text_content, file_size) VALUES (?, ?, ?, ?)",
            (pdf_id, filename, text_content, file_size)
        )


def get_pdf_by_id(pdf_id: str) -> Optional[dict]:
    """Get a PDF record by its ID."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pdfs WHERE id = ?", (pdf_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None


def get_all_pdfs() -> list[dict]:
    """Get all PDF records from the database."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pdfs")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def delete_pdf(pdf_id: str) -> bool:
    """Delete a PDF record by its ID."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pdfs WHERE id = ?", (pdf_id,))
        return cursor.rowcount > 0
