import os
import discord
from discord.ext import commands, tasks
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot läuft"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# 🔐 SAFE: kommt aus Render ENV
USER_ID = int(os.environ["USER_ID"])


def get_server():
    return {"name": "Underground", "players": 50}


@tasks.loop(seconds=60)
async def check():
    data = get_server()

    if data["players"] > 45:
        user = await bot.fetch_user(USER_ID)
        await user.send(
            f"🚨 Server Alert: {data['players']} Players"
        )


@bot.event
async def on_ready():
    print("Bot ready")
    check.start()


if __name__ == "__main__":
    import threading
    threading.Thread(target=run_web).start()

    bot.run(os.environ["TOKEN"])
