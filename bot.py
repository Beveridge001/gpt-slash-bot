import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv

from openai import OpenAI
import requests
from io import BytesIO
from PIL import Image

load_dotenv()

client = OpenAI()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

@bot.event
async def on_message(message):
    print("OCR key used:", os.getenv("OCR_SPACE_API_KEY"))

    if message.author == bot.user:
        return

    if message.attachments:
        for attachment in message.attachments:
            if attachment.filename.lower().endswith((".png", ".jpg", ".jpeg")):
                await message.channel.send("🖼️ Image received. Extracting text...")

                img_data = await attachment.read()
                image_file = BytesIO(img_data)

                response = requests.post(
                    "https://api.ocr.space/parse/image",
                    files={"filename": image_file},
                    data={
    "apikey": os.getenv("OCR_SPACE_API_KEY"),
    "language": "eng",
    "isOverlayRequired": False
},

                    headers={"User-Agent": "Mozilla/5.0"}
                )

print("OCR response status:", response.status_code)
print("OCR raw response:", response.text)

                try:
                    result = response.json()
                    if isinstance(result, str):
                        await message.channel.send("⚠️ OCR API returned text, not JSON. Check your API key or usage limit.")
                        return

                    if result.get("IsErroredOnProcessing"):
                        await message.channel.send("❌ OCR failed.")
                    else:
                        parsed_text = result["ParsedResults"][0]["ParsedText"]
                        if parsed_text.strip():
                            await message.channel.send(f"📄 Extracted Text:\n```{parsed_text[:1900]}```")
                        else:
                            await message.channel.send("❌ No readable text found.")
                except Exception as e:
                    await message.channel.send(f"⚠️ Error processing image: {e}")

    await bot.process_commands(message)


@bot.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("Slash commands synced.")

@tree.command(name="ping", description="Replies with Pong!")
async def ping_command(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")

@tree.command(name="chat", description="Talk to ChatGPT")
@app_commands.describe(message="Your message to ChatGPT")
async def chat_command(interaction: discord.Interaction, message: str):
    await interaction.response.defer()
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message}]
        )
        reply = response.choices[0].message.content
    except Exception as e:
        reply = f"⚠️ OpenAI error: {e}"

    await interaction.followup.send(reply)

bot.run(os.getenv("DISCORD_TOKEN"))
