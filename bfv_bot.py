import os
import discord
from discord.ext import commands, tasks
from flask import Flask
import requests

# ---------------- FLASK (Render Pflicht) ----------------
app = Flask(__name__)

@app.route("/")
def home():
    return "BFV Bot läuft"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


# ---------------- DISCORD ----------------
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# 👉 HIER SPEICHERN WIR DEN CHANNEL
ALERT_CHANNEL_ID = None

# ---------------- BEISPIEL SERVER DATEN ----------------
def get_server_data():
    """
    🔴 HIER kommt deine echte BFV API rein
    """
    # Beispiel Fake-Daten (ersetzen!)
    return {
        "name": "Underground Server",
        "players": 50
    }


# ---------------- ALERT LOOP ----------------
@tasks.loop(seconds=60)  # alle 60 Sekunden prüfen
async def check_servers():
    global ALERT_CHANNEL_ID

    if ALERT_CHANNEL_ID is None:
        return

    channel = bot.get_channel(ALERT_CHANNEL_ID)
    if not channel:
        return

    data = get_server_data()

    if data["players"] > 45:
        await channel.send(
            f"🚨 **ALERT!**\n"
            f"Server: {data['name']}\n"
            f"👥 Spieler: {data['players']} (>45!)"
        )


# ---------------- EVENTS ----------------
@bot.event
async def on_ready():
    print(f"✅ Eingeloggt als {bot.user}")
    check_servers.start()


# ---------------- COMMANDS ----------------
@bot.command()
async def setchannel(ctx):
    """Setzt den Alert Channel"""
    global ALERT_CHANNEL_ID
    ALERT_CHANNEL_ID = ctx.channel.id
    await ctx.send("✅ Alert Channel gesetzt!")


@bot.command()
async def test(ctx):
    await ctx.send("🔧 Bot funktioniert!")


# ---------------- START ----------------
if __name__ == "__main__":
    import threading
    threading.Thread(target=run_web).start()

    bot.run(os.environ["TOKEN"])
