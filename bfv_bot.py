import discord
import requests
import asyncio
import os

TOKEN = os.environ["TOKEN"]
USER_ID = int(os.environ["USER_ID"])

CHECK_INTERVAL = 30
MIN_PLAYERS = 45

intents = discord.Intents.default()
client = discord.Client(intents=intents)

already_reported = set()

def get_servers():
    url = "https://api.gametools.network/bfv/servers?platform=pc&limit=200"
    try:
        r = requests.get(url, timeout=10)
        return r.json().get("servers", [])
    except Exception as e:
        print("API ERROR:", e)
        return []

def get_players(s):
    return s.get("slots", {}).get("Soldier", {}).get("current", 0)

def is_eu(s):
    region = s.get("region", "").lower()
    return any(x in region for x in ["eu", "europe", "de", "frankfurt"])

async def check_loop():
    await client.wait_until_ready()

    print("CHECK LOOP STARTED")

    user = await client.fetch_user(USER_ID)

    while True:
        servers = get_servers()
        print("Servers:", len(servers))

        for s in servers:
            map_name = s.get("mapNamePretty", "").lower()
            players = get_players(s)
            name = s.get("name")
            server_id = s.get("gameId")

            if "underground" in map_name:
                print("FOUND:", name, players)

            if (
                "underground" in map_name
                and players >= MIN_PLAYERS
                and is_eu(s)
            ):
                print("MATCH:", name, players)

                if server_id not in already_reported:
                    already_reported.add(server_id)

                    try:
                        await user.send(
                            f"🔥 Underground EU\n{name}\nSpieler: {players}"
                        )
                        print("DM SENT")
                    except Exception as e:
                        print("DM ERROR:", e)

        await asyncio.sleep(CHECK_INTERVAL)

@client.event
async def on_ready():
    print("BOT READY:", client.user)
    client.loop.create_task(check_loop())

client.run(TOKEN)
