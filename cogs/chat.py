from discord.ext import commands
from helper.config_sql_helper import ConfigSQLHelper
from helper.history_sql_helper import HistorySqlHelper
from utils.chat_outputer import ChatOutput
from utils.gemini_api import chat_request
from helper.memory_sql_helper import MemorySqlHelper
import tiktoken
class Chat(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def chat(self, ctx:commands.Context, user_input:str):
        try:
            async with ctx.message.channel.typing():
                enc = tiktoken.get_encoding("cl100k_base")
                histories = await HistorySqlHelper().get_history_list(channel_id=ctx.message.channel.id)
                role_prompt = ConfigSQLHelper().default_role
                full_prompt = role_prompt + "\n" + "【用戶主動對話】" + user_input + "【歷史對話】"
                total_tokens = 0
                for h in histories:
                    time = h.time
                    author = h.author
                    content = h.content
                    if total_tokens + len(enc.encode(content)) > 3000:
                        break
                    full_prompt += f"\n[{time}] {author}: {content}"
                    total_tokens += len(enc.encode(content))
                response = await chat_request(full_prompt)
                if response:
                    if response == "deep_memory_need":
                        print("Deep memory requested")
                        memories = await MemorySqlHelper().get_memory_list(channel_id=ctx.channel.id)
                        if not memories:
                            full_prompt += "\n【深度記憶】無"
                        else:
                            full_prompt += f"\n【深度記憶】\n"
                            for mem in memories:
                                full_prompt += f"{mem.author} @ {mem.time}:\n{mem.content}"
                        response = await chat_request(full_prompt)
                        print("another new request")
                    else:
                        await ChatOutput(response=response, ctx=ctx).strip_output()
                else:
                    await ctx.send("Error: No response from Gemini API")
        except Exception as e:
            await ctx.send(f"Error: {e}")

async def setup(bot:commands.Bot):
    await bot.add_cog(Chat(bot=bot))