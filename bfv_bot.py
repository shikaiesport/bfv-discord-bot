import discord
import requests
import asyncio
import os
from flask import Flask
from threading import Thread

# =====================
# CONFIG
# =====================
TOKEN = os.environ["TOKEN"]
USER_ID = int(os.environ["USER_ID"])

CHECK_INTERVAL = 30
MIN_PLAYERS = 45
TARGET_MAP = "operation underground"

# =====================
# DISCORD
# =====================
intents = discord.Intents.default()
client = discord.Client(intents=intents)

already_reported = set()
loop_started = False

# =====================
# FLASK (FOR RENDER)
# =====================
app = Flask(__name__)

@app.route("/")
def home():
    return "BFV Bot running"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# =====================
# API
# =====================
def get_servers():
    url = "https://api.gametools.network/bfv/servers?platform=pc&limit=200"
    try:
        r = requests.get(url, timeout=10)
        return r.json().get("servers", [])
    except Exception as e:
        print("API error:", e)
        return []

def get_players(server):
    try:
        return server.get("slots", {}).get("Soldier", {}).get("current", 0)
    except:
        return 0

def is_eu(server):
    region = server.get("region", "").lower()
    return any(x in region for x in ["eu", "europe", "de", "frankfurt"])

# =====================
# MAIN LOOP
# =====================
async def check_servers():
    await client.wait_until_ready()
    user = await client.fetch_user(USER_ID)

    print("Server checking started")

    while not client.is_closed():
        servers = get_servers()

        print(f"[DEBUG] servers fetched: {len(servers)}")

        for s in servers:
            map_name = s.get("mapNamePretty", "").lower()
            name = s.get("name", "unknown")
            server_id = s.get("gameId")
            region = s.get("region")
            players = get_players(s)

            # DEBUG nur Underground anzeigen
            if "underground" in map_name:
                print("FOUND UNDERGROUND:")
                print("Map:", map_name)
                print("Players:", players)
                print("Region:", region)
                print("Name:", name)
                print("------")

            # FILTER
            if (
                "underground" in map_name
                and players >= MIN_PLAYERS
                and is_eu(s)
            ):
                print("MATCHED SERVER:", name, players)

                if server_id not in already_reported:
                    already_reported.add(server_id)

                    msg = (
                        f"🔥 Operation Underground EU Server gefunden!\n"
                        f"Server: {name}\n"
                        f"Spieler: {players}\n"
                        f"Map: {map_name}"
                    )

                    try:
                        await user.send(msg)
                        print("DM SENT")
                    except Exception as e:
                        print("DM FAILED:", e)

        await asyncio.sleep(CHECK_INTERVAL)

# =====================
# DISCORD EVENTS
# =====================
@client.event
async def on_ready():
    global loop_started

    print(f"Bot online: {client.user}")

    if not loop_started:
        asyncio.create_task(check_servers())
        loop_started = True

# =====================
# START
# =====================
def run_discord():
    client.run(TOKEN)

if __name__ == "__main__":
    Thread(target=run_flask).start()
    run_discord()