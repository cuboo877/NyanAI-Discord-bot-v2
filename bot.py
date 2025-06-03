import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio
from utils.config_controller import ConfigController
from memory.sql_helper import SqlHelper
load_dotenv()
#--------------
ConfigController.load()
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
token = os.getenv('discord-token')

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')
    print(f'Bot is in {len(bot.guilds)} guilds')
    for guild in bot.guilds:
        print(f'- {guild.name} (id: {guild.id})')

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
    for filename in os.listdir("NyanAI\cogs"): # type: ignore
        if filename.endswith(".py"):
            module_name = f"cogs.{filename[:-3]}"
            try:
                await bot.load_extension(module_name)
                print(f"✅ Loaded extension: {module_name}")
            except Exception as e:
                print(f"❌ Failed to load {module_name}: {e}")

async def main():
    async with bot:
        await load_extensions()
        await bot.start(token=token) # type: ignore
        await SqlHelper.init_db()

asyncio.run(main())