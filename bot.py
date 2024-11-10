import requests
from PIL import Image
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
TELEGRAM_BOT_API_KEY = '7461790177:AAFivnngWdq2ryoxn08q_j2Degxxkk3Cjlg'

# Target 8K resolution dimensions
TARGET_WIDTH = 7680
TARGET_HEIGHT = 4320

# Function to handle the /start command
async def start(update: Update, context):
    logger.info("Received /start command")
    await update.message.reply_text("Welcome! Send me an image, and I will upscale it to 8K quality and provide a link in /upload format.")

# Function to upscale the image to 8K and upload it to Catbox
async def handle_image(update: Update, context):
    logger.info("Received an image")
    # Get the image file from the message
    photo_file = await update.message.photo[-1].get_file()
    image_path = 'received_image.jpg'
    
    # Download the image from Telegram
    await photo_file.download_to_drive(image_path)
    logger.info("Image downloaded")

    # Upscale the image to 8K using Pillow
    upscaled_image_path = 'upscaled_image_8k.jpg'
    with Image.open(image_path) as img:
        # Calculate upscale factors
        width_factor = TARGET_WIDTH / img.width
        height_factor = TARGET_HEIGHT / img.height
        upscale_factor = min(width_factor, height_factor)
        
        # Calculate new dimensions
        new_size = (int(img.width * upscale_factor), int(img.height * upscale_factor))
        upscaled_img = img.resize(new_size, Image.LANCZOS)
        
        # Save the upscaled image
        upscaled_img.save(upscaled_image_path, quality=95)
        logger.info("Image upscaled to 8K")

    # Upload the upscaled image to Catbox
    with open(upscaled_image_path, 'rb') as image_file:
        files = {'fileToUpload': image_file}
        catbox_response = requests.post('https://catbox.moe/user/api.php', files=files, data={'reqtype': 'fileupload'})

    if catbox_response.status_code == 200:
        # Successfully uploaded to Catbox
        catbox_url = catbox_response.text.strip()
        logger.info(f"Image uploaded to Catbox: {catbox_url}")
        await update.message.reply_text(f"/upload {catbox_url}")
    else:
        # Catbox upload failed
        logger.error("Image upload to Catbox failed")
        await update.message.reply_text("Image upload failed. Please try again later.")

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
