import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
load_dotenv()

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

@bot.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("Slash commands synced.")

@tree.command(name="ping", description="Replies with Pong!")
async def ping_command(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")

import os
bot.run(os.getenv("DISCORD_TOKEN"))
