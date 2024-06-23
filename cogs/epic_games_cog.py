
import json
import logging
import os
import requests
import pytz
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from datetime import datetime
from config import EPIC_GAMES_DATA
from discord.ext import commands, tasks
from cogs.utils import create_subcommand_response

FREE_GAMES_URL = "https://store.epicgames.com/en-US/free-games"
URL = "https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions?locale=en-US&country=FI&allowCountries=FI"
CHANNEL_LIST_FILE = "channels.txt"
CHANNEL_LIST_FULL_PATH = os.path.join(EPIC_GAMES_DATA, CHANNEL_LIST_FILE)
CURRENT_GAMES = os.path.join(EPIC_GAMES_DATA, "free_games.json")


@dataclass_json
@dataclass(eq=True, frozen=True)
class FreeGame:
    name: str
    end_date: str

    def __repr__(self) -> str:
        return f"{self.name} {self.end_date}"

    def get_local_end_date(self) -> str:
        utc_dt = datetime.fromisoformat(self.end_date.replace("Z", "+00:00"))
        local_tz = pytz.timezone("Europe/Helsinki")
        local_dt = utc_dt.astimezone(local_tz)
        return local_dt.strftime("%d/%m/%Y %H:%M %Z")


class EpicGamesCog(commands.Cog):
    """ Alert free games on Epic """

    def __init__(self, bot):
        self.bot = bot
        self.alerting_channels = set()
        self.load_channels_from_file()
        self.current_games_alerted = False
        self.current_games = set()
        self.load_current_games()
        self.checkForDrops.start()

    @commands.group(name="epic_games", invoke_without_command=True)
    async def epic_games(self, ctx: commands.Context):
        subcommands = self.epic_games.commands
        response = create_subcommand_response(subcommands)
        await ctx.send(response)

    @epic_games.command(
        name="observe_free_epic_games",
        description="Alert this channel when free games on Epic are available")
    async def observe_free_epic_games(self, ctx: commands.Context):
        """ Alert this channel when new free games are available """
        self.alerting_channels.add(ctx.channel.id)
        try:
            self.update_channels_file()
        except Exception:
            await ctx.send("Could not permanently update channel list")
            return
        await ctx.send(f"Alerting")

    @ epic_games.command(
        name="stop_observing_free_games",
        description="Remove from the list of alerted channels")
    async def stop_observing_free_games(self, ctx: commands.Context):
        """ Remove from the list channels"""
        self.alerting_channels.remove(ctx.channel.id)
        try:
            self.update_channels_file()
        except Exception:
            await ctx.send("Could not permanently update channel list")
            return
        await ctx.send("Not alerting")

    @ tasks.loop(minutes=120)
    async def checkForDrops(self):
        response_json = requests.get(URL).json()
        games = response_json["data"]["Catalog"]["searchStore"]["elements"]
        new_free_games = set()
        for new_game in games:
            try:
                if new_game["price"]["totalPrice"]["discountPrice"] != 0:
                    continue
                new_free_games.add(
                    FreeGame(
                        name=new_game["title"],
                        end_date=new_game["promotions"]["promotionalOffers"]
                        [0]["promotionalOffers"][0]["endDate"])
                )
            except Exception as e:
                logging.error(f"EPIC GAMES: {e}")
        difference = new_free_games.difference(self.current_games)

        if len(difference) == 0:
            return

        alert_message = f"[**__New free games on Epic__**]({FREE_GAMES_URL})\n\n"

        try:
            for new_game in new_free_games:
                if new_game not in self.current_games:
                    alert_message += "**"+new_game.name + "**\n"
                    alert_message += "Until: "+new_game.get_local_end_date() + "\n"
                    alert_message += "\n"
            self.current_games = new_free_games
            self.save_current_games()
            for channel_id in self.alerting_channels:
                channel = self.bot.get_channel(channel_id)
                await channel.send(alert_message)
        except Exception as e:
            logging.error(f"EPIC GAMES: {e}")

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

    def save_current_games(self):
        data = [game.to_dict() for game in self.current_games]
        try:
            with open(CURRENT_GAMES, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logging.error(f"EPIC GAMES: {e}")

    def load_current_games(self):
        if not os.path.exists(CURRENT_GAMES):
            return
        try:
            with open(CURRENT_GAMES, "r") as f:
                data = json.load(f)
                self.current_games = {
                    FreeGame.from_dict(game) for game in data}
        except Exception as e:
            logging.error(f"EPIC GAMES: {e}")
