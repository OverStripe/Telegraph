import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import logging
from PIL import Image
import subprocess
import os

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Your Bot API Key from BotFather
TELEGRAM_BOT_API_KEY = '7461790177:AAEtu6bGnTMhH4tmszva7zDaJ3ebRq3xcXE'

# Paths for Real-ESRGAN
REAL_ESRGAN_EXECUTABLE = './realesrgan-ncnn-vulkan'  # Adjust to your executable's path
MODEL_PATH = './models'

# Function to handle the /start command
async def start(update: Update, context):
    logger.info("Received /start command")
    await update.message.reply_text(
        "Welcome! Send me an image, and I will upscale it to 8K quality using advanced AI models and provide a link in /upload format."
    )

# Function to upscale the image using Real-ESRGAN
def upscale_with_realesrgan(input_path, output_path, scale=4):
    try:
        # Run the Real-ESRGAN command
        command = [
            REAL_ESRGAN_EXECUTABLE,
            '-i', input_path,
            '-o', output_path,
            '-s', str(scale),
            '-n', 'realesrgan-x4plus'  # Using the x4 model for high-quality results
        ]
        subprocess.run(command, check=True)
        logger.info("Image upscaled using Real-ESRGAN")
    except Exception as e:
        logger.error(f"Real-ESRGAN upscaling failed: {e}")
        raise RuntimeError("Upscaling failed using Real-ESRGAN")

# Function to handle image messages
async def handle_image(update: Update, context):
    logger.info("Received an image")
    # Get the image file from the message
    photo_file = await update.message.photo[-1].get_file()
    image_path = 'received_image.jpg'

    # Download the image from Telegram
    await photo_file.download_to_drive(image_path)
    logger.info("Image downloaded")

    # Prepare paths for the upscaled image
    upscaled_image_path = 'upscaled_image.jpg'

    try:
        # Perform upscaling using Real-ESRGAN
        upscale_with_realesrgan(image_path, upscaled_image_path, scale=4)

        # Upload the upscaled image to Catbox
        with open(upscaled_image_path, 'rb') as image_file:
            files = {'fileToUpload': image_file}
            catbox_response = requests.post(
                'https://catbox.moe/user/api.php',
                files=files,
                data={'reqtype': 'fileupload'}
            )

        if catbox_response.status_code == 200:
            # Successfully uploaded to Catbox
            catbox_url = catbox_response.text.strip()
            logger.info(f"Image uploaded to Catbox: {catbox_url}")
            await update.message.reply_text(f"/upload {catbox_url}")
        else:
            # Catbox upload failed
            logger.error("Image upload to Catbox failed")
            await update.message.reply_text("Image upload failed. Please try again later.")
    except Exception as e:
        logger.error(f"Error during image processing: {e}")
        await update.message.reply_text("Failed to process the image. Please try again later.")

    # Clean up temporary files
    if os.path.exists(image_path):
        os.remove(image_path)
    if os.path.exists(upscaled_image_path):
        os.remove(upscaled_image_path)

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
