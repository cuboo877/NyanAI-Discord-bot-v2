import discord
from discord.ext import commands
from helper.config_sql_helper import ConfigSQLHelper
import asyncio


class ChatOutput:
    @classmethod
    def __init__(cls, response:str, ctx:commands.Context):
        cls.ctx = ctx
        cls.response = response
        
    @classmethod
    async def strip_output(cls):
        try:
            _config = await ConfigSQLHelper().get_config_package(channel_id=cls.ctx.channel.id)
            if _config is None:
                _config = await ConfigSQLHelper().get_default_config_package(channel_id=cls.ctx.channel.id)
            segment = [s.strip() for s in cls.response.split("<:>") if s.strip()]
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