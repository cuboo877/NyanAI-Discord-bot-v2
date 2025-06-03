import discord
from discord.ext import commands


class InfoGetterByMsg:
    @classmethod
    async def get_server_name(cls, msg:discord.Message):
        if msg.guild:
            return msg.guild.name
        return "私訊"
    
    @classmethod
    async def get_server_id(cls, msg:discord.Message):
        if msg.guild:
            return msg.guild.id
        return None
    
    @classmethod
    async def get_channel_id(cls, msg:discord.Message):
        if msg.channel:
            return msg.channel.id
        return None
    
# Pylance認為這個name屬性有None的可能，因為頻道有分語音與文字頻道，name只有文字頻道能存取，因此要自己加上判斷
#   @classmethod
#    async def get_channel_name(cls, ctx:discord.Message):
 #       if ctx.channel.name:
  #          return ctx.channel.id
   #     return None
   
    @classmethod
    async def get_channel_name(cls, msg:discord.Message):
        if isinstance(msg.channel, discord.TextChannel):
            return msg.channel.name
        return None
    
    @classmethod
    async def get_author(cls, msg:discord.Message):
        if msg.author:
            return msg.author
        return None
    
    @classmethod
    async def get_time(cls, msg:discord.Message):
        if msg.content:
            return msg.author 
        return None
    
class InfoGetterByCtx:
    @classmethod
    async def get_server_name(cls, ctx:commands.Context):
        if ctx.guild:
            return ctx.guild.name
        return "私訊"
    
    @classmethod
    async def get_server_id(cls, ctx:commands.Context):
        if ctx.guild:
            return ctx.guild.id
        return None
    
    @classmethod
    async def get_server_icon_url(cls, ctx:commands.Context):
        if ctx.guild:
            return ctx.guild.icon
        return None
    
    @classmethod
    async def get_channel_id(cls, ctx:commands.Context):
        if ctx.channel:
            return ctx.channel.id
        return None
    
# Pylance認為這個name屬性有None的可能，因為頻道有分語音與文字頻道，name只有文字頻道能存取，因此要自己加上判斷
#   @classmethod
#    async def get_channel_name(cls, ctx:discord.Message):
 #       if ctx.channel.name:
  #          return ctx.channel.id
   #     return None

    @classmethod    
    async def get_channel_name(cls, ctx:commands.Context): #使用isinstance判斷ctx頻道是不是文字頻道
        if isinstance(ctx.channel, discord.TextChannel): #isistance(object, class)
            return ctx.channel.name 
        return None
    
    @classmethod
    async def get_author(cls, ctx:commands.Context):
        if ctx.author:
            return ctx.author
        return None
