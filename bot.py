import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio
from helper.config_sql_helper import ConfigSQLHelper
from helper.history_sql_helper import HistorySqlHelper
from helper.concentrated_sql_helper import ConcentratedSqlHelper
from datetime import datetime
from auto_reply.auto_reply_trigger import AutoReplyTrigger

load_dotenv() #從.env拿資料
#--------------
intents = discord.Intents.all() 
bot = commands.Bot(command_prefix="!", intents=intents)
token = os.getenv('discord-token')
if not token: #基本可以無視，保險token錯誤
    raise ValueError("無discord bot token! 請檢查.env!")


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')
    print(f'Bot is in {len(bot.guilds)} guilds')
    for guild in bot.guilds: #說機器人在哪個伺服器裡(所有)
        print(f'- {guild.name} (id: {guild.id})')
    
    # 背景執行AutoReplyTrigger
    bot.loop.create_task(AutoReplyTrigger.check_reply_looper())
     
@bot.event
async def on_message(message):
    if message.author == bot.user or message.content.startswith("!"):
        pass  # 不處理 bot 自己或指令
    else: # 因為要透過使用者的訊息來啟動AutoReply
        AutoReplyTrigger.got_message(message, bot) #得到訊息，刷新狀態
        if AutoReplyTrigger._auto_mode: #如果在自動模式
            AutoReplyTrigger.user_replied() #(得到使用者訊息+在自動模式) -> 代表使用者回覆了自動回覆，繼續自動回覆
    await HistorySqlHelper.add_message(message)
    print("added message to memory")
    await bot.process_commands(message) #一定要加這行才能判斷!指令
    
@bot.event
async def on_command_error(ctx, error): # 單純提醒錯誤指令
    print(f'Command error: {error}')
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("喵嗚~ 找不到這個指令欸！")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("喵嗚~ 指令參數不夠啦！")
    else:
        await ctx.send(f"喵嗚~ 發生錯誤了：{error}")

async def load_extensions(): # 載入cog模組
    for filename in os.listdir("cogs"):
        if filename.endswith(".py"):
            module_name = f"cogs.{filename[:-3]}"
            try:
                await bot.load_extension(module_name)   #discord api只要他的名稱
                print(f"✅ Loaded extension: {module_name}")
            except Exception as e:
                print(f"❌ Failed to load {module_name}: {e}")

async def main():
    # 先初始化資料庫
    await ConcentratedSqlHelper.init_db()
    await ConfigSQLHelper.init_db()
    await HistorySqlHelper.init_db()
    print("initialized sql")
    async with bot:
        await load_extensions()
        await bot.start(token=token) #type: ignore

asyncio.run(main())

