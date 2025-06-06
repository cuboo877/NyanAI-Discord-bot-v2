import asyncio
from discord.ext import commands
from helper.history_sql_helper import HistorySqlHelper
import discord
from datetime import datetime, timedelta, timezone
from typing import Optional
import re
from auto_reply.auto_reply_chat import AutoReplyChat
class AutoReplyTrigger:
    _last_user_time: Optional[datetime] = None  # 最後一則使用者訊息時間
    _last_user_message: Optional[discord.Message] = None
    _auto_mode = False
    _auto_reply_time: Optional[datetime] = None  # 最後一次 auto_reply 的時間
    _bot = None

    @classmethod
    def got_message(cls, message: discord.Message, bot: commands.Bot):
        # 只處理非 bot 訊息，刷新資料跟狀態
        if message.author == bot.user:
            return
        cls._last_user_time = datetime.now(timezone.utc)
        cls._last_user_message = message
        cls._bot = bot

    @classmethod
    def user_replied(cls):
        print("用戶回應")
        # 用戶回應後，更新最後使用者訊息時間
        cls._last_user_time = datetime.now(timezone.utc)

    @classmethod
    async def check_reply_looper(cls):
        async def auto_reply():
            if cls._bot is not None and cls._last_user_message is not None:
                ctx = await cls._bot.get_context(cls._last_user_message)
                await AutoReplyChat.auto_reply_chat(ctx=ctx)
                cls._auto_reply_time = datetime.now(timezone.utc)
                print("已自動回覆，進入自動回覆模式")

        while True:
            await asyncio.sleep(1)
            now = datetime.now(timezone.utc)

            # 狀態(1)：等待5秒沒人回覆就自動回覆
            if not cls._auto_mode:
                if cls._last_user_time and (now - cls._last_user_time) >= timedelta(seconds=5):
                    await auto_reply()
                    cls._auto_mode = True
                if cls._last_user_message is not None and cls._last_user_message.content is not None:
                    await auto_reply()
                    cls._auto_mode = True
                    #我知道這裡不應該，但是我好懶
            # 狀態(2)：自動回覆後10秒內沒人回覆就回到(1)，有回覆就再自動回覆
            else:
                if cls._auto_reply_time:
                    # 10秒內有使用者回覆
                    if cls._last_user_time and cls._last_user_time > cls._auto_reply_time:
                        print("用戶回覆自動回覆，繼續自動回覆")
                        await auto_reply()
                    # 10秒內沒人回覆
                    elif (now - cls._auto_reply_time) >= timedelta(seconds=10):
                        print("10秒內沒人回覆，回到等待狀態")
                        cls._auto_mode = False
                        cls._auto_reply_time = None
                        cls._last_user_time = None
                        cls._last_user_message = None

