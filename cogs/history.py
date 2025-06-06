from discord.ext import commands
import discord
from helper.history_sql_helper import HistorySqlHelper

class History(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def history(self, ctx: commands.Context, limit: int = 10):
        try:
            async with ctx.message.channel.typing():
                histories = await HistorySqlHelper.get_history_list(ctx.channel.id, limit=limit)
                if not histories:
                    await ctx.send("查無歷史訊息")
                    return

                embed = discord.Embed(title="歷史訊息", color=discord.Color.blue())
                for h in histories[::-1]:  # 由舊到新
                    # 每則訊息顯示作者與內容
                    embed.add_field(
                        name=f"{h.author} @ {h.time}",
                        value=h.content if h.content else "(無內容)",
                        inline=False
                    )
                await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"Error: {e}")

    @commands.command()
    async def clearhistory(self, ctx: commands.Context):
        try:
            histories = await HistorySqlHelper.get_history_list(ctx.channel.id, limit=1000)
            if not histories:
                await ctx.send("查無歷史訊息")
                return

            embed = discord.Embed(title="刪除此頻道歷史訊息完成拉喵~", color=discord.Color.blue())
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"Error: {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(History(bot=bot))