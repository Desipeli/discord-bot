import datetime
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
        self.load_channels_from_file()
        self.onGoingCampaignAlerted = False
        self.comingCampaignAlerted = False
        self.checkForDrops.start()

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
        not_started = soup.find_all(class_="not-started")
        if self.onGoingCampaignAlerted:
            if not campaign or not_started:
                logging.info("Rust Twitch drop campaign ended")
                self.onGoingCampaignAlerted = False
        else:
            if campaign and not not_started:
                self.comingCampaignAlerted = False
                logging.info("Rust Twitch drop campaign started")
                for channel_id in self.alerting_channels:
                    channel = self.bot.get_channel(channel_id)
                    await channel.send(f"Twitch drops {URL}")
                self.onGoingCampaignAlerted = True

        if not self.comingCampaignAlerted and campaign and not_started:
            try:
                round_number = soup.find(class_="round-info-number").text
                round_title = soup.find(class_="round-info-title").text

                # Timestamps can be found from data-date-ids, format: randomstring-timestamp
                date_ids = [
                    int(span["data-date-id"].split("-")[1]) for span in soup.find_all("span", class_="date")]
                start_date = datetime.datetime.fromtimestamp(
                    date_ids[0])
                start_date = start_date.strftime('%d-%m-%Y %H:%M')
                end_date = datetime.datetime.fromtimestamp(date_ids[1])
                end_date = end_date.strftime('%d-%m-%Y %H:%M')

                video_sources = []
                for video in soup.find_all('video'):
                    for source in video.find_all('source'):
                        video_sources.append(source['src'])

                for channel_id in self.alerting_channels:
                    channel = self.bot.get_channel(channel_id)
                    await channel.send(f"""
Next Rust Twitch drop event: {start_date} to {end_date}
{round_number}
{round_title}
                                       """)

                # Discord displays only 5 videos per message
                video_links = ""
                for i, video_link in enumerate(video_sources):
                    i = i+1
                    video_links += f"{video_link}\n"
                    if i % 5 == 0:
                        await channel.send(video_links)
                        video_links = ""
                await channel.send(video_links)

                self.comingCampaignAlerted = True
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
