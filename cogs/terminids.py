from json import load
from disnake import AppCmdInter
from disnake.ext import commands
from helpers.db import Guilds
from helpers.embeds import Terminid
from data.lists import enemies


class TerminidsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.terminids_dict = enemies["terminids"]
        self.variations_dict: dict = {}
        for i in enemies["terminids"].values():
            if i["variations"] != None:
                for n, j in i["variations"].items():
                    self.variations_dict[n] = j
        print("Terminids cog has finished loading")

    async def terminids_autocomp(inter: AppCmdInter, user_input: str):
        return [
            command for command in enemies["terminids"] if user_input in command.lower()
        ]

    async def variations_autocomp(inter: AppCmdInter, user_input: str):
        variations_list: list[str] = []
        for i in enemies["terminids"].values():
            if i["variations"] != None:
                for n in i["variations"]:
                    variations_list.append(n)
        return [command for command in variations_list if user_input in command.lower()]

    @commands.slash_command(
        description="Returns information on a Terminid or variation.",
    )
    async def terminid(
        self,
        inter: AppCmdInter,
        species: str = commands.Param(
            autocomplete=terminids_autocomp,
            default=None,
            description="A specific 'main' species",
        ),
        variation: str = commands.Param(
            autocomplete=variations_autocomp,
            default=None,
            description="A specific variant of a species",
        ),
    ):
        if not species and not variation:
            return await inter.send(
                "<a:explodeybug:1219248670482890752>", delete_after=10.0, ephemeral=True
            )
        guild_in_db = Guilds.get_info(inter.guild_id)
        guild_language = load(
            open(f"data/languages/{guild_in_db[5]}.json", encoding="UTF-8")
        )
        if species and variation:
            return await inter.send(
                guild_language["enemy.species_or_variation"],
                ephemeral=True,
            )
        elif species != None and species not in self.terminids_dict:
            return await inter.send(
                guild_language["enemy.missing"],
                ephemeral=True,
            )
        elif variation != None and variation not in self.variations_dict:
            return await inter.send(
                guild_language["enemy.missing"],
                ephemeral=True,
            )
        if species != None:
            species_info = self.terminids_dict[species]
            embed = Terminid(species, species_info, guild_language)
        elif variation != None:
            variation_info = self.variations_dict[variation]
            embed = Terminid(variation, variation_info, guild_language, variation=True)
        return await inter.send(embed=embed, ephemeral=True)


def setup(bot: commands.Bot):
    bot.add_cog(TerminidsCog(bot))
