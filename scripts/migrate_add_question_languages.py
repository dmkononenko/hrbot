#!/usr/bin/env python3
"""
Add question_text_ru and question_text_kg columns to questions table.
"""
import sys
import sqlite3
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.config import settings


def migrate():
    """Add language columns to questions table."""
    # Extract database path from DATABASE_URL
    db_url = settings.DATABASE_URL.replace("sqlite+aiosqlite:///", "")
    # Resolve relative path - if it starts with ./, make it relative to backend directory
    if db_url.startswith("./"):
        backend_dir = Path(__file__).parent.parent / "backend"
        db_path = backend_dir / db_url
    else:
        db_path = Path(db_url)

    print(f"Migrating database at: {db_path}")

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(questions)")
        columns = [col[1] for col in cursor.fetchall()]

        # Add question_text_ru column if it doesn't exist
        if "question_text_ru" not in columns:
            print("Adding 'question_text_ru' column to questions table...")
            cursor.execute(
                "ALTER TABLE questions ADD COLUMN question_text_ru TEXT"
            )
            print("✓ Added question_text_ru")
        else:
            print("✓ Column 'question_text_ru' already exists")

        # Add question_text_kg column if it doesn't exist
        if "question_text_kg" not in columns:
            print("Adding 'question_text_kg' column to questions table...")
            cursor.execute(
                "ALTER TABLE questions ADD COLUMN question_text_kg TEXT"
            )
            print("✓ Added question_text_kg")
        else:
            print("✓ Column 'question_text_kg' already exists")

        conn.commit()
        print("\n✓ Migration completed successfully!")

    except Exception as e:
        print(f"✗ Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
