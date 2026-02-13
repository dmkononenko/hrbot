#!/usr/bin/env python3
"""
Migration script to add branch, department, and position fields to employees table.
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
        # Check if columns already exist
        result = await conn.execute(text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'employees'
            AND column_name IN ('branch', 'department', 'position')
        """))
        existing_columns = {row[0] for row in result}

        # Add branch column if not exists
        if 'branch' not in existing_columns:
            print("Adding 'branch' column...")
            await conn.execute(text("""
                ALTER TABLE employees
                ADD COLUMN branch VARCHAR(255)
            """))
            print("  - Column 'branch' added")
        else:
            print("  - Column 'branch' already exists")

        # Add department column if not exists
        if 'department' not in existing_columns:
            print("Adding 'department' column...")
            await conn.execute(text("""
                ALTER TABLE employees
                ADD COLUMN department VARCHAR(255)
            """))
            print("  - Column 'department' added")
        else:
            print("  - Column 'department' already exists")

        # Add position column if not exists
        if 'position' not in existing_columns:
            print("Adding 'position' column...")
            await conn.execute(text("""
                ALTER TABLE employees
                ADD COLUMN position VARCHAR(255)
            """))
            print("  - Column 'position' added")
        else:
            print("  - Column 'position' already exists")

    print("\nMigration completed successfully!")
    print("\nNew fields added to employees table:")
    print("  - branch (VARCHAR(255)) - Филиал")
    print("  - department (VARCHAR(255)) - Департамент")
    print("  - position (VARCHAR(255)) - Должность")


if __name__ == "__main__":
    asyncio.run(migrate())
