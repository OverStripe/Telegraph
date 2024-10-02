import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import asyncio

# Your Bot API Key from BotFather
TELEGRAM_BOT_API_KEY = '7461790177:AAH59lA1Ix2AmvFf94n8ZcRsuY0QPJ5TtZU'

# Trace.moe API endpoint
TRACE_MOE_API_URL = 'https://api.trace.moe/search'

# Function to handle the /start command
async def start(update: Update, context):
    await update.message.reply_text("Welcome! Send me an anime image, and I will try to recognize the character and return the formatted URL.")

# Function to identify the character and upload the image to Catbox
async def handle_image(update: Update, context):
    # Get the image file from the message
    photo_file = await update.message.photo[-1].get_file()
    image_path = 'received_image.jpg'
    await photo_file.download(image_path)  # Save the image temporarily

    # Identify the character using Trace.moe API
    with open(image_path, 'rb') as image_file:
        response = requests.post(TRACE_MOE_API_URL, files={'image': image_file})

    if response.status_code == 200 and response.json().get('result'):
        # Get the most likely result
        result = response.json()['result'][0]
        anime_title = result.get('anime', "Unknown")
        character_name = result.get('character', "Unknown_Character")
    else:
        anime_title = "Unknown"
        character_name = "Unknown_Character"

    # Upload image to Catbox
    with open(image_path, 'rb') as image_file:
        files = {'fileToUpload': image_file}
        catbox_response = requests.post('https://catbox.moe/user/api.php', files=files, data={'reqtype': 'fileupload'})

    if catbox_response.status_code == 200:
        # Get the Catbox URL of the uploaded image
        catbox_url = catbox_response.text.strip()

        # Respond with the formatted output including the character name and anime title
        await update.message.reply_text(f"/upload {catbox_url} {character_name} ({anime_title})")
    else:
        await update.message.reply_text("Image upload failed. Please try again.")

# Main function to set up the bot
async def main():
    # Initialize the application using the updated builder pattern
    application = Application.builder().token(TELEGRAM_BOT_API_KEY).build()

    # Define command handlers
    application.add_handler(CommandHandler("start", start))

    # Define a message handler for images
    application.add_handler(MessageHandler(filters.PHOTO, handle_image))

    # Start polling (without using asyncio.run)
    application.run_polling()

# Check if an event loop is already running
if __name__ == '__main__':
    try:
        # Check if the event loop is already running
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If the loop is running, directly call main
            asyncio.ensure_future(main())
        else:
            # If no event loop is running, run normally
            loop.run_until_complete(main())
    except RuntimeError:
        # If no loop is found, create a new one and run the bot
        asyncio.run(main())
