import tiktoken
from helper.concentrated_sql_helper import ConcentratedSqlHelper
from helper.config_sql_helper import ConfigSQLHelper 
from helper.history_sql_helper import HistorySqlHelper
from discord.ext import commands
from utils.chat_outputer import ChatOutput
from utils.gemini_api import request
from cogs.chat import build_history_prompt

class AutoReplyChat:
    @classmethod
    async def auto_reply_chat(cls, ctx:commands.Context):
        try:
            enc = tiktoken.get_encoding("cl100k_base")
            histories = await HistorySqlHelper.get_history_list(channel_id=ctx.message.channel.id)
            role_prompt = ConfigSQLHelper.default_role_rules
            history_prompt = build_history_prompt(histories, enc, max_tokens=250) #自動回覆需要壓低token使用量
            auto_reply_prompt = ConfigSQLHelper.default_auto_reply_rules
            full_prompt = role_prompt + auto_reply_prompt + "\n" + history_prompt
            
            response = await request(full_prompt)
            if response != "<refuse>":
                await ChatOutput(response=response, ctx=ctx).strip_output()
            else:
                print("以被拒絕自動回覆")
        except Exception as e:
            print(f"Error in auto_reply: {e}")
            
            
    