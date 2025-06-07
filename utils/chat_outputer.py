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
        
    @classmethod
    async def strip_output(cls):
        try:
            async with cls.ctx.channel.typing():
                if "<m>" in cls.response: #如果回覆有濃縮記憶，就分割並處裡
                    content = cls.response.split("<m>")[0] #回覆內容
                    memory = cls.response.split("<m>")[1] #記憶
                    await ConcentratedSqlHelper.add_memory(
                        ctx=cls.ctx, content=memory
                    )  # 新增濃縮記憶至concentrated.db
                else:
                    content = cls.response #沒有<m>就整個都是回覆就對了
                
                _config = await ConfigSQLHelper().get_config_package(channel_id=cls.ctx.channel.id) #得到此頻道的設定(已經包好了)
                if _config is None: #找不到設定就使用預設
                    _config = await ConfigSQLHelper().get_default_config_package(channel_id=cls.ctx.channel.id)
                segment = [s.strip() for s in content.split("<:>")]
                for part in segment: #斷句點分割
                    if(part.strip()): #怕是純space
                        await cls.ctx.send(part)
                        await asyncio.sleep(_config.delay_time) #關鍵的延遲
                print('Sent all the stripping response')
        except Exception as e:
            print(f"Error in ChatOutput.strip_output: {e}")
            await cls.ctx.send(embed=discord.Embed(
                title="發生錯誤喵！",
                description="請稍後再試或聯繫管理員喵~",
                color=0xf5d400
            ))