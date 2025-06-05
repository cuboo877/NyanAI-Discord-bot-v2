from discord.ext import commands
from helper.config_sql_helper import ConfigSQLHelper
from helper.history_sql_helper import HistorySqlHelper
from utils.chat_outputer import ChatOutput
from utils.gemini_api import request
from helper.concentrated_sql_helper import ConcentratedSqlHelper
import tiktoken

def build_history_prompt(histories, enc, max_tokens=2500):
    history_prompt = "【歷史對話】"
    total_tokens = 0
    for h in histories:
        time = h.time
        author = h.author
        content = h.content
        content_tokens = len(enc.encode(content))
        if total_tokens + content_tokens > max_tokens:
            break
        history_prompt += f"\n[{time}] {author}: {content}"
        total_tokens += content_tokens
    return history_prompt

class Chat(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def chat(self, ctx:commands.Context, user_input:str):
        try:
            async with ctx.message.channel.typing():
                enc = tiktoken.get_encoding("cl100k_base")
                histories = await HistorySqlHelper.get_history_list(channel_id=ctx.message.channel.id)
                role_prompt = ConfigSQLHelper.default_role_rules
                output_prompt = ConfigSQLHelper.default_output_rules
                history_prompt = build_history_prompt(histories, enc)
                full_prompt = role_prompt + output_prompt + "\n" + "【用戶主動對話】" + user_input + history_prompt
                print("原始prompt:", full_prompt)
                response = await request(full_prompt) #第一次請求
                if response:
                    if "<concentrated_memory>" == response:
                        print("Concentrated memory requested")
                        memories = await ConcentratedSqlHelper.get_memory_list(channel_id=ctx.channel.id)
                        if memories:
                            history_prompt += f"\n【濃縮記憶】\n"
                            for mem in memories:
                                history_prompt += f"{mem.time}:\n{mem.content}"
                        response = await request(role_prompt + "\n" + "【用戶主動對話】" + user_input + history_prompt)
                        print(role_prompt + "\n" + "【用戶主動對話】" + user_input + history_prompt)
                        #TODO等等刪掉
                    await ChatOutput(response=response, ctx=ctx).strip_output()
                    print("Prepare to send response")
                    print("最終原始回應:", response)
                else:
                    await ctx.send("Error: No response from Gemini API")
        except Exception as e:
            await ctx.send(f"Error: {e}")
        
async def setup(bot:commands.Bot):
    await bot.add_cog(Chat(bot=bot))