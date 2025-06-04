import aiosqlite
import discord
from discord.ext import commands
import tiktoken
from typing import Optional

class HistoryPackage:
    def __init__(self, messages):
        # messages 是 tuple: (id, channelId, author, time, content)
        self.id = messages[0]
        self.channel_id = messages[1]
        self.author = messages[2]
        self.time = messages[3]
        self.content = messages[4]

class MemorySqlHelper:
    def __init__(self):
        self._path = "chat_history.db"

    async def init_db(self):           
        try:
            async with aiosqlite.connect(self._path) as db:
                await db.execute(
                    '''
                    CREATE TABLE IF NOT EXISTS Dm(
                        id BIGINT PRIMARY KEY
                    )
                    '''
                )
                await db.execute(
                    '''
                    CREATE TABLE IF NOT EXISTS Dm_Message (
                        id BIGINT PRIMARY KEY,
                        dmId BIGINT,
                        author TEXT,
                        time TEXT,
                        content TEXT,
                        FOREIGN KEY (dmId) REFERENCES Dm(id)
                    )
                    '''
                )
                await db.execute(
                    '''
                    CREATE TABLE IF NOT EXISTS Server (
                        id BIGINT PRIMARY KEY,
                        name TEXT
                    )
                    '''
                )
                await db.execute(
                    '''
                    CREATE TABLE IF NOT EXISTS Channel (
                        id BIGINT PRIMARY KEY,
                        serverId BIGINT,
                        name TEXT,
                        FOREIGN KEY (serverId) REFERENCES Server(id)
                    )
                    '''
                )
                await db.execute(
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

    async def add_message(self, msg:discord.Message):
        try:
            if msg.guild and isinstance(msg.channel, discord.TextChannel): #位於伺服器頻道且為文字頻道
                _server_id = msg.guild.id
                _server_name = str(msg.guild.name)
                _channel_id = msg.channel.id
                _channel_name = str(msg.channel.name)
                _msg_id = msg.id
                _author = str(msg.author.display_name)
                _time = msg.created_at
                _content = str(msg.content)
                async with aiosqlite.connect(self._path) as db:
                    await db.execute(
                        '''
                        INSERT OR IGNORE INTO Server(id,name) Values(?, ?)
                        ''',
                        (_server_id,_server_name)
                    )
                    
                    await db.execute(
                        '''
                        INSERT OR IGNORE INTO Channel(id,name) Values(?, ?)
                        ''',
                        (_channel_id,_channel_name)
                    )
                    
                    await db.execute(
                        '''
                        INSERT OR IGNORE INTO Message(id,ChannelId,author,time,content) Values(?, ?, ?, ?, ?)
                        ''',
                        (_msg_id,_channel_id,_author,_time,_content)
                    )
                    await db.commit()
            else:
                _msg_id = msg.id
                _dm_id = msg.channel.id
                _author = str(msg.author.display_name)
                _time = msg.created_at
                _content = msg.content
                async with aiosqlite.connect(self._path) as db:
                    await db.execute(
                        '''
                        INSERT OR IGNORE INTO Dm(id) Values(?)
                        ''',
                        (_dm_id,)
                    )
                    
                    await db.execute(
                        '''
                        INSERT OR IGNORE INTO Dm_Message(id,dmId,author,time,content) Values(?, ?, ?, ?, ?)
                        ''',
                        (_msg_id, _dm_id, _author, _time, _content)
                    )
                    
                    await db.commit()
        except Exception as e:
            print(f"Error adding message: {e}")

    async def add_message_raw(self, _server_id:Optional[int],_server_name:Optional[str], _channel_id, _channel_name:Optional[str], _msg_id, _author, _time, _content):
        #原始訊息添加的方式
        try:
            async with aiosqlite.connect(self._path) as db:
                await db.execute(
                    '''
                    INSERT OR IGNORE INTO Server(id,name) Values(?, ?)
                    ''',
                    (_server_id,_server_name)
                )
                
                await db.execute(
                    '''
                    INSERT OR IGNORE INTO Channel(id,name) Values(?, ?)
                    ''',
                    (_channel_id,_channel_name)
                )
                
                await db.execute(
                    '''
                    INSERT OR IGNORE INTO Message(id,ChannelId,author,time,content) Values(?, ?, ?, ?, ?)
                    ''',
                    (_msg_id,_channel_id,_author,_time,_content)
                )
                await db.commit()
        except Exception as e:
            print(f"Error adding message: {e}")
    
    async def get_history_list(self, channel_id: int, limit: int = 100):
        try:
            async with aiosqlite.connect(self._path) as db:
                cursor = await db.execute(
                    '''
                    SELECT * FROM Message WHERE ChannelId = ? ORDER BY time DESC LIMIT ?
                    ''',
                    (channel_id, limit)
                )
                rows = await cursor.fetchall()
                result = []
                for row in rows:
                    result.append(HistoryPackage(messages=row))
                return result
        except Exception as e:
            print(e)
            return []
        
    async def reset(self):
        try:
            async with aiosqlite.connect(self._path) as db:
                await db.execute(
                    '''
                    DROP TABLE FROM Server, Channel, Message, Dm, Dm_Message;
                    '''
                )
                await db.commit()
        except Exception as e:
            print(e)