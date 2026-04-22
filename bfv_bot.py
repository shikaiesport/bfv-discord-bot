import os
import asyncio
import discord
import requests
from flask import Flask
from threading import Thread

TOKEN = os.getenv("DISCORD_TOKEN")
USER_ID = int(os.getenv("USER_ID"))

THRESHOLD = 45
SEARCH_URL = "https://api.battlemetrics.com/servers?filter[search]=underground"

intents = discord.Intents.default()
client = discord.Client(intents=intents)

app = Flask(__name__)

notified_servers = set()


def get_servers():
    try:
        r = requests.get(SEARCH_URL, timeout=10)
        data = r.json()

        servers = []

        for s in data["data"]:
            attrs = s["attributes"]
            name = attrs.get("name", "").lower()
            players = attrs.get("players", 0)

            if "underground" in name and players >= THRESHOLD:
                servers.append((s["id"], name, players))

        return servers

    except Exception as e:
        print("API ERROR:", e)
        return []


async def monitor():
    global notified_servers

    await client.wait_until_ready()

    while not client.is_closed():
        servers = get_servers()

        print("Found:", servers)

        for sid, name, players in servers:
            if sid not in notified_servers:
                user = await client.fetch_user(USER_ID)
                await user.send(
                    f"🚨 Underground Server ONLINE!\n"
                    f"Name: {name}\nPlayers: {players}"
                )
                notified_servers.add(sid)

        # Reset wenn Spieler runtergehen (optional sauberer refresh)
        if not servers:
            notified_servers.clear()

        await asyncio.sleep(60)


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")


@app.route("/")
def home():
    return "Bot läuft"


def run_flask():
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))


def run_bot():
    client.loop.create_task(monitor())
    client.run(TOKEN)


if __name__ == "__main__":
    Thread(target=run_flask).start()
    run_bot()
