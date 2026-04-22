import discord
import asyncio
from flask import Flask
import threading

TOKEN = "DEIN_DISCORD_BOT_TOKEN"
CHANNEL_ID = 1234567890  # optional für Log-DM/Channel

intents = discord.Intents.default()
client = discord.Client(intents=intents)

app = Flask(__name__)

# ---------------- FLASK KEEP ALIVE ----------------
@app.route("/")
def home():
    return "Bot is running"

def run_web():
    app.run(host="0.0.0.0", port=10000)

# ---------------- BFV MONITOR (DEIN LOGIK CODE HIER) ----------------
async def monitor():
    await client.wait_until_ready()

    while not client.is_closed():
        try:
            # 🔥 HIER kommt deine Battlefield/Battlemetrics API Logik rein

            # Beispiel (Fake Check):
            server_name = "Underground Server 1"
            players = 46

            if "Underground" in server_name and players > 45:
                user = await client.fetch_user(YOUR_USER_ID)
                await user.send(f"🚨 {server_name} ist online mit {players} Spielern!")

            await asyncio.sleep(60)

        except Exception as e:
            print("Monitor error:", e)
            await asyncio.sleep(10)

# ---------------- DISCORD EVENTS ----------------
@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

    # ✅ WICHTIG: neuer richtiger Weg
    asyncio.create_task(monitor())

# ---------------- START ----------------
def run_bot():
    threading.Thread(target=run_web).start()
    client.run(TOKEN)

if __name__ == "__main__":
    run_bot()
