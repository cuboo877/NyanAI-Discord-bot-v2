from discord.ext import commands
from utils.chat_outputer import ChatOutput
from utils.gemini_api import request
class Chat(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def chat(self, ctx:commands.Context, user_input:str):
        try:
            async with ctx.message.channel.typing():
                print("request to gemini now")
                response = await request(user_input)
                if response:
                    await ChatOutput(response=response, ctx=ctx).strip_output()
                else:
                    await ctx.send("Error: No response from Gemini API")
        except Exception as e:
            await ctx.send(f"Error: {e}")

async def setup(bot:commands.Bot):
    await bot.add_cog(Chat(bot=bot))