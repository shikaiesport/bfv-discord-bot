import os
import asyncio
import discord
import requests
from flask import Flask
from threading import Thread

TOKEN = os.getenv("DISCORD_TOKEN")
USER_ID = int(os.getenv("USER_ID"))

THRESHOLD = 45

URL = "https://api.battlemetrics.com/servers?filter[search]=underground&page[size]=50"

intents = discord.Intents.default()
client = discord.Client(intents=intents)

app = Flask(__name__)

notified = set()


def get_servers():
    try:
        r = requests.get(URL, timeout=10)
        data = r.json()

        results = []

        for s in data["data"]:
            attr = s["attributes"]
            name = attr.get("name", "").lower()
            players = attr.get("players", 0)

            if "underground" in name and players >= THRESHOLD:
                results.append((s["id"], name, players))

        return results

    except Exception as e:
        print("API ERROR:", e)
        return []


async def monitor():
    global notified

    while True:
        servers = get_servers()

        print("CHECK:", servers)

        for sid, name, players in servers:
            if sid not in notified:
                try:
                    user = await client.fetch_user(USER_ID)
                    await user.send(f"🚨 Underground Server!\n{name} ({players})")
                    notified.add(sid)
                except Exception as e:
                    print("DM ERROR:", e)

        if not servers:
            notified.clear()

        await asyncio.sleep(60)


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

    # 🔥 WICHTIG: Loop HIER starten
    client.loop.create_task(monitor())


@app.route("/")
def home():
    return "OK"


def run_flask():
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))


Thread(target=run_flask).start()
client.run(TOKEN)
