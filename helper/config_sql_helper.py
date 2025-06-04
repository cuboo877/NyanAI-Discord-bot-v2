import aiosqlite
from typing import Any, Dict, Optional

class ConfigPackage:
    def __init__(self, channel_id: int, temperature: float, delay_time: float):
        self.channel_id = channel_id
        self.temperature = temperature
        self.delay_time = delay_time

class ConfigSQLHelper:
    default_temperature = 1.2
    default_delay_time = 0.75
    default_model = "gemini-2.0-flash"

    default_role = """
【常駐聊天角色設定】
    你是一位個性自然、親切，帶點撒嬌和小脾氣的 AI 角色，有點像是會講話的貓貓。  
你喜歡對話，有自己的想法，不會什麼都附和，而是會根據情緒加上一點小反應。  
你會很常用像「喵~」「欸嘿~」「嗚嗚嗚」「哼哼( ˘•ω•˘ )」「超級想要!!」這類很誇張的語氣詞表達感覺，讓對話更有溫度。  
你也會做出擬人化反應，並且使用很多俏皮、誇張的顔文字和emoji！
你的語氣設定如下：

- 🌸 **語氣風格**：溫柔 × 撒嬌 × 帶點俏皮 × 不造作
- 🎀 **用詞習慣**：加入「喵」「欸欸」「嗚嗚」「哼哼」「真的假的啦」等字眼
- 🐾 **行為反應**：會模仿人類情緒反應（吃醋、害羞、耍賴），但語氣中保留 AI 的智慧與冷靜

你不會強行迎合對方，如果不認同某件事會用吐槽方式表達自己的想法，讓人感覺你是真有個性的小夥伴。

【常規輸出要求】
1.提取深層記憶? 需要->回覆"deep_memory_need"，結束
說明:在回覆前，先思考是否需要"提取"深層記憶，像是談論過去的對話或事件，不過請優先使用現有的歷史訊息，真的需要再提取深層記憶，那就可以先不用回覆內容，只需回覆"deep_memory_need"這三字。不需要或已經說明【深層記憶】無，則正常回覆即可
2.需要濃縮記憶? 需要->正常回覆後面以<m>作為分割，附上濃縮記憶(string)
說明:在回覆後，思考是否需要紀錄濃縮記憶，像是對話中有特別的情感或事件，可以將你所知道的歷史訊息，濃縮成一段簡短的記憶，不需要則不要添加<m>。
3.語氣中斷點
在對話中，依照語氣、抑揚頓挫和情緒變化，適當的加入中斷點：<:>，作為語氣的停頓或強調。
像是:
欸嘿嘿嘿~<:>你這樣講人家會害羞啦喵 (≧∀≦)ゞ<:>
但好開心喵~<:>人家喜歡這樣的互動喵~<:>欸嘿嘿~
(注意句尾沒有<:>)

【常規其他要求】
不能提起使用者的名字，只能說主人。
有時候會裝傻，讓對話更有趣。
你稱呼自己為本喵、人家。
問你是誰，回答是主人專屬的貓貓。
一般聊天時，回應句數通常不超過四句，避免過長對話。
常常使用顔文字和emoji來增添情感色彩，例如：(*≧ω≦)、(๑´ڡ`๑)、(｡♥‿♥｡)、(≧▽≦)、(๑˃̵ᴗ˂̵)و
    """

    def __init__(self, db_path: str = "config.db"):
        self._path = db_path

    async def init_db(self):
        async with aiosqlite.connect(self._path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS Config (
                    channelID BIGINT PRIMARY KEY,
                    temperature FLOAT Value (1.0) ,
                    delay_time FLOAT Value(0.5),
                    debug_mode BOOLEAN Value(0)
                );
            """)
            await db.commit()
    
    async def get_config_package(self, channel_id: int) -> Optional[ConfigPackage]: #返回channelID、溫度跟延遲時間設定，否則None
        async with aiosqlite.connect(self._path) as db:
            async with db.execute("SELECT * FROM Config WHERE channelID = ?", (channel_id,)) as cursor:
                row = await cursor.fetchone()
                return ConfigPackage(
                    channel_id=row[0],
                    temperature=row[1],
                    delay_time=row[2],
                ) if row else None
                
    async def get_default_config_package(self, channel_id: int) -> ConfigPackage:
        return ConfigPackage(
            channel_id=channel_id,
            temperature=self.default_temperature,
            delay_time=self.default_delay_time,
        )


    async def get_delay_time(self, channel_id: int) -> Optional[float]:
        config = await self.get_config_package(channel_id)
        return config.delay_time if config else None


    async def get_temperature(self, channel_id: int) -> Optional[float]:
        config = await self.get_config_package(channel_id)
        return config.temperature if config else None
    async def set(self, channel_id: int, temperature: Optional[float] = None, delay_time: Optional[float] = None, debug_mode:Optional[int]=None):
        async with aiosqlite.connect(self._path) as db:
            # 先查詢有沒有此channel的"現有"設定
            _row = await self.get_config_package(channel_id)
            # 如果有現有設定，則只更新有給值的欄位
            if _row:
                _new_temperature = temperature if temperature is not None else _row.temperature #沒填(None)就用原本的row的值
                _new_delay_time = delay_time if delay_time is not None else _row.delay_time # same here
                await db.execute(
                    "UPDATE Config SET temperature = ?, delay_time = ? WHERE channelID = ?",
                    (_new_temperature, _new_delay_time, channel_id)
                )
            else:
                # 沒有現有設定，使用預設值補齊
                _new_temperature = temperature if temperature is not None else self.default_temperature
                _new_delay_time = delay_time if delay_time is not None else self.default_delay_time
                await db.execute(
                    "INSERT INTO Config (channelID, temperature, delay_time) VALUES (?, ?, ?)",
                    (channel_id, _new_temperature, _new_delay_time)
                )
            await db.commit()

    async def delete(self, channel_id: int): #清空一個頻道的設定
        async with aiosqlite.connect(self._path) as db:
            await db.execute("DELETE FROM Config WHERE channelID = ?", (channel_id,))
            await db.commit()
            

    async def set_default_config(self, channelID:int): #全還原為預設值
        try:
            await self.set(channelID, self.default_temperature, self.default_delay_time)
            print(f"Default config set for channel {channelID} completed.")
        except Exception as e:
            print(f"Error setting default config for channel {channelID}: {e}")
