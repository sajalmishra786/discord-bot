import discord
from discord.ext import commands, tasks
from datetime import datetime
import pytz
from collections import defaultdict
import os
# Channel IDs
ATTENDANCE_CHANNEL_ID = 1372554787203055726
EOD_CHANNEL_ID = 1372554764898013296
ADMIN_CHANNEL_ID = 1378605606608568382

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

attendance_log = defaultdict(list)
eod_log = defaultdict(list)

summary_message = None  # To track and update the last summary

def get_ist_time():
    return datetime.now(pytz.timezone('Asia/Kolkata'))

def format_date_key():
    return get_ist_time().strftime('%Y-%m-%d')

# Attendance View
class AttendanceView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="✅ Mark Present", style=discord.ButtonStyle.success, custom_id="mark_present")
    async def mark_present(self, interaction: discord.Interaction, button: discord.ui.Button):
        now = get_ist_time()
        date_key = format_date_key()
        entry = f"{interaction.user.mention} at `{now.strftime('%I:%M %p')}`"
        if entry not in attendance_log[date_key]:
            attendance_log[date_key].append(entry)
        await interaction.response.send_message(f"🟢 Attendance marked at `{now.strftime('%I:%M %p')} IST`!", ephemeral=True)

# EOD Modal
class ReportModal(discord.ui.Modal, title="📋 End of Day Report"):
    report = discord.ui.TextInput(label="🛠 What did you work on today?", style=discord.TextStyle.paragraph, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        now = get_ist_time()
        date_key = format_date_key()
        eod_log[date_key].append((interaction.user.mention, now.strftime('%I:%M %p'), self.report.value))
        await interaction.response.send_message(f"📨 Report submitted at `{now.strftime('%I:%M %p')} IST`!", ephemeral=True)

# EOD View
class EODView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📝 Submit EOD Report", style=discord.ButtonStyle.primary, custom_id="submit_report")
    async def submit_report(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ReportModal())

# Setup Command
@bot.command(name="setup")
@commands.has_permissions(administrator=True)
async def setup(ctx):
    attendance_channel = bot.get_channel(ATTENDANCE_CHANNEL_ID)
    eod_channel = bot.get_channel(EOD_CHANNEL_ID)

    if attendance_channel:
        await attendance_channel.send("📌 Click below to mark your attendance:", view=AttendanceView())
    if eod_channel:
        await eod_channel.send("🗓 Click below to submit your EOD report:", view=EODView())

    await ctx.send("✅ Setup complete!")
@bot.command(name="say")
@commands.is_owner()
async def say(ctx, *, message: str):
    await ctx.send(message)
# Manual summary command (if needed)
@bot.command(name="summary")
@commands.has_permissions(administrator=True)
async def summary(ctx):
    await send_summary()

# Function to generate and send the summary
async def send_summary():
    global summary_message
    date_key = format_date_key()
    attendance_entries = attendance_log.get(date_key, [])
    eod_entries = eod_log.get(date_key, [])

    embed = discord.Embed(
        title=f"📅 Summary for {date_key}",
        color=discord.Color.teal(),
        timestamp=get_ist_time()
    )

    embed.add_field(
        name="✅ Attendance",
        value="\n".join(attendance_entries) if attendance_entries else "No attendance marked.",
        inline=False
    )

    if eod_entries:
        eod_formatted = ""
        for user, time, report in eod_entries:
            eod_formatted += f"**{user}** at `{time}`\n> {report}\n\n"
        embed.add_field(name="📝 EOD Reports", value=eod_formatted, inline=False)
    else:
        embed.add_field(name="📝 EOD Reports", value="No reports submitted.", inline=False)

    admin_channel = bot.get_channel(ADMIN_CHANNEL_ID)
    if admin_channel:
        if summary_message:
            try:
                await summary_message.edit(embed=embed)
            except discord.NotFound:
                summary_message = await admin_channel.send(embed=embed)
        else:
            summary_message = await admin_channel.send(embed=embed)

# Auto summary task every 30 seconds
@tasks.loop(seconds=30)
async def auto_summary():
    await send_summary()

# Bot Ready
@bot.event
async def on_ready():
    bot.add_view(AttendanceView())
    bot.add_view(EODView())
    auto_summary.start()
    print(f"✅ Logged in as {bot.user}")


bot.run(os.getenv("BOT_TOKEN"))
