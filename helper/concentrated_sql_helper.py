import aiosqlite
from typing import Optional
from discord.ext import commands

class ConcentratedPackage:
    def __init__(self, memory):
        # memory 是 tuple: (id, channelId, time, content)
        self.id = memory[0]
        self.channel_id = memory[1]
        self.time = memory[2]
        self.content = memory[3]

class ConcentratedSqlHelper:
    def __init__(self):
        self._path = "concentrated_memory.db"

    async def init_db(self):
        try:
            async with aiosqlite.connect(self._path) as db:
                await db.execute(
                    '''
                    CREATE TABLE IF NOT EXISTS Memory (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        channelId BIGINT,
                        time TEXT,
                        content TEXT
                    )
                    '''
                )
                await db.commit()
        except Exception as e:
            print(f"Error initializing database: {e}")

    async def add_memory(self, ctx:commands.Context,content: Optional[str] = None):
        try:
            async with aiosqlite.connect(self._path) as db:
                await db.execute(
                    '''
                    INSERT INTO Memory(channelId, time, content) VALUES (?, ?, ?)
                    ''',
                    (ctx.channel.id, ctx.message.created_at, content)
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
                    result.append(ConcentratedPackage(memory=row))
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