#!/usr/bin/env python3
"""
Migration script to add gender and age fields to employees table.
Run this script to update existing database schema.
"""
import asyncio
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from sqlalchemy import text
from app.database import engine
from app.config import settings


async def migrate():
    """Add new columns to employees table."""
    print(f"Connecting to database: {settings.DATABASE_URL}")

    async with engine.begin() as conn:
        # Get existing columns using sqlite_master
        result = await conn.execute(text("""
            SELECT sql
            FROM sqlite_master
            WHERE type='table' AND name='employees'
        """))
        table_sql = result.scalar_one_or_none()

        existing_columns = set()
        if table_sql:
            # Parse column names from CREATE TABLE statement
            import re
            columns = re.findall(r'"(\w+)"\s+', table_sql)
            existing_columns = set(columns)

        print(f"Existing columns: {existing_columns}")

        # Add gender column if not exists
        if 'gender' not in existing_columns:
            print("Adding 'gender' column...")
            await conn.execute(text("""
                ALTER TABLE employees
                ADD COLUMN gender VARCHAR(10)
            """))
            print("  - Column 'gender' added")
        else:
            print("  - Column 'gender' already exists")

        # Add age column if not exists
        if 'age' not in existing_columns:
            print("Adding 'age' column...")
            await conn.execute(text("""
                ALTER TABLE employees
                ADD COLUMN age INTEGER
            """))
            print("  - Column 'age' added")
        else:
            print("  - Column 'age' already exists")

    print("\nMigration completed successfully!")
    print("\nNew fields added to employees table:")
    print("  - gender (VARCHAR(10)) - Пол (male, female, other)")
    print("  - age (INTEGER) - Возраст")


if __name__ == "__main__":
    asyncio.run(migrate())
