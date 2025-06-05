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
load_dotenv()
#--------------
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
token = os.getenv('discord-token')
if not token:
    raise ValueError("找不到 Discord token，請確認 .env 檔案有設定 'discord-token'")


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')
    print(f'Bot is in {len(bot.guilds)} guilds')
    for guild in bot.guilds:
        print(f'- {guild.name} (id: {guild.id})')
    # 啟動自動回覆判斷的背景任務

    bot.loop.create_task(AutoReplyTrigger.check_reply_looper())
     
@bot.event
async def on_message(message):
    if message.author == bot.user or message.content.startswith("!"):
        pass  # 不處理 bot 自己或指令
    else:
        AutoReplyTrigger.got_message(message, bot)
        if AutoReplyTrigger._auto_mode:
            AutoReplyTrigger.user_replied()
    await HistorySqlHelper.add_message(message)
    print("added message to memory")
    await bot.process_commands(message)
    
@bot.event
async def on_command_error(ctx, error):
    print(f'Command error: {error}')
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("喵嗚~ 找不到這個指令欸！")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("喵嗚~ 指令參數不夠啦！")
    else:
        await ctx.send(f"喵嗚~ 發生錯誤了：{error}")

async def load_extensions():
    for filename in os.listdir("cogs"):
        if filename.endswith(".py"):
            module_name = f"cogs.{filename[:-3]}"
            try:
                await bot.load_extension(module_name)   
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

