import discord
from discord.ext import commands
import os
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.command(name="ping")
async def ping(ctx):
    latency = bot.latency * 1000  # Convert to milliseconds
    await ctx.send(f"🏓 Pong! Latency is {latency:.2f} ms")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}!")

# Replace with your actual token
bot.run(os.getenv("BOT_TOKEN"))
