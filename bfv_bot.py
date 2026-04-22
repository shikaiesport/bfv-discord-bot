import os
import discord
from discord.ext import commands, tasks
from flask import Flask

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

# 👉 DEINE DISCORD USER ID HIER EINTRAGEN
YOUR_USER_ID = 123456789012345678  # <-- ersetzen!


# ---------------- SERVER DATEN (PLACEHOLDER) ----------------
def get_server_data():
    # 🔴 HIER deine echte BFV API rein
    return {
        "name": "Underground Server",
        "players": 50
    }


# ---------------- CHECK LOOP ----------------
@tasks.loop(seconds=60)
async def check_servers():
    data = get_server_data()

    if data["players"] > 45:
        user = await bot.fetch_user(YOUR_USER_ID)

        await user.send(
            f"🚨 **BFV ALERT!**\n"
            f"Server: {data['name']}\n"
            f"👥 Spieler: {data['players']} (>45)"
        )


# ---------------- READY ----------------
@bot.event
async def on_ready():
    print(f"✅ Online als {bot.user}")
    check_servers.start()


# ---------------- TEST COMMAND ----------------
@bot.command()
async def test(ctx):
    await ctx.send("Bot läuft!")


# ---------------- START ----------------
if __name__ == "__main__":
    import threading
    threading.Thread(target=run_web).start()

    bot.run(os.environ["TOKEN"])
