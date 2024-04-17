from asyncio import sleep
from datetime import datetime
from disnake import (
    Activity,
    ActivityType,
    ButtonStyle,
    Guild,
    MessageInteraction,
    NotFound,
)
from disnake.ext import commands, tasks
from helpers.db import Guilds, BotDashboard
from helpers.embeds import BotDashboardEmbed, ReactRoleDashboard
from os import getenv, getpid
from psutil import Process, cpu_percent
from helpers.functions import health_bar
from disnake.ui import Button


class GuildManagementCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot_dashboard.start()
        self.react_role_dashboard.start()
        print("Guild Management cog has finished loading")
        self.startup_time = datetime.now()

    def cog_unload(self):
        self.bot_dashboard.stop()
        self.react_role_dashboard.stop()

    @commands.Cog.listener()
    async def on_guild_join(self, guild: Guild):
        channel_id = int(getenv("MODERATION_CHANNEL"))
        channel = self.bot.get_channel(channel_id) or await self.bot.fetch_channel(
            channel_id
        )
        Guilds.insert_new_guild(guild.id)
        await channel.send(
            f"Just joined server #{len(self.bot.guilds)} `{guild.name}` with {guild.member_count} members"
        )
        await self.bot.change_presence(
            activity=Activity(name="for alien sympathisers", type=ActivityType.watching)
        )
        await sleep(10.0)
        await self.bot.change_presence(
            activity=Activity(name="for Socialism", type=ActivityType.watching)
        )

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: Guild):
        channel_id = int(getenv("MODERATION_CHANNEL"))
        channel = self.bot.get_channel(channel_id) or await self.bot.fetch_channel(
            channel_id
        )
        Guilds.remove_from_db(guild.id)
        await channel.send(
            f"Just left `{guild.name}`, down to {len(self.bot.guilds)} servers"
        )

    @tasks.loop(minutes=1)
    async def bot_dashboard(self):
        data = BotDashboard.get_info()
        if data[1] == 0:
            channel = self.bot.get_channel(data[0]) or await self.bot.fetch_channel(
                data[0]
            )
            message = await channel.send("Placeholder message, please ignore.")
            BotDashboard.set_message(message.id)
        else:
            now = datetime.now()
            dashboard_embed = BotDashboardEmbed(now)
            commands = ""
            for command in self.bot.global_slash_commands:
                commands += f"`/{command.name}`\n"
            dashboard_embed.add_field(
                "The GWW has",
                f"{len(self.bot.global_slash_commands)} commands available:\n{commands}",
            ).add_field("Currently in", f"{len(self.bot.guilds)} discord servers")
            pid = getpid()
            process = Process(pid)
            memory_used = process.memory_info().rss / 1024**2
            dashboard_embed.add_field(
                "------------------\nHardware Info",
                (
                    f"**CPU**: {cpu_percent()}%\n"
                    f"**RAM**: {memory_used:.2f}MB\n"
                    f"**Last restart**: <t:{int(self.startup_time.timestamp())}:R>\n"
                    f"**Latency**: {int(self.bot.latency * 1000)}ms"
                ),
                inline=False,
            )

            dashboard_not_setup = len(Guilds.dashboard_not_setup())
            healthbar = health_bar(
                (len(self.bot.guilds) - dashboard_not_setup),
                len(self.bot.guilds),
                "Illuminate",
            )
            dashboard_embed.add_field(
                "------------------\nDashboards Setup",
                (
                    f"**Setup**: {len(self.bot.guilds) - dashboard_not_setup}\n"
                    f"**Not Setup**: {dashboard_not_setup}\n"
                    f"{healthbar}"
                ),
            )

            feed_not_setup = len(Guilds.feed_not_setup())
            healthbar = health_bar(
                (len(self.bot.guilds) - feed_not_setup),
                len(self.bot.guilds),
                "Illuminate",
            )
            dashboard_embed.add_field(
                "------------------\nAnnouncements Setup",
                (
                    f"**Setup**: {len(self.bot.guilds) - feed_not_setup}\n"
                    f"**Not Setup**: {feed_not_setup}\n"
                    f"{healthbar}"
                ),
            )

            patch_notes_not_setup = len(Guilds.patch_notes_not_setup())
            healthbar = health_bar(
                (len(self.bot.guilds) - patch_notes_not_setup),
                len(self.bot.guilds),
                "Illuminate",
            )
            dashboard_embed.add_field(
                "------------------\nPatch Notes Enabled",
                (
                    f"**Setup**: {len(self.bot.guilds) - patch_notes_not_setup}\n"
                    f"**Not Setup**: {patch_notes_not_setup}\n"
                    f"{healthbar}"
                ),
                inline=False,
            )
            dashboard_embed.add_field(
                "Credits",
                (
                    "https://helldivers.fandom.com/wiki/Helldivers_Wiki - Most of my enemy information is from them, as well as a lot of the enemy images.\n\n"
                    "https://helldivers.news/ - Planet images are from them, their website is also amazing.\n\n"
                    "https://github.com/helldivers-2/ - The people over here are kind and helpful, great work too!\n\n"
                    "and **You**\n"
                ),
            )

            channel = self.bot.get_channel(data[0]) or await self.bot.fetch_channel(
                data[0]
            )
            try:
                message = channel.get_partial_message(data[1])
            except Exception as e:
                print(f"bot_dashboard ", e)
            try:
                await message.edit(
                    embed=dashboard_embed,
                    components=[
                        Button(
                            label="Top.GG",
                            style=ButtonStyle.link,
                            url="https://top.gg/bot/1212535586972369008",
                        ),
                        Button(
                            label="App Directory",
                            style=ButtonStyle.link,
                            url="https://discord.com/application-directory/1212535586972369008",
                        ),
                        Button(
                            label="Ko-Fi",
                            style=ButtonStyle.link,
                            url="https://ko-fi.com/galacticwideweb",
                        ),
                        Button(
                            label="GitHub",
                            style=ButtonStyle.link,
                            url="https://github.com/Stonemercy/Galactic-Wide-Web",
                        ),
                    ],
                ),
            except:
                pass

    @bot_dashboard.before_loop
    async def before_bot_dashboard(self):
        await self.bot.wait_until_ready()

    @tasks.loop(hours=1)
    async def react_role_dashboard(self):
        embed = ReactRoleDashboard()
        data = BotDashboard.get_info()
        channel_id = data[0]
        message_id = data[2]
        components = [
            Button(label="Subscribe to Bot Updates", custom_id="BotUpdatesButton")
        ]
        channel = self.bot.get_channel(channel_id) or await self.bot.fetch_channel(
            channel_id
        )
        if channel == None:
            return
        if message_id == None:
            message = await channel.send(embed=embed, components=components)
            BotDashboard.set_react_role(message.id)
        else:
            message = channel.get_partial_message(message_id)
            try:
                await message.edit(embed=embed, components=components)
            except NotFound:
                message = await channel.send(embed=embed, components=components)
                BotDashboard.set_react_role(message.id)
            except:
                pass

    @react_role_dashboard.before_loop
    async def before_react_role(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener("on_button_click")
    async def react_role(self, inter: MessageInteraction):
        if inter.component.custom_id == "BotUpdatesButton":
            role = inter.guild.get_role(1228077919952437268)
            if role in inter.author.roles:
                await inter.author.remove_roles(role)
                return await inter.send(
                    "Removed the Bot Update role from you",
                    ephemeral=True,
                    delete_after=10,
                )
            else:
                await inter.author.add_roles(role)
                return await inter.send(
                    "Gave you the Bot Update role",
                    ephemeral=True,
                    delete_after=10,
                )


def setup(bot: commands.Bot):
    bot.add_cog(GuildManagementCog(bot))
