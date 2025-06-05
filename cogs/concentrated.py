from discord.ext import commands
import discord
from helper.concentrated_sql_helper import ConcentratedSqlHelper

class Concentrated(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def concentrated(self, ctx: commands.Context, limit: int = 10):
        try:
            async with ctx.message.channel.typing():
                memories = await ConcentratedSqlHelper().get_memory_list(ctx.channel.id, limit=limit)
                if not memories:
                    await ctx.send("查無濃縮記憶")
                    return

                embed = discord.Embed(title="濃縮記憶", color=discord.Color.purple())
                for m in memories[::-1]:  # 由舊到新
                    embed.add_field(
                        name=f"{m.author} @ {m.time}",
                        value=m.content if m.content else "(無內容)",
                        inline=False
                    )
                await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"Error: {e}")

    @commands.command()
    async def clearconcentrated(self, ctx: commands.Context):
        try:
            memories = await ConcentratedSqlHelper().get_memory_list(ctx.channel.id, limit=1000)
            if not memories:
                await ctx.send("查無濃縮記憶")
                return

            await ctx.send("確定要刪除本頻道所有濃縮記憶嗎？請輸入 yes 以確認，或輸入 cancel 取消。")

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            msg = await ctx.bot.wait_for('message', check=check, timeout=60)
            if msg.content.lower() == "cancel":
                await ctx.send("已取消操作。")
                return
            if msg.content.lower() != "yes":
                await ctx.send("未確認，操作已取消。")
                return


            await ConcentratedSqlHelper().clear_concentrated(ctx.channel.id)
            await ctx.send(f"已完全刪除本頻道所有濃縮記憶。")
        except Exception as e:
            await ctx.send(f"Error: {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(Concentrated(bot=bot))