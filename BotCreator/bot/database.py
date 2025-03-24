import aiosqlite
from datetime import datetime
from config import DATABASE_NAME
import logging

logger = logging.getLogger(__name__)

class DatabaseHandler:
    def __init__(self, db_path: str = DATABASE_NAME):
        self.db_path = db_path

    async def create_tables(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''CREATE TABLE IF NOT EXISTS users (
                                user_id INTEGER PRIMARY KEY,
                                token TEXT UNIQUE,
                                description TEXT,
                                avatar_url TEXT,
                                created_at TIMESTAMP)''')
            await db.commit()

    async def user_exists(self, user_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
            return await cursor.fetchone() is not None

    async def add_user(self, user_id: int, token: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("INSERT INTO users (user_id, token, created_at) VALUES (?, ?, ?)",
                          (user_id, token, datetime.now()))
            await db.commit()

    async def update_description(self, user_id: int, description: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("UPDATE users SET description = ? WHERE user_id = ?",
                          (description, user_id))
            await db.commit()