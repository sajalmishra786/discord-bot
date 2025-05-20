import discord
import os
from discord.ext import commands
from discord import app_commands

# Replace with your bot token and channel IDs
TOKEN = "YOUR_BOT_TOKEN"
ATTENDANCE_CHANNEL_ID = 1372554787203055726  # Replace with actual channel ID
EOD_CHANNEL_ID = 1372554764898013296        # Replace with actual channel ID

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# --- VIEW FOR ATTENDANCE BUTTON ---
class AttendanceView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Mark Present", style=discord.ButtonStyle.success, custom_id="mark_present")
    async def mark_present(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"✅ {interaction.user.mention}, your attendance has been marked!", ephemeral=True)

# --- MODAL FOR END OF THE DAY REPORT ---
class ReportModal(discord.ui.Modal, title="End of the Day Report"):
    report = discord.ui.TextInput(label="What did you work on today?", style=discord.TextStyle.paragraph, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"📝 Thank you {interaction.user.mention}! Your report has been submitted.", ephemeral=True)
        log_channel = bot.get_channel(EOD_CHANNEL_ID)
        if log_channel:
            await log_channel.send(f"📋 **Report from {interaction.user.mention}:**\n{self.report.value}")

# --- VIEW FOR EOD REPORT BUTTON ---
class EODView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Submit EOD Report", style=discord.ButtonStyle.primary, custom_id="submit_report")
    async def submit_report(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ReportModal())

# --- SEND SETUP MESSAGES IN CHANNELS ---
@bot.command(name="setup")
@commands.has_permissions(administrator=True)
async def setup(ctx):
    attendance_channel = bot.get_channel(ATTENDANCE_CHANNEL_ID)
    eod_channel = bot.get_channel(EOD_CHANNEL_ID)

    if attendance_channel:
        await attendance_channel.send("🎯 Click below to mark your attendance!!!", view=AttendanceView())

    if eod_channel:
        await eod_channel.send("📆 Click below to submit your end-of-day report!!", view=EODView())

    await ctx.send("✅ Setup complete!")

# --- STARTUP: Syncing persistent views ---
@bot.event
async def on_ready():
    bot.add_view(AttendanceView())
    bot.add_view(EODView())
    print(f"Logged in as {bot.user}!")

bot.run(os.getenv("BOT_TOKEN"))

