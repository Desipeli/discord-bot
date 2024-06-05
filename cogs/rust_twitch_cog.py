import logging
import os
import requests
from config import RUST_TWITCH_DATA
from bs4 import BeautifulSoup
from discord.ext import commands, tasks

URL = "https://twitch.facepunch.com/"
CHANNEL_LIST_FILE = "channels.txt"
CHANNEL_LIST_FULL_PATH = os.path.join(RUST_TWITCH_DATA, CHANNEL_LIST_FILE)


class RustTwitchCog(commands.Cog):
    """ Alert twitch drops """

    def __init__(self, bot):
        self.bot = bot
        self.alerting_channels = set()
        self.checkForDrops.start()
        self.onGoingCampaign = False

    @commands.command(name="add_rust_twitch")
    async def add_rust_twitch(self, ctx: commands.Context):
        """ Alert this channel when new twitch drops are available """
        self.alerting_channels.add(ctx.channel.id)
        try:
            self.update_channels_file()
        except Exception:
            await ctx.send("Could not permanently update channel list")
            return
        await ctx.send(f"Alerting")

    @commands.command(name="remove_rust_twitch")
    async def remove_rust_twitch(self, ctx: commands.Context):
        """ Remove from the list channels"""
        self.alerting_channels.remove(ctx.channel.id)
        try:
            self.update_channels_file()
        except Exception:
            await ctx.send("Could not permanently update channel list")
            return
        await ctx.send("Not alerting")

    @tasks.loop(minutes=77)
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

    def update_channels_file(self):
        try:
            with open(CHANNEL_LIST_FULL_PATH, "w") as channel_list:
                for channel_id in self.alerting_channels:
                    channel_list.write(f"{channel_id}\n")
        except Exception as e:
            logging.error(e)
            raise Exception("Could not update channels")
