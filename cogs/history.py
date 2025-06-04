from discord.ext import commands
import discord
from helper.memory_sql_helper import MemorySqlHelper

class History(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def history(self, ctx: commands.Context, limit: int = 10):
        try:
            async with ctx.message.channel.typing():
                histories = await MemorySqlHelper().get_history_list(ctx.channel.id, limit=limit)
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
            histories = await MemorySqlHelper().get_history_list(ctx.channel.id, limit=1000)
            if not histories:
                await ctx.send("查無歷史訊息")
                return

            await ctx.send("確定要刪除本頻道所有歷史訊息嗎？請輸入 yes 以確認，或輸入 cancel 取消。")

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            msg = await ctx.bot.wait_for('message', check=check, timeout=60)
            if msg.content.lower() == "cancel":
                await ctx.send("已取消操作。")
                return
            if msg.content.lower() != "yes":
                await ctx.send("未確認，操作已取消。")
                return

            await ctx.send(f"已完全刪除本頻道所有歷史訊息。")
        except Exception as e:
            await ctx.send(f"Error: {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(History(bot=bot))