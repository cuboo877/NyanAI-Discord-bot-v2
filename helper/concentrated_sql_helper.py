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
    
    _path = "concentrated_memory.db"

    @classmethod
    async def init_db(cls):
        try:
            async with aiosqlite.connect(cls._path) as db:
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
    @classmethod
    async def add_memory(cls, ctx:commands.Context,content: Optional[str] = None):
        try:
            async with aiosqlite.connect(cls._path) as db:
                await db.execute(
                    '''
                    INSERT INTO Memory(channelId, time, content) VALUES (?, ?, ?)
                    ''',
                    (ctx.channel.id, ctx.message.created_at, content)
                )
                await db.commit()
        except Exception as e:
            print(f"Error adding memory: {e}")
    @classmethod
    async def get_memory_list(cls, channel_id: int, limit: int = 100):
        try:
            async with aiosqlite.connect(cls._path) as db:
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
    @classmethod
    async def clear_concentrated(cls, channel_id: int):
        try:
            async with aiosqlite.connect(cls._path) as db:
                await db.execute(
                    '''
                    DELETE FROM Memory WHERE channelId = ?
                    ''',
                    (channel_id,)
                )
                await db.commit()
        except Exception as e:
            print(f"Error clearing concentrated memory: {e}")
    @classmethod
    async def reset(cls):
        try:
            async with aiosqlite.connect(cls._path) as db:
                await db.execute(
                    '''
                    DROP TABLE IF EXISTS Memory;
                    '''
                )
                await db.commit()
        except Exception as e:
            print(f"Error resetting database: {e}")