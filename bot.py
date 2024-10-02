import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import logging

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Your Bot API Key from BotFather
TELEGRAM_BOT_API_KEY = '7461790177:AAGQn4dUWQsdpiCrJX2YqI8iSw5CRGg-aOw'
# DeepAI API Key
DEEPAI_API_KEY = '896d15c1-2f42-4e5f-ab5c-dbf7ffdf137f'

# Function to handle the /start command
async def start(update: Update, context):
    logger.info("Received /start command")
    await update.message.reply_text("Welcome! Send me an image and I will upscale and upload it to Catbox.")

# Function to upscale and upload the image to Catbox and return the formatted link
async def handle_image(update: Update, context):
    logger.info("Received an image")
    # Get the image file from the message
    photo_file = await update.message.photo[-1].get_file()
    image_path = 'received_image.jpg'
    
    # Download the image from Telegram
    await photo_file.download_to_drive(image_path)
    logger.info("Image downloaded")

    # Upscale the image using DeepAI API
    logger.info("Upscaling image with DeepAI...")
    with open(image_path, 'rb') as image_file:
        response = requests.post(
            'https://api.deepai.org/api/torch-srgan',
            files={'image': image_file},
            headers={'api-key': DEEPAI_API_KEY}
        )

    if response.status_code == 200:
        upscaled_image_url = response.json().get('output_url')
        logger.info(f"Image upscaled: {upscaled_image_url}")

        # Download the upscaled image
        upscaled_image = requests.get(upscaled_image_url)
        upscaled_image_path = 'upscaled_image.jpg'
        with open(upscaled_image_path, 'wb') as f:
            f.write(upscaled_image.content)

        # Upload the upscaled image to Catbox
        with open(upscaled_image_path, 'rb') as image_file:
            files = {'fileToUpload': image_file}
            catbox_response = requests.post('https://catbox.moe/user/api.php', files=files, data={'reqtype': 'fileupload'})

        if catbox_response.status_code == 200:
            # Get the Catbox URL of the uploaded image
            catbox_url = catbox_response.text.strip()
            logger.info(f"Image uploaded to Catbox: {catbox_url}")

            # Respond with the formatted output
            await update.message.reply_text(f"/upload {catbox_url} <character_name>")
        else:
            logger.error("Image upload to Catbox failed")
            await update.message.reply_text("Upscaled image upload failed. Please try again.")
    else:
        logger.error("Image upscaling failed")
        await update.message.reply_text("Image upscaling failed. Please try again.")

# Main function to set up the bot
def main():
    # Initialize the application using the updated builder pattern
    application = Application.builder().token(TELEGRAM_BOT_API_KEY).build()

    # Define command handlers
    application.add_handler(CommandHandler("start", start))

    # Define a message handler for images
    application.add_handler(MessageHandler(filters.PHOTO, handle_image))

    # Start polling
    logger.info("Bot started, waiting for updates...")
    application.run_polling()

# Entry point to run the bot
if __name__ == '__main__':
    main()
