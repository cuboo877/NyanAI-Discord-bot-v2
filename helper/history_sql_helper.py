import aiosqlite
import discord
from typing import Optional

class HistoryPackage:
    def __init__(self, messages):
        # messages 是 tuple: (id, channelId, author, time, content)
        self.id = messages[0]
        self.channel_id = messages[1]
        self.author = messages[2]
        self.time = messages[3]
        self.content = messages[4]

class HistorySqlHelper:
    _path = "chat_history.db"

    @classmethod
    async def init_db(cls):           
        try:
            async with aiosqlite.connect(cls._path) as db:
                await db.execute(
                    '''
                    CREATE TABLE IF NOT EXISTS Channel (
                        id BIGINT PRIMARY KEY,
                        name TEXT
                    )
                    '''
                )
                await db.execute( # 不用server是因為沒有什麼用處，因為是以頻道來做記憶的
                    '''
                    CREATE TABLE IF NOT EXISTS Message (
                        id BIGINT PRIMARY KEY,
                        channelId BIGINT,
                        author TEXT,
                        time TEXT,
                        content TEXT,
                        FOREIGN KEY (channelId) REFERENCES Channel(id)
                    )
                    '''
                )
                await db.commit()
        except Exception as e:
            print(e)
    @classmethod
    async def add_message(cls, msg:discord.Message):
        try:
            if msg.guild and isinstance(msg.channel, discord.TextChannel): # 位於伺服器頻道且為文字頻道
                _channel_id = msg.channel.id
                _channel_name = str(msg.channel.name)
                _msg_id = msg.id
                _author = str(msg.author.display_name) 
                _time = msg.created_at
                _content = str(msg.content)
                async with aiosqlite.connect(cls._path) as db:
                    await db.execute( #如果沒有在伺服器上(也就是第一次add_message)，不是新增就是不做
                        '''
                        INSERT OR IGNORE INTO Channel(id, name) VALUES(?, ?)
                        ''',
                        (_channel_id, _channel_name)
                    )
                    await db.execute( #一樣
                        '''
                        INSERT OR IGNORE INTO Message(id, channelId, author, time, content) VALUES(?, ?, ?, ?, ?)
                        ''',
                        (_msg_id, _channel_id, _author, _time, _content)
                    )
                    await db.commit()
        except Exception as e:
            print(f"Error adding message: {e}")
            
    @classmethod #limit是訊息限制量
    async def get_history_list(cls, channel_id: int, limit: int = 100):
        try:
            async with aiosqlite.connect(cls._path) as db:
                cursor = await db.execute( 
                    '''
                    SELECT * FROM Message WHERE channelId = ? ORDER BY time DESC LIMIT ?
                    ''',
                    (channel_id, limit)
                ) # fetchall() 回傳的會是tuple: (id, channelId,... )
                rows = await cursor.fetchall()
                result = []
                for row in rows:
                    result.append(HistoryPackage(messages=row)) #這就是為什麼Package是這樣設計的
                return result
        except Exception as e:
            print(e)
            return []
    @classmethod
    async def reset(cls):
        try:
            async with aiosqlite.connect(cls._path) as db:
                await db.execute('DROP TABLE IF EXISTS Channel;')
                await db.execute('DROP TABLE IF EXISTS Message;')
                await db.commit()
        except Exception as e:
            print(e)