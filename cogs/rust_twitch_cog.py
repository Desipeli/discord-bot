import logging
import requests
from bs4 import BeautifulSoup
from discord.ext import commands, tasks

URL = "https://twitch.facepunch.com/"


class RustTwitchCog(commands.Cog):
    """ Alert twitch drops """

    def __init__(self, bot):
        self.bot = bot
        self.alerting_channels = set()
        self.checkForDrops.start()
        self.onGoingCampaign = False

    @commands.command(name="add_rust_twich")
    async def add_rust_twich(self, ctx: commands.Context):
        """ Alert this channel when new twitch drops are available """
        self.alerting_channels.add(ctx.channel.id)
        await ctx.send(f"Alerting")

    @tasks.loop(minutes=1)
    async def checkForDrops(self):
        response = requests.get(URL)
        soup = BeautifulSoup(response.text, features="html.parser")
        campaign = soup.find_all(class_="campaign")
        if self.onGoingCampaign:
            if not campaign:
                logging.info("Rust Twitch drop campaign ended")
                self.onGoingCampaign = False
        else:
            if campaign:
                logging.info("Rust Twitch drop campaign started")
                self.onGoingCampaign = True
                for channel_id in self.alerting_channels:
                    channel = self.bot.get_channel(channel_id)
                    await channel.send(f"Twitch drops {URL}")
