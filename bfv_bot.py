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
TARGET_MAP = "Operation Underground"
REGION = "EU"

# =====================
# DISCORD CLIENT
# =====================
intents = discord.Intents.default()
client = discord.Client(intents=intents)

already_reported = set()

# =====================
# FLASK (IMPORTANT FOR RENDER)
# =====================
app = Flask(__name__)

@app.route("/")
def home():
    return "BFV Bot is running 🚀"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# =====================
# SERVER LOGIC
# =====================
def get_servers():
    url = "https://api.gametools.network/bfv/servers?platform=pc&limit=200"
    try:
        r = requests.get(url, timeout=10)
        return r.json().get("servers", [])
    except:
        return []

def is_eu(server):
    region = server.get("region", "")
    return REGION.lower() in region.lower()

async def check_servers():
    await client.wait_until_ready()
    user = await client.fetch_user(USER_ID)

    while not client.is_closed():
        servers = get_servers()

        for s in servers:
            map_name = s.get("mapNamePretty", "")
            players = s.get("slots", {}).get("Soldier", {}).get("current", 0)
            name = s.get("name")
            server_id = s.get("gameId")

            if (
                TARGET_MAP in map_name
                and players >= MIN_PLAYERS
                and is_eu(s)
            ):
                if server_id not in already_reported:
                    already_reported.add(server_id)

                    msg = (
                        f"🔥 Operation Underground (EU) gefunden!\n"
                        f"Server: {name}\n"
                        f"Spieler: {players}\n"
                        f"Map: {map_name}"
                    )

                    await user.send(msg)

        await asyncio.sleep(CHECK_INTERVAL)

# =====================
# DISCORD EVENTS
# =====================
@client.event
async def on_ready():
    print(f"Bot online: {client.user}")
    client.loop.create_task(check_servers())

# =====================
# STARTUP (IMPORTANT)
# =====================
def run_discord():
    client.run(TOKEN)

if __name__ == "__main__":
    # Flask in eigenem Thread (wichtig für Render Web Service)
    Thread(target=run_flask).start()

    # Discord Bot im Main Thread
    run_discord()