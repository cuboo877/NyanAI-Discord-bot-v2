import discord
from discord.ext import commands
from utils.config_controller import ConfigController
import asyncio


class ChatOutput:
    def __init__(self, response:str, ctx:commands.Context):
        self.ctx = ctx
        self.response = response

    async def strip_output(self):
        delay_time = ConfigController.get(key="delay-time", default=1)
        segment = [s.strip() for s in self.response.split("<:>") if s.strip()]
        for part in segment:
            await self.ctx.send(part)
            await asyncio.sleep(delay_time)
        print('Sent all the stripping response')