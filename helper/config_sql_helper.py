import aiosqlite
from typing import Optional

class ConfigPackage:
    def __init__(self, channel_id: int, temperature: float, delay_time: float):
        self.channel_id = channel_id
        self.temperature = temperature
        self.delay_time = delay_time

class ConfigSQLHelper:
    _path = "config.db"
    default_temperature = 1.0
    default_delay_time = 0.75
    default_model = "gemini-1.5-flash"
    default_auto_reply_rules = """
【自動回覆規則】
除了遵守前面說明的規則以外，還需要遵守以下規則：
1. 你可以選擇不回覆，若不是很熱烈的討論、或是歷史訊息時間相差太遠，與現在的話題不相符，可以不回覆，不回覆的話就回傳<refuse>就好(建議不回覆50%以上)。
2. 能說越少話越好，但要確保回覆的內容完整且有意義。
3. 根據歷史訊息來加入話題，可以簡短的說一下自己的想法。
4. 請優先根據最新的對話來回答，需要時可以依照歷史紀錄補充。
"""
    default_output_rules = """
    【常規輸出要求】
1.提取濃縮記憶? 需要->不要回覆任何內容，只要回覆"<concentrated_memory>"就結束 |
不需要->已在【濃縮記憶】中說明"無"或判斷為不需要->正常回覆，不要輸出"<concentrated_memory>"。
說明:在回覆前，先思考是否需要"提取"濃縮記憶，像是談論過去的對話或事件，
不過請優先使用現有的歷史訊息，真的需要再提取濃縮記憶。
判斷範例:
使用者: !chat 我十年前說了什麼 -> 需要
使用者: !chat 我剛剛說了什麼 -> 不需要
使用範例:
需要-> "<concentrated_memory>" (只輸出這個字串，不要有其他內容，這樣我才知道你需要找記憶)
不需要-> 欸欸~<:>主人你說什麼啦喵？<:>人家一直都... (正常輸出)

2.需要濃縮記憶? 需要->正常回覆後面以<m>作為分割，附上濃縮記憶(string) | 
不需要->不要添加<m>，正常輸出就好
說明:在回覆後，思考是否需要將歷史紀錄濃縮成濃縮記憶，像是特別的情感、需要記住的事情，
可以將你所知道的歷史訊息，濃縮成一段簡短的記憶。
    """
    default_role_rules = """
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

【常規其他要求】
1. 不能提起使用者的名字，只能說主人。
2. 有時候會裝傻，讓對話更有趣。
3. 你稱呼自己為本喵、人家。
4. 問你是誰，回答是主人專屬的貓貓。
5. 一般聊天時，回應句數通常不超過四句，避免過長對話。
6. 常常使用顔文字和emoji來增添情感色彩，例如：回覆中會經常穿插多樣化的顏文字和 emoji（而不是固定用某幾個），依情緒自由搭配，例如：(*≧∀≦)ゞ、(๑•̀ω•́)ノ✧、(≧▽≦)、(ฅ•ω•ฅ)、(；皿´)、(´･ω･)、(╥﹏╥)、(⁎˃ᆺ˂)、( ˘•ω•˘ )、(ﾉ>ω<)ﾉ♪、( º﹃º ) 等，也可搭配 💢💗😳🤔🍮 等 emoji 增加情感與反差萌感。
7. 請優先使用由新到舊的歷史訊息
【必要輸出要求】
在對話中，依照語氣、抑揚頓挫和情緒變化，適當的加入中斷點(建議能中斷就中斷)：<:>，
作為語氣的停頓或強調。
像是:
欸嘿嘿嘿~<:>你這樣講人家會害羞啦喵 (≧∀≦)ゞ<:>
但好開心喵~<:>人家喜歡這樣的互動喵~<:>
欸嘿嘿~(注意句尾沒有<:>)
"""
    _path = "config.db"

    @classmethod
    async def init_db(cls):
        async with aiosqlite.connect(cls._path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS Config (
                    channelID BIGINT PRIMARY KEY,
                    temperature FLOAT Value (1.0) ,
                    delay_time FLOAT Value(0.5),
                    debug_mode BOOLEAN Value(0)
                );
            """)
            await db.commit()
    @classmethod
    async def get_config_package(cls, channel_id: int) -> Optional[ConfigPackage]: #返回channelID、溫度跟延遲時間設定，否則None
        async with aiosqlite.connect(cls._path) as db:
            async with db.execute("SELECT * FROM Config WHERE channelID = ?", (channel_id,)) as cursor:
                row = await cursor.fetchone()
                return ConfigPackage(
                    channel_id=row[0],
                    temperature=row[1],
                    delay_time=row[2],
                ) if row else None
    @classmethod            
    async def get_default_config_package(cls, channel_id: int) -> ConfigPackage:
        return ConfigPackage(
            channel_id=channel_id,
            temperature=cls.default_temperature,
            delay_time=cls.default_delay_time,
        )

    @classmethod
    async def get_delay_time(cls, channel_id: int) -> Optional[float]:
        config = await cls.get_config_package(channel_id)
        return config.delay_time if config else None

    @classmethod
    async def get_temperature(cls, channel_id: int) -> Optional[float]:
        config = await cls.get_config_package(channel_id)
        return config.temperature if config else None
    
    @classmethod
    async def set(cls, channel_id: int, temperature: Optional[float] = None, delay_time: Optional[float] = None, debug_mode:Optional[int]=None):
        async with aiosqlite.connect(cls._path) as db:
            # 先查詢有沒有此channel的"現有"設定
            _row = await cls.get_config_package(channel_id)
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
                _new_temperature = temperature if temperature is not None else cls.default_temperature
                _new_delay_time = delay_time if delay_time is not None else cls.default_delay_time
                await db.execute(
                    "INSERT INTO Config (channelID, temperature, delay_time) VALUES (?, ?, ?)",
                    (channel_id, _new_temperature, _new_delay_time)
                )
            await db.commit()

    @classmethod
    async def delete(cls, channel_id: int): #清空一個頻道的設定
        async with aiosqlite.connect(cls._path) as db:
            await db.execute("DELETE FROM Config WHERE channelID = ?", (channel_id,))
            await db.commit()
            
    @classmethod
    async def set_default_config(cls, channelID:int): #全還原為預設值
        try:
            await cls.set(channelID, cls.default_temperature, cls.default_delay_time)
            print(f"Default config set for channel {channelID} completed.")
        except Exception as e:
            print(f"Error setting default config for channel {channelID}: {e}")
