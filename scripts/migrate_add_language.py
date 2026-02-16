#!/usr/bin/env python3
"""
Add language column to employees table.
"""
import asyncio
import sys
import sqlite3
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.config import settings


def migrate():
    """Add language column to employees table."""
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
        # Check if column already exists
        cursor.execute("PRAGMA table_info(employees)")
        columns = [col[1] for col in cursor.fetchall()]

        if "language" not in columns:
            print("Adding 'language' column to employees table...")
            cursor.execute(
                "ALTER TABLE employees ADD COLUMN language VARCHAR(2) DEFAULT 'ru'"
            )
            conn.commit()
            print("✓ Migration completed successfully!")
        else:
            print("✓ Column 'language' already exists. Skipping migration.")

    except Exception as e:
        print(f"✗ Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
