import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from datetime import datetime
from keep_alive import keep_alive

# Start keep-alive web server
keep_alive()

# Load .env for token
load_dotenv()
TOKEN = os.getenv('TOKEN')

# === CONFIG ===
TARGET_CHANNEL_IDS = [
    1388447502335868938,  # Replace with your channel IDs
]


ALLOWED_ROLES = [
    "Subutaj",
]

# === BOT SETUP ===
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.command(name='defcall')
async def attack(ctx):
    # Check if user has an allowed role
    author_roles = [role.name for role in ctx.author.roles]
    if not any(role in ALLOWED_ROLES for role in author_roles):
        await ctx.send("❌ You don't have permission to use this command.")
        return

    def check_author(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        # Ask for both coordinates in one message, format: X/Y
        await ctx.send("Enter the coordinates in the format X/Y (e.g., 123/456):")
        coords_msg = await bot.wait_for('message', check=check_author, timeout=60)
        coords = coords_msg.content.strip()

        # Parse coordinates
        try:
            x, y = [coord.strip() for coord in coords.split('/')]
        except ValueError:
            await ctx.send("❌ Invalid format! Please use the format X/Y, for example: 123/456")
            return

        # Ask only for arrival time
        await ctx.send("Enter the arrival time (format HH:mm:ss):")
        time_msg = await bot.wait_for('message', check=check_author, timeout=60)
        arrival_time = time_msg.content.strip()

        # Ask only for number of troops time
        await ctx.send("Enter the minimum number of troops ( 0 for undefined ):")
        numberOfTroops_msg = await bot.wait_for('message', check=check_author, timeout=60)
        troops = numberOfTroops_msg.content.strip()

        # Convert troops to int for comparison, but keep original string for display if needed
        troops_int = int(troops)

        # Build minimum troops line separately for clarity
        if troops_int == 0:
            min_troops_line = ":shield: Minimum troops: Not specified\n\n"
        else:
            min_troops_line = f":shield: Minimum troops: **{troops}**\n\n"

        # Build final message
        final_message = (
            "------------------------------------------\n"
            "🚨 **Incoming Attack!** 🚨\n\n"
            f"Coordinates: **{x} | {y}**\n"
            f"Arrival Time Before **{arrival_time}**\n"
            f"{min_troops_line}"
            f"⚔️ Please send reinforcements now!\n"
            f":arrow_forward: [Open Map](https://ts7.x1.international.travian.com/karte.php?x={x}&y={y})\n"
            f":arrow_forward: https://ts7.x1.international.travian.com/karte.php?x={x}&y={y}"
        )

        for channel_id in TARGET_CHANNEL_IDS:
            channel = bot.get_channel(channel_id)
            if channel is None:
                print(f"Channel ID {channel_id} not found.")
                continue
            permissions = channel.permissions_for(channel.guild.me)
            if not permissions.send_messages:
                print(f"Bot lacks send_messages permission in channel {channel.name} ({channel.id})")

        # Send to all target channels
        for channel_id in TARGET_CHANNEL_IDS:
            channel = bot.get_channel(channel_id)
            if channel:
                await channel.send(final_message)
            else:
                print(f"Channel ID {channel_id} not found.")

        await ctx.send("✅ Defense call sent!")

    except Exception as e:
        await ctx.send(f"❌ Something went wrong: {e}")


bot.run(TOKEN)
