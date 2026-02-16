import json
import asyncio
import sqlite3
import aiosqlite
from typing import Optional, Dict, Any
from aiogram.fsm.storage.base import BaseStorage, StorageKey
from aiogram.fsm.state import State


class SQLiteStorage(BaseStorage):
    """SQLite-based FSM storage for Aiogram 3.x with improved concurrency handling."""

    # Connection timeout in seconds
    DB_TIMEOUT = 30.0
    # Maximum retry attempts for locked database
    MAX_RETRIES = 3
    # Base delay for retries (exponential backoff)
    RETRY_BASE_DELAY = 0.1

    def __init__(self, db_path: str = "./hrbot.db"):
        self.db_path = db_path
        self._conn: Optional[aiosqlite.Connection] = None

    async def _get_conn(self) -> aiosqlite.Connection:
        """Get or create database connection with WAL mode and extended timeout."""
        if self._conn is None:
            self._conn = await aiosqlite.connect(self.db_path, timeout=self.DB_TIMEOUT)
            # Enable WAL mode for better concurrency
            await self._conn.execute("PRAGMA journal_mode=WAL")
            # Set busy timeout for this connection
            await self._conn.execute(f"PRAGMA busy_timeout={int(self.DB_TIMEOUT * 1000)}")
            await self._init_table()
        return self._conn

    async def _init_table(self) -> None:
        """Initialize FSM table if not exists."""
        await self._conn.execute("""
            CREATE TABLE IF NOT EXISTS fsm_state (
                chat_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                bot_id INTEGER NOT NULL DEFAULT 1,
                state TEXT,
                data TEXT DEFAULT '{}',
                PRIMARY KEY (chat_id, user_id, bot_id)
            )
        """)
        await self._conn.commit()

    def _get_key_parts(self, key: StorageKey) -> tuple:
        """Extract key parts from StorageKey."""
        return (
            key.chat_id or 0,
            key.user_id or 0,
            key.bot_id or 1
        )

    async def _execute_with_retry(self, operation: str, coro_factory) -> Any:
        """Execute a database operation with retry logic for locked database.
        
        Args:
            operation: Name of the operation for logging purposes
            coro_factory: Callable that returns a coroutine (factory function)
                          This is needed because coroutines cannot be reused after await.
        """
        last_error = None
        for attempt in range(self.MAX_RETRIES):
            try:
                return await coro_factory()
            except sqlite3.OperationalError as e:
                last_error = e
                if "locked" in str(e) and attempt < self.MAX_RETRIES - 1:
                    # Exponential backoff: 0.1s, 0.2s, 0.3s
                    delay = self.RETRY_BASE_DELAY * (attempt + 1)
                    await asyncio.sleep(delay)
                    continue
                raise
        raise last_error

    async def set_state(self, key: StorageKey, state: Optional[State] = None) -> None:
        """Set state for a specific key with retry logic."""
        async def _do_set_state():
            conn = await self._get_conn()
            chat_id, user_id, bot_id = self._get_key_parts(key)
            state_value = state.state if state else None

            # First check if row exists
            cursor = await conn.execute(
                "SELECT 1 FROM fsm_state WHERE chat_id = ? AND user_id = ? AND bot_id = ?",
                (chat_id, user_id, bot_id)
            )
            exists = await cursor.fetchone()

            if exists:
                # Update existing row, preserve data
                await conn.execute("""
                    UPDATE fsm_state SET state = ? WHERE chat_id = ? AND user_id = ? AND bot_id = ?
                """, (state_value, chat_id, user_id, bot_id))
            else:
                # Insert new row
                await conn.execute("""
                    INSERT INTO fsm_state (chat_id, user_id, bot_id, state)
                    VALUES (?, ?, ?, ?)
                """, (chat_id, user_id, bot_id, state_value))
            await conn.commit()

        await self._execute_with_retry("set_state", _do_set_state)

    async def get_state(self, key: StorageKey) -> Optional[State]:
        """Get state for a specific key."""
        conn = await self._get_conn()
        chat_id, user_id, bot_id = self._get_key_parts(key)

        cursor = await conn.execute(
            "SELECT state FROM fsm_state WHERE chat_id = ? AND user_id = ? AND bot_id = ?",
            (chat_id, user_id, bot_id)
        )
        row = await cursor.fetchone()

        if row and row[0]:
            return State(state=row[0])
        return None

    async def set_data(self, key: StorageKey, data: Dict[str, Any]) -> None:
        """Set data for a specific key with retry logic."""
        async def _do_set_data():
            conn = await self._get_conn()
            chat_id, user_id, bot_id = self._get_key_parts(key)
            data_json = json.dumps(data)

            # First check if row exists
            cursor = await conn.execute(
                "SELECT 1 FROM fsm_state WHERE chat_id = ? AND user_id = ? AND bot_id = ?",
                (chat_id, user_id, bot_id)
            )
            exists = await cursor.fetchone()

            if exists:
                # Update existing row, preserve state
                await conn.execute("""
                    UPDATE fsm_state SET data = ? WHERE chat_id = ? AND user_id = ? AND bot_id = ?
                """, (data_json, chat_id, user_id, bot_id))
            else:
                # Insert new row
                await conn.execute("""
                    INSERT INTO fsm_state (chat_id, user_id, bot_id, data)
                    VALUES (?, ?, ?, ?)
                """, (chat_id, user_id, bot_id, data_json))
            await conn.commit()

        await self._execute_with_retry("set_data", _do_set_data)

    async def get_data(self, key: StorageKey) -> Dict[str, Any]:
        """Get data for a specific key."""
        conn = await self._get_conn()
        chat_id, user_id, bot_id = self._get_key_parts(key)

        cursor = await conn.execute(
            "SELECT data FROM fsm_state WHERE chat_id = ? AND user_id = ? AND bot_id = ?",
            (chat_id, user_id, bot_id)
        )
        row = await cursor.fetchone()

        if row and row[0]:
            try:
                return json.loads(row[0])
            except json.JSONDecodeError:
                return {}
        return {}

    async def update_data(self, key: StorageKey, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update data for a specific key."""
        current_data = await self.get_data(key)
        current_data.update(data)
        await self.set_data(key, current_data)
        return current_data

    async def close(self) -> None:
        """Close database connection."""
        if self._conn:
            await self._conn.close()
            self._conn = None
