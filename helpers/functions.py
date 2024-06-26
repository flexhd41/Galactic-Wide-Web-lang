from json import dumps, loads
from math import ceil
from os import getenv
from re import sub
from aiohttp import ClientSession


def health_bar(current_health: int, max_health: int, race: str, reverse: bool = False):
    if race not in ("Terminids", "Automaton", "Illuminate", "Humans", "MO"):
        print(race, "race not in health_bar func")
        return ""
    perc = (
        10 - ceil((current_health / max_health) * 10)
        if reverse
        else ceil((current_health / max_health) * 10)
    )
    health_icon_dict = {
        "Terminids": "<:tc:1229360523217342475>",
        "Automaton": "<:ac:1229360519689801738>",
        "Illuminate": "<:ic:1229360521002618890>",
        "Humans": "<:hc:1229362077974401024>",
        "MO": "<:moc:1229360522181476403>",
    }
    progress_bar = health_icon_dict[race] * perc
    while perc < 10:
        progress_bar += "<:nc:1229450109901606994>"
        perc += 1
    return progress_bar


async def pull_from_api(
    get_war_state: bool = False,
    get_assignments: bool = False,
    get_campaigns: bool = False,
    get_dispatches: bool = False,  # first index is newest
    get_planets: bool = False,
    get_planet_events: bool = False,
    get_steam: bool = False,  # first index is newest
    get_thumbnail: bool = False,
    language: str = "en-GB",
):

    api = getenv("API")
    results = {}
    if get_war_state:
        async with ClientSession(headers={"Accept-Language": language}) as session:
            try:
                async with session.get(f"{api}/war") as r:
                    if r.status == 200:
                        js = await r.json()
                        results["war_state"] = loads(dumps(js))
                        await session.close()
            except Exception as e:
                print(("API/WAR", e))
    if get_assignments:
        async with ClientSession(headers={"Accept-Language": language}) as session:
            try:
                async with session.get(f"{api}/assignments") as r:
                    if r.status == 200:
                        js = await r.json()
                        results["assignments"] = loads(dumps(js))
                        await session.close()
            except Exception as e:
                print(("API/ASSIGNMENTS", e))
    if get_campaigns:
        async with ClientSession(headers={"Accept-Language": language}) as session:
            try:
                async with session.get(f"{api}/campaigns") as r:
                    if r.status == 200:
                        js = await r.json()
                        results["campaigns"] = loads(dumps(js))
                        await session.close()
            except Exception as e:
                print(("API/CAMPAIGNS", e))
    if get_dispatches:
        async with ClientSession(headers={"Accept-Language": language}) as session:
            try:
                async with session.get(f"{api}/dispatches") as r:
                    if r.status == 200:
                        js = await r.json()
                        results["dispatches"] = loads(dumps(js))
                        await session.close()
            except Exception as e:
                print(("API/DISPATCHES", e))
    if get_planets:
        async with ClientSession(headers={"Accept-Language": language}) as session:
            try:
                async with session.get(f"{api}/planets") as r:
                    if r.status == 200:
                        js = await r.json()
                        results["planets"] = loads(dumps(js))
                        await session.close()
            except Exception as e:
                print(("API/PLANETS", e))
    if get_planet_events:
        async with ClientSession(headers={"Accept-Language": language}) as session:
            try:
                async with session.get(f"{api}/planet-events") as r:
                    if r.status == 200:
                        js = await r.json()
                        results["planet_events"] = loads(dumps(js)) or None
                        await session.close()
            except Exception as e:
                print(("API/PLANET-EVENTS", e))
    if get_steam:
        async with ClientSession(headers={"Accept-Language": language}) as session:
            try:
                async with session.get(f"{api}/steam") as r:
                    if r.status == 200:
                        js = await r.json()
                        results["steam"] = loads(dumps(js))
                        await session.close()
            except Exception as e:
                print(("API/STEAM", e))
    if get_thumbnail:
        async with ClientSession() as session:
            try:
                async with session.get(f"https://helldivers.news/api/planets") as r:
                    if r.status == 200:
                        js = await r.json()
                        results["thumbnails"] = loads(dumps(js))
                        await session.close()
                    else:
                        pass
            except Exception as e:
                print(("API/THUMBNAILS", e))
    return results


def short_format(num):
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num = round(num / 1000.0, 2)
    return "{:.{}f}{}".format(num, 2, ["", "K", "M", "B", "T", "Q"][magnitude])


def dispatch_format(message: str):
    try:
        message = (
            message.replace("<i=3>", "")
            .replace("</i=2>", "")
            .replace("</i=3>", "")
            .replace("</i=1>", "")
            .replace("</i>", "")
            .replace("<i=1>", "")
            .replace("<i=2>", "")
            .replace("<br>", "\n")
        )
    except:
        print("Failed to format dispatch")
    return message


def steam_format(content: str):  # thanks Chats
    content = sub(r"\[h1\](.*?)\[/h1\]", r"# \1", content)
    content = sub(r"\[h2\](.*?)\[/h2\]", r"## \1", content)
    content = sub(r"\[h3\](.*?)\[/h3\]", r"### \1", content)
    content = sub(r"\[h3\](.*?)\[/h4\]", r"### \1", content)
    content = sub(r"\[h3\](.*?)\[/h5\]", r"### \1", content)
    content = sub(r"\[h3\](.*?)\[/h6\]", r"### \1", content)
    content = sub(r"\[url=(.+?)](.+?)\[/url\]", r"[\2]\(\1\)", content)
    content = sub(r"\[quote\]", r"> ", content)
    content = sub(r"\[quote\]", r"> ", content)
    content = sub(r"\[/quote\]", r"", content)
    content = sub(r"\[b\]", r"**", content)
    content = sub(r"\[/b\]", r"**", content)
    content = sub(r"\[i\]", r"*", content)
    content = sub(r"\[/i\]", r"*", content)
    content = sub(r"\[u\]", r"\n# __", content)
    content = sub(r"\[/u\]", r"__", content)
    content = sub(r"\[list\]", r"", content)
    content = sub(r"\[/list\]", r"", content)
    content = sub(r"\[\*\]", r" - ", content)
    content = sub(r"/\[img\](.*?)\[\/img\]/", r"", content)
    content = sub(
        r"\[previewyoutube=(.+);full\]\[/previewyoutube\]",
        "[YouTube](https://www.youtube.com/watch?v=" + r"\1)",
        content,
    )
    content = sub(r"\[img\](.*?\..{3,4})\[/img\]\n\n", "", content)
    return content
