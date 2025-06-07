from discord.ext import commands
from helper.config_sql_helper import ConfigSQLHelper
from helper.history_sql_helper import HistorySqlHelper
from utils.chat_outputer import ChatOutput
from utils.gemini_api import request
from helper.concentrated_sql_helper import ConcentratedSqlHelper
import tiktoken


#建立歷史訊息prompt
def build_history_prompt(histories, max_tokens=2500):
    enc = tiktoken.get_encoding("cl100k_base")
    history_prompt = "【歷史對話】"
    total_tokens = 0 #開始token計算
    for h in histories: 
        time = h.time
        author = h.author
        content = h.content
        content_tokens = len(enc.encode(content))  #內容的token
        if total_tokens + content_tokens > max_tokens: #累計token > 最大限制token
            break #不加歷史訊息了
        history_prompt += f"\n[{time}] {author}: {content}"
        total_tokens += content_tokens
    return history_prompt

class Chat(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def chat(self, ctx:commands.Context, user_input:str):
        try:
            histories = await HistorySqlHelper.get_history_list(channel_id=ctx.message.channel.id)
            role_prompt = ConfigSQLHelper.default_role_rules
            output_prompt = ConfigSQLHelper.default_output_rules
            history_prompt = build_history_prompt(histories)
            #第一次的完整prompt(有請求提取記憶的output_prompt)
            full_prompt = role_prompt + output_prompt + "\n" + "【用戶主動對話】" + user_input + history_prompt
            print("原始prompt:", full_prompt)
            response = await request(full_prompt) #第一次請求
            if response: #如果請求需要記憶，就提取記憶並加回prompt中
                if "<concentrated_memory>" == response:
                    print("Concentrated memory requested")
                    memories = await ConcentratedSqlHelper.get_memory_list(channel_id=ctx.channel.id)
                    if memories: #加回濃縮記憶
                        history_prompt += f"\n【重要摘要】\n"
                        for mem in memories:
                            history_prompt += f"{mem.time}:\n{mem.content}" 
                    #第二次請求就沒有判斷的prompt(因為不需要在判斷一次了，就沒要求了)
                    response = await request(role_prompt + "\n" + "【用戶主動對話】" + user_input + history_prompt)
                    print(role_prompt + "\n" + "【用戶主動對話】" + user_input + history_prompt)
                await ChatOutput(response=response, ctx=ctx).strip_output() #輸出至聊天室
                print("Prepare to send response")
                print("最終原始回應:", response)
            else:
                await ctx.send("Error: No response from Gemini API")
        except Exception as e:
            await ctx.send(f"Error: {e}")
        
async def setup(bot:commands.Bot):
    await bot.add_cog(Chat(bot=bot))