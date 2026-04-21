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
# DISCORD SETUP
# =====================
intents = discord.Intents.default()
client = discord.Client(intents=intents)

already_reported = set()

# =====================
# FLASK (RENDER PORT FIX)
# =====================
app = Flask(__name__)

@app.route("/")
def home():
    return "BFV Bot running 🚀"

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
        data = r.json()
        return data.get("servers", [])
    except Exception as e:
        print("API error:", e)
        return []

# =====================
# FILTER HELPERS
# =====================
def is_eu(server):
    region = server.get("region", "").lower()
    return any(x in region for x in ["eu", "europe", "de", "frankfurt"])

def get_players(server):
    try:
        return server.get("slots", {}).get("Soldier", {}).get("current", 0)
    except:
        return 0

# =====================
# MAIN LOOP
# =====================
async def check_servers():
    await client.wait_until_ready()
    user = await client.fetch_user(USER_ID)

    while not client.is_closed():
        servers = get_servers()

        print(f"[DEBUG] Servers fetched: {len(servers)}")

        for s in servers:
            map_name = s.get("mapNamePretty", "").lower()
            name = s.get("name", "unknown")
            server_id = s.get("gameId")

            players = get_players(s)

            # DEBUG (sehr wichtig beim ersten Start)
            print(f"[DEBUG] {map_name} | {players} | {s.get('region')} | {name}")

            # FILTER
            if (
                TARGET_MAP in map_name
                and players >= MIN_PLAYERS
                and is_eu(s)
            ):
                if server_id not in already_reported:
                    already_reported.add(server_id)

                    msg = (
                        f"🔥 Operation Underground EU Server gefunden!\n"
                        f"Server: {name}\n"
                        f"Spieler: {players}\n"
                        f"Map: {map_name}"
                    )

                    await user.send(msg)
                    print("[ALERT SENT]", name)

        await asyncio.sleep(CHECK_INTERVAL)

# =====================
# DISCORD EVENTS
# =====================
@client.event
async def on_ready():
    print(f"Bot online: {client.user}")
    client.loop.create_task(check_servers())

# =====================
# START
# =====================
def run_discord():
    client.run(TOKEN)

if __name__ == "__main__":
    Thread(target=run_flask).start()
    run_discord()