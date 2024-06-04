import asyncio
import os
import logging
import discord
from discord.ext import commands
from dotenv import load_dotenv
from logger import setup_logging

from cogs.greeting_cog import GreetingCog

load_dotenv()
setup_logging()


class BotClient(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_connect(self):
        await self.add_cog(GreetingCog(self))

    async def on_ready(self):
        logging.info(f"Bot client ready. Logged in as {self.user}")

    async def on_command_error(self, ctx, error):
        logging.error(f"An error occurred: {error}")
        await ctx.send(f"An error occurred: {error}")
        

if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.message_content = True

    bot = BotClient(command_prefix="!", intents=intents)
    bot.run(os.getenv("DISCORD_TOKEN"))

