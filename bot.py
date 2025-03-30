import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv

import pytesseract
from PIL import Image
import requests
from io import BytesIO
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.attachments:
        for attachment in message.attachments:
            if attachment.filename.lower().endswith((".png", ".jpg", ".jpeg")):
                await message.channel.send("🖼️ Image received. Extracting text...")

                img_data = await attachment.read()
                img = Image.open(BytesIO(img_data))

                extracted_text = pytesseract.image_to_string(img)

                if extracted_text.strip():
                    await message.channel.send(f"📄 Extracted Text:\n```{extracted_text[:1900]}```")
                else:
                    await message.channel.send("❌ No readable text found.")

    await bot.process_commands(message)



@bot.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("Slash commands synced.")

@tree.command(name="ping", description="Replies with Pong!")
async def ping_command(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")

bot.run(os.getenv("DISCORD_TOKEN"))
