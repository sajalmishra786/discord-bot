import discord
from discord.ext import commands
from os import getenv

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.command(name="ping")
async def ping(ctx):
    latency = bot.latency * 1000
    await ctx.send(f"🏓 Pong! Latency is {latency:.2f} ms")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}!")

bot.run(getenv("BOT_TOKEN"))
