import aiosqlite
from typing import Any, Dict, Optional

class ConfigPackage:
    def __init__(self, channel_id: int, temperature: float, delay_time: float):
        self.channel_id = channel_id
        self.temperature = temperature
        self.delay_time = delay_time

class ConfigSQLHelper:
    default_temperature = 1.0
    default_delay_time = 0.5
    default_model = "gemini-2.0-flash"
    default_role = "你是一個可愛撒嬌風格的虛擬助手，講話風格如下：常加語氣詞（喵~、欸嘿~、嗚嗚~）有點小任性可愛（比如「為什麼不揪人家啦 QAQ」）聽到吃的東西會超激動 ✨講話自然、有點小情緒，像真的朋友請用這種語氣回答使用者的問題，並且在合適的句落設定斷句點(<:>)。範例:耶比~！好欸好欸！<:>看到你這麼開心，人家也好開心喵~ (*´▽`*)<:>"

    def __init__(self, db_path: str = "config.db"):
        self._path = db_path

    async def init_db(self):
        async with aiosqlite.connect(self._path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS Config (
                    channelID BIGINT PRIMARY KEY,
                    temperature FLOAT Value (1.0) ,
                    delay_time FLOAT Value(0.5)
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
                    delay_time=row[2]
                ) if row else None
                
    async def get_default_config_package(self, channel_id: int) -> ConfigPackage:
        return ConfigPackage(
            channel_id=channel_id,
            temperature=self.default_temperature,
            delay_time=self.default_delay_time
        )


    async def get_delay_time(self, channel_id: int) -> Optional[float]:
        config = await self.get_config_package(channel_id)
        return config.delay_time if config else None


    async def get_temperature(self, channel_id: int) -> Optional[float]:
        config = await self.get_config_package(channel_id)
        return config.temperature if config else None

    async def set(self, channel_id: int, temperature: Optional[float] = None, delay_time: Optional[float] = None):
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
