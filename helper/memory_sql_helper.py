import aiosqlite
from typing import Optional

class MemoryPackage:
    def __init__(self, memory):
        # memory 是 tuple: (id, channelId, author, time, content)
        self.id = memory[0]
        self.channel_id = memory[1]
        self.author = memory[2]
        self.time = memory[3]
        self.content = memory[4]

class MemorySqlHelper:
    def __init__(self):
        self._path = "deep_memory.db"

    async def init_db(self):
        try:
            async with aiosqlite.connect(self._path) as db:
                await db.execute(
                    '''
                    CREATE TABLE IF NOT EXISTS Memory (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        channelId BIGINT,
                        author TEXT,
                        time TEXT,
                        content TEXT
                    )
                    '''
                )
                await db.commit()
        except Exception as e:
            print(f"Error initializing database: {e}")

    async def add_memory(self, channel_id: int, author: str, time, content: str):
        try:
            async with aiosqlite.connect(self._path) as db:
                await db.execute(
                    '''
                    INSERT INTO Memory(channelId, author, time, content) VALUES (?, ?, ?, ?)
                    ''',
                    (channel_id, author, time, content)
                )
                await db.commit()
        except Exception as e:
            print(f"Error adding memory: {e}")

    async def get_memory_list(self, channel_id: int, limit: int = 100):
        try:
            async with aiosqlite.connect(self._path) as db:
                cursor = await db.execute(
                    '''
                    SELECT * FROM Memory WHERE channelId = ? ORDER BY time DESC LIMIT ?
                    ''',
                    (channel_id, limit)
                )
                rows = await cursor.fetchall()
                result = []
                for row in rows:
                    result.append(MemoryPackage(memory=row))
                return result
        except Exception as e:
            print(f"Error getting memory list: {e}")
            return []

    async def reset(self):
        try:
            async with aiosqlite.connect(self._path) as db:
                await db.execute(
                    '''
                    DROP TABLE IF EXISTS Memory;
                    '''
                )
                await db.commit()
        except Exception as e:
            print(f"Error resetting database: {e}")