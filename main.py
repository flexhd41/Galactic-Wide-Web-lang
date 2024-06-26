from disnake.ext import commands
from dotenv import load_dotenv
from os import getenv
from disnake import ActivityType, Intents, Activity
import logging

logger = logging.getLogger("disnake")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename="disnake.log", encoding="utf-8", mode="w")
handler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
logger.addHandler(handler)

intents = Intents.default()

load_dotenv("data/.env")
OWNER = int(getenv("OWNER"))

activity = Activity(name="for Socialism", type=ActivityType.watching)

bot = commands.InteractionBot(
    owner_id=OWNER,
    intents=intents,
    activity=activity,
)

bot.load_extensions("cogs")


if __name__ == "__main__":
    bot.run(getenv("TOKEN"))
