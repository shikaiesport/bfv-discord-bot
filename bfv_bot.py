import os
import discord
from discord.ext import commands, tasks
from flask import Flask
import requests

# ---------------- WEB SERVER (Render Pflicht) ----------------
app = Flask(__name__)

@app.route("/")
def home():
    return "BFV Bot is running"


def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


# ---------------- DISCORD BOT ----------------
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

TOKEN = os.environ["TOKEN"]
USER_ID = int(os.environ["USER_ID"])

# 👉 HIER DEINE API EINTRAGEN
API_URL = os.environ["API_URL"]


# ---------------- API CALL ----------------
def get_servers():
    """
    Erwartet:
    [
        {"name": "Underground #1", "players": 50},
        ...
    ]
    """

    try:
        r = requests.get(API_URL, timeout=10)
        return r.json()

    except Exception as e:
        print("API Fehler:", e)
        return []


# ---------------- STATE (kein Spam) ----------------
alerted = set()


# ---------------- LOOP ----------------
@tasks.loop(seconds=60)
async def check_servers():
    global alerted

    servers = get_servers()

    user = await bot.fetch_user(USER_ID)

    for s in servers:

        name = s.get("name", "").lower()
        players = int(s.get("players", 0))

        is_underground = "underground" in name
        key = s.get("name")

        if is_underground and players > 45 and key not in alerted:

            await user.send(
                f"🚨 BFV ALERT\n"
                f"Server: {s['name']}\n"
                f"Players: {players}"
            )

            alerted.add(key)

        # Reset wenn wieder runter
        if players <= 45 and key in alerted:
            alerted.remove(key)


# ---------------- READY ----------------
@bot.event
async def on_ready():
    print(f"Bot online als {bot.user}")
    check_servers.start()


# ---------------- START ----------------
if __name__ == "__main__":
    import threading

    threading.Thread(target=run_web).start()

    bot.run(TOKEN)
