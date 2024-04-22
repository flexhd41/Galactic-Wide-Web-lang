from asyncio import sleep
from disnake import TextChannel
from disnake.ext import commands, tasks
from helpers.db import Campaigns, Guilds
from helpers.embeds import CampaignEmbed, CampaignEmbeds
from helpers.functions import pull_from_api
from datetime import datetime


class WarUpdatesCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.channels = []
        self.cache_channels.start()
        self.campaign_check.start()
        print("War Updates cog has finished loading")

    def cog_unload(self):
        self.campaign_check.stop()
        self.cache_channels.stop()

    async def channel_list_gen(self, channel_id: int):
        try:
            channel = self.bot.get_channel(channel_id) or await self.bot.fetch_channel(
                channel_id
            )
            self.channels.append(channel)
        except:
            print(channel_id, "channel not found")
            pass

    async def send_campaign(self, channel: TextChannel, embed):
        try:
            await channel.send(embed=embed)
        except Exception as e:
            print("Send campaign", e, channel)
            pass

    @tasks.loop(count=1)
    async def cache_channels(self):
        guilds = Guilds.get_all_guilds()
        if not guilds:
            return
        self.channels = []
        for guild in guilds:
            if guild[3] == 0:
                continue
            self.bot.loop.create_task(self.channel_list_gen(guild[3]))

    @cache_channels.before_loop
    async def before_caching(self):
        await self.bot.wait_until_ready()

    @tasks.loop(minutes=1)
    async def campaign_check(self):
        data = await pull_from_api(
            get_planets=True, get_campaigns=True, get_war_state=True
        )
        planets = data["planets"]
        war = data["war_state"]
        new_campaigns = data["campaigns"]
        old_campaigns = Campaigns.get_all()
        embed = CampaignEmbed()
        new_updates = False

        new_campaign_ids = []
        for campaign in new_campaigns:
            new_campaign_ids.append(campaign["id"])

        if old_campaigns == []:
            for new_campaign in new_campaigns:
                Campaigns.new_campaign(
                    new_campaign["id"],
                    new_campaign["planet"]["name"],
                    new_campaign["planet"]["currentOwner"],
                    new_campaign["planet"]["index"],
                )
            return

        old_campaign_ids = []
        for old_campaign in old_campaigns:  # loop through old campaigns
            old_campaign_ids.append(old_campaign[0])
            if old_campaign[0] not in new_campaign_ids:
                # if campaign is no longer active
                planet = planets[old_campaign[3]]
                if planet["currentOwner"] == "Humans" and old_campaign[2] == "Humans":
                    # if successful defence campaign
                    embed.add_def_victory(planet)
                    new_updates = True
                    Campaigns.remove_campaign(old_campaign[0])
                if planet["currentOwner"] != old_campaign[2]:  # if owner has changed
                    if old_campaign[2] == "Humans":  # if defence campaign loss
                        Campaigns.remove_campaign(old_campaign[0])
                    elif planet["currentOwner"] == "Humans":  # if attack campaign win
                        embed.add_campaign_victory(planet, old_campaign[2])
                        new_updates = True
                        Campaigns.remove_campaign(old_campaign[0])
                elif planet["currentOwner"] != "Humans":
                    Campaigns.remove_campaign(old_campaign[0])

        for new_campaign in new_campaigns:  # loop through new campaigns
            if new_campaign["id"] not in old_campaign_ids:  # if campaign is brand new
                planet = planets[new_campaign["planet"]["index"]]
                try:
                    war_now = datetime.fromisoformat(war["now"]).timestamp()
                except Exception as e:
                    print("war_now", e)
                    war_now = None
                try:
                    end_time = datetime.fromisoformat(
                        new_campaign["planet"]["event"]["endTime"]
                    ).timestamp()
                except:
                    end_time = None
                current_time = datetime.now().timestamp()
                if war_now != None and current_time != None and end_time != None:
                    time_remaining = (
                        f"<t:{((current_time - war_now) + end_time):.0f}:R>"
                    )
                else:
                    time_remaining = None
                embed.add_new_campaign(new_campaign, time_remaining)
                new_updates = True
                Campaigns.new_campaign(
                    new_campaign["id"],
                    new_campaign["planet"]["name"],
                    planet["currentOwner"],
                    new_campaign["planet"]["index"],
                )
            continue
        if new_updates:
            embed.remove_empty()
            chunked_channels = [
                self.channels[i : i + 100] for i in range(0, len(self.channels), 100)
            ]
            for chunk in chunked_channels:
                for channel in chunk:
                    self.bot.loop.create_task(self.send_campaign(channel, embed))
                await sleep(60)

    @campaign_check.before_loop
    async def before_dashboard(self):
        await self.bot.wait_until_ready()


def setup(bot: commands.Bot):
    bot.add_cog(WarUpdatesCog(bot))
