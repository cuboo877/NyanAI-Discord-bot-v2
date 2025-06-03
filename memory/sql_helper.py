import aiosqlite
import discord
from discord.ext import commands
from typing import Optional
class SqlHelper:
    
    @classmethod
    async def init_db(cls):           
        async with aiosqlite.connect("chat_history.db") as db:
            await db.execute(
                '''
                CREATE TABLE IF NOT EXISTS Dm(
                    id BIGINT PRIMARY KEY
                );
                
                CREATE TABLE IF NOT EXISTS Dm_Message (
                    id BIGINT PRIMARY KEY,
                    dmId BIGINT,
                    author TEXT,
                    time TEXT,
                    content TEXT,
                    FOREIGN KEY (dmId) REFERENCES Dm(id)
                );
                
                CREATE TABLE IF NOT EXISTS Server (
                    id BIGINT PRIMARY KEY,
                    name TEXT
                );

                CREATE TABLE IF NOT EXISTS Channel (
                    id BIGINT PRIMARY KEY,
                    serverId BIGINT,
                    FOREIGN KEY (serverId) REFERENCES Server(id)
                );

                CREATE TABLE IF NOT EXISTS Message (
                    id BIGINT PRIMARY KEY,
                    channelId BIGINT,
                    author TEXT,
                    time TEXT,
                    content TEXT,
                    FOREIGN KEY (channelId) REFERENCES Channel(id)
                );
                '''
            )
            await db.commit()

    @classmethod
    async def add(cls, msg:discord.Message):
        
        if msg.guild and isinstance(msg.channel, discord.TextChannel): #位於伺服器頻道且為文字頻道
            _server_id = msg.guild.id
            _server_name = msg.guild.name
            _channel_id = msg.channel.id
            _channel_name = msg.channel.name
            _msg_id = msg.id
            _author = msg.author
            _time = msg.created_at
            _content = msg.content
            async with aiosqlite.connect("chat_history.db") as db:
                await db.execute(
                    f'''
                    INSERT OR IGNORE INTO Server(id,name) Values({_server_id},{_server_name})
                    '''
                    f'''
                    INSERT OR IGNORE INTO Channel(id,name) Values({_channel_id},{_channel_name})
                    '''
                    f'''
                    INSERT OR IGNORE INTO Message(id,ChannelId,author,time,content) Values({msg.id},{_channel_id},{_author},{_time},{_content})
                    '''
                )
                await db.commit()
        else:
            _msg_id = msg.id
            _dm_id = msg.channel.id
            _author = msg.author
            _time = msg.created_at
            _content = msg.content
            async with aiosqlite.connect("chat_history.db") as db:
                await db.execute(
                    f'''
                    INSERT OR IGNORE INTO Dm(id) Values({_dm_id})
                    '''
                    f'''
                    INSERT OR IGNORE INTO Dm_Message(id,dmId,author,time,content) Values({msg.id},{_dm_id},{_author},{_time},{_content})
                    '''
                )
                await db.commit()
            