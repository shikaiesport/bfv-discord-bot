import discord
import requests
import asyncio
import os
from flask import Flask
from threading import Thread

TOKEN = os.environ["TOKEN"]
USER_ID = int(os.environ["USER_ID"])

CHECK_INTERVAL = 30
MIN_PLAYERS = 45

intents = discord.Intents.default()
client = discord.Client(intents=intents)

already_reported = set()

# ---------------- Flask ----------------

app = Flask(__name__)

@app.route("/")
def home():
    return "BFV Bot running"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# ---------------- API ----------------

def get_servers():
    url = "https://api.gametools.network/bfv/servers?platform=pc&limit=200"
    try:
        r = requests.get(url, timeout=10)
        return r.json().get("servers", [])
    except Exception as e:
        print("API error:", e)
        return []

def get_players(server):
    return server.get("slots", {}).get("Soldier", {}).get("current", 0)

def is_eu(server):
    region = server.get("region", "").lower()
    return any(x in region for x in ["eu", "europe", "de", "frankfurt"])

# ---------------- LOOP ----------------

async def check_servers():
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
                print("FOUND:", name, players, map_name)

            if (
                "underground" in map_name
                and players >= MIN_PLAYERS
                and is_eu(s)
            ):
                print("MATCH:", name, players)

                if server_id not in already_reported:
                    already_reported.add(server_id)

                    msg = (
                        f"🔥 Operation Underground EU Server\n"
                        f"{name}\n"
                        f"Spieler: {players}"
                    )

                    try:
                        await user.send(msg)
                        print("DM SENT")
                    except Exception as e:
                        print("DM ERROR:", e)

        await asyncio.sleep(CHECK_INTERVAL)

# ---------------- READY ----------------

@client.event
async def on_ready():
    print("BOT READY:", client.user)

    # HIER der sichere Start
    client.loop.create_task(check_servers())

# ---------------- START ----------------

def run_discord():
    client.run(TOKEN)

if __name__ == "__main__":
    Thread(target=run_flask).start()
    run_discord()
