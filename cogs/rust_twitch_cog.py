import json
import logging
import os
import requests
from config import RUST_TWITCH_DATA
from bs4 import BeautifulSoup
from discord.ext import commands, tasks
from cogs.utils import create_subcommand_response

URL = "https://twitch.facepunch.com/"
CHANNEL_LIST_FILE = "channels.txt"
CHANNEL_LIST_FULL_PATH = os.path.join(RUST_TWITCH_DATA, CHANNEL_LIST_FILE)
ALERTED_JSON = os.path.join(RUST_TWITCH_DATA, "alerted.json")


class RustTwitchCog(commands.Cog):
    """ Alert twitch drops """

    def __init__(self, bot):
        self.bot = bot
        self.alerting_channels = set()
        self.load_channels_from_file()
        self.current_campaign = ""
        self.load_alerted_json()
        self.checkForDrops.start()

    @commands.group(name="rust", invoke_without_command=True)
    async def rust(self, ctx: commands.Context):
        subcommands = self.rust.commands
        response = create_subcommand_response(subcommands)
        await ctx.send(response)

    @rust.command(
        name="observe_twitch_drops",
        description="Alert this channel when a new twitch drop event has started.")
    async def observe_twitch_drops(self, ctx: commands.Context):
        """ Alert this channel when new twitch drops are available """
        self.alerting_channels.add(ctx.channel.id)
        try:
            self.update_channels_file()
        except Exception:
            await ctx.send("Could not permanently update channel list")
            return
        await ctx.send(f"Alerting")

    @ rust.command(
        name="stop_observing_twitch_drops",
        description="Remove from the list of alerted channels")
    async def remove_rust_twitch(self, ctx: commands.Context):
        """ Remove from the list channels"""
        self.alerting_channels.remove(ctx.channel.id)
        try:
            self.update_channels_file()
        except Exception:
            await ctx.send("Could not permanently update channel list")
            return
        await ctx.send("Not alerting")

    @ tasks.loop(minutes=77)
    async def checkForDrops(self):
        try:
            response = requests.get(URL)
            soup = BeautifulSoup(response.text, features="html.parser")
            campaign = soup.find_all(class_="campaign")
            not_started = soup.find_all(class_="not-started")
            round_title = soup.find(class_="round-info-title")

            if campaign and not not_started and round_title and self.current_campaign != round_title.text:
                logging.info("Rust Twitch drop campaign started")
                for channel_id in self.alerting_channels:
                    channel = self.bot.get_channel(channel_id)
                    await channel.send(f"Twitch drops {URL}")
                self.current_campaign = round_title.text
            self.save_alerted_json()
        except Exception as e:
            logging.error(e)

    def load_channels_from_file(self):
        try:
            with open(CHANNEL_LIST_FULL_PATH, "r") as channel_list:
                for channel_id in channel_list:
                    self.alerting_channels.add(int(channel_id))
        except Exception as e:
            logging.error(e)

    def update_channels_file(self):
        try:
            with open(CHANNEL_LIST_FULL_PATH, "w") as channel_list:
                for channel_id in self.alerting_channels:
                    channel_list.write(f"{channel_id}\n")
        except Exception as e:
            logging.error(e)
            raise Exception("Could not update channels")

    def load_alerted_json(self):
        if not os.path.exists(ALERTED_JSON):
            return
        try:
            with open(ALERTED_JSON, "r") as f:
                data = json.load(f)
            self.current_campaign = data["roundTitle"]
        except Exception as e:
            logging.error(f"Could load data from {ALERTED_JSON}, {e}")

    def save_alerted_json(self):
        data = {
            "roundTitle": self.current_campaign
        }
        try:
            with open(ALERTED_JSON, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logging.error(f"Could not save data to {ALERTED_JSON}, {e}")
