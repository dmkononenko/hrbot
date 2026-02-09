#!/usr/bin/env python3
"""
Initialize the HR Bot database.
Creates all tables and indexes.
"""
import asyncio
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.database import init_db
from app.config import settings


async def main():
    """Initialize database tables."""
    print(f"Initializing database at: {settings.DATABASE_URL}")
    await init_db()
    print("Database initialized successfully!")
    print("\nTables created:")
    print("  - employees")
    print("  - surveys")
    print("  - questions")
    print("  - question_options")
    print("  - survey_responses")
    print("  - answers")
    print("\nNext steps:")
    print("  1. Create a .env file with BOT_TOKEN and other settings")
    print("  2. Run: uvicorn app.main:app --reload")
    print("  3. Access API docs at: http://localhost:8000/docs")


if __name__ == "__main__":
    asyncio.run(main())
