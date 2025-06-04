import discord
from discord.ext import commands
from helper.config_sql_helper import ConfigSQLHelper
from utils.info_getter import InfoGetterByCtx
class Setting(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        print("Setting cog initialized")

    @commands.group(invoke_without_command=True)
    async def set(self, ctx:commands.Context):
        print(f"Set command invoked by {ctx.author.name}")
        embed = discord.Embed(
            title="⚙️ Nyan 設定指令教學",
            description="使用 `!set` 指令來修改 Nyan 的基礎參數設定喵~\n包含延遲時間、模型選擇、創造力等等！",
            color=0xf5d400
        )

        embed.add_field(
            name="📘 `!set`",
            value="顯示所有可用設定指令與說明 ✨",
            inline=True
        )

        embed.add_field(
            name="⏱️ `!set delay <數字>`",
            value="設定 Nyan 回覆訊息的 **延遲時間**\n👉 數字格式：`1.5`、`3`\n👉 單位：**秒**",
            inline=False
        )

        embed.add_field(
            name="🔥 `!set temperature <0~2>`",
            value="設定 AI 回應的 **創造力溫度**\n👉 範圍：`0`（穩定）～ `2`（瘋狂）\n建議值：`0.7 ~ 1.3`",
            inline=False
        )

        embed.add_field(
            name="♻️ `!set default`",
            value="重設所有設定為預設值（喵嗚~回到原點！）",
            inline=False
        )

        embed.set_footer(
            text= InfoGetterByCtx.get_channel_name(ctx),
        )

        try:
            await ctx.send(embed=embed)
            print("Set command executed successfully")
        except Exception as e:
            print(f"Error in set command: {e}")
            await ctx.send("喵嗚~ 發生錯誤了！")

    @set.command()
    async def delay(self, ctx:commands.Context, value:float):
        print(f"Set delay command invoked with value={value}")
        try:
            if await ConfigSQLHelper().set(channel_id=ctx.channel.id, delay_time=value):
                await ctx.send(embed=discord.Embed(
                    title="設定成功喵~ ✨",
                    description=f"已將延遲時間設定為 **{value}** 秒",
                    color=0xf5d400
                ))
        except Exception as e:
            print(f"Error in delay command: {e}")
            await ctx.send(embed=discord.Embed(
                title="輸入格式錯誤啦！",
                description="請輸入正確的數字格式喵~",
                color=0xf5d400
            ))

    @set.command()
    async def temp(self, ctx:commands.Context, value:float):
        try:
            if await ConfigSQLHelper().set(channel_id=ctx.channel.id, temperature=value):
                await ctx.send(embed=discord.Embed(
                    title="設定成功喵~ ✨",
                    description=f"已將創造力溫度設定為 **{value}**",
                    color=0xf5d400
                ))
            print(f"Set temperature command invoked with value={value}")
            
        except Exception as e:
            print(f"Error in temperature command: {e}")
            await ctx.send(embed=discord.Embed(
                title="輸入格式錯誤啦！",
                description="請輸入正確的數字格式喵~",
                color=0xf5d400
            ))

    @set.command()
    async def default(self, ctx:commands.Context):
        print("Set default command invoked")
        try:
            await ConfigSQLHelper().set_default_config(channelID=ctx.channel.id)
            await ctx.send(embed=discord.Embed(
            title="設定已重置喵~ ✨",
            description="所有設定都已恢復為預設值！",
            color=0xf5d400
            ))
        except Exception as e:
            print(f"Error in default command: {e}")
            await ctx.send(embed=discord.Embed(
                title="重設失敗喵！",
                description="請稍後再試或聯繫管理員喵~",
                color=0xf5d400
            ))
        

async def setup(bot:commands.Bot):
    print("Setting cog setup started")
    await bot.add_cog(Setting(bot))
    print("Setting cog setup completed")
