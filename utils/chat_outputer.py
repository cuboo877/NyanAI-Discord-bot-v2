import discord
from discord.ext import commands
from helper.config_sql_helper import ConfigSQLHelper
import asyncio
from typing import Optional
from helper.history_sql_helper import HistorySqlHelper
from helper.concentrated_sql_helper import ConcentratedSqlHelper

class ChatOutput:
    @classmethod
    def __init__(cls, response:str, ctx:commands.Context):
        cls.ctx = ctx
        cls.response = response
        cls.content = ""
        cls.deep_memory = Optional[str]  # 用於深度記憶的特殊處理
        
    @classmethod
    async def strip_output(cls):
        try:
            if "<m>" in cls.response:
                cls.content = cls.response.split("<m>")[0]
                cls.deep_memory = cls.response.split("<m>")[1]
                await ConcentratedSqlHelper().add_memory(
                    ctx=cls.ctx, content=cls.deep_memory
                )  # 新增濃縮記憶
            else:
                cls.content = cls.response
            
            _config = await ConfigSQLHelper().get_config_package(channel_id=cls.ctx.channel.id)
            if _config is None:
                _config = await ConfigSQLHelper().get_default_config_package(channel_id=cls.ctx.channel.id)
            segment = [s.strip() for s in cls.content.split("<:>") if s.strip()]
            for part in segment:
                await cls.ctx.send(part)
                await asyncio.sleep(_config.delay_time)
            print('Sent all the stripping response')
        except Exception as e:
            print(f"Error in ChatOutput.strip_output: {e}")
            await cls.ctx.send(embed=discord.Embed(
                title="發生錯誤喵！",
                description="請稍後再試或聯繫管理員喵~",
                color=0xf5d400
            ))