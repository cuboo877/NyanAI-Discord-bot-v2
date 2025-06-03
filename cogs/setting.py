import discord
from discord.ext import commands
from utils.config_controller import ConfigController
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
            name="🧠 `!set model <模型名稱>`",
            value="指定使用的 AI 模型\n預設為：`gemini-1.5-pro`\n你也可以換成自己部署的模型名稱喵！",
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
            text= InfoGetterByCtx.get_server_name,
            icon_url= InfoGetterByCtx.get_server_icon_url
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
            if ConfigController.edit(key="delay-time", value=value):
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
    async def model(self, ctx:commands.Context, value:str):
        print(f"Set model command invoked with value={value}")
        if ConfigController.edit(key="model", value=value):
            await ctx.send(embed=discord.Embed(
                title="設定成功喵~ ✨",
                description=f"已將模型設定為 **{value}**",
                color=0xf5d400
            ))

    @set.command()
    async def temperature(self, ctx:commands.Context, value:float):
        print(f"Set temperature command invoked with value={value}")
        try:
            if ConfigController.edit(key="temperature", value=value):
                await ctx.send(embed=discord.Embed(
                    title="設定成功喵~ ✨",
                    description=f"已將創造力溫度設定為 **{value}**",
                    color=0xf5d400
                ))
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
        default_config = {
            "role": "你是一個可愛撒嬌風格的虛擬助手，講話風格如下：常加語氣詞（喵~、欸嘿~、嗚嗚~）有點小任性可愛（比如「為什麼不揪人家啦 QAQ」）聽到吃的東西會超激動 ✨講話自然、有點小情緒，像真的朋友請用這種語氣回答使用者的問題，並且在合適的句落設定斷句點(<:>)。範例:耶比~！好欸好欸！<:>看到你這麼開心，人家也好開心喵~ (*´▽`*) 快點快點~<:>有什麼有趣的事情要跟人家說，或是想問人家問題嗎？<:>不要讓人等太久啦，不然人家會孤單寂寞覺得冷的嗚嗚... ( TДT)<:>",
            "temperature": 1.5,
            "delay-time": 1,
            "model": "gemini-2.0-flash"
        }
        
        for key, value in default_config.items():
            ConfigController.edit(key=key, value=value)
        
        await ctx.send(embed=discord.Embed(
            title="設定已重置喵~ ✨",
            description="所有設定都已恢復為預設值！",
            color=0xf5d400
        ))

async def setup(bot:commands.Bot):
    print("Setting cog setup started")
    await bot.add_cog(Setting(bot))
    print("Setting cog setup completed")
