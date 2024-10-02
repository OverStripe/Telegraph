import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Your Bot API Key from BotFather
TELEGRAM_BOT_API_KEY = '7461790177:AAFBBQyYHxpTUnvjEXImvwbikCKIauXvalM'

# Function to handle the /start command
async def start(update: Update, context):
    await update.message.reply_text("Welcome! Send me an image and I will upload it to Catbox and return the formatted URL.")

# Function to upload image to Catbox and return the formatted link
async def handle_image(update: Update, context):
    # Get the image file from the message
    photo_file = await update.message.photo[-1].get_file()
    image_path = 'received_image.jpg'
    await photo_file.download(image_path)  # Save the image temporarily

    # Upload image to Catbox
    with open(image_path, 'rb') as image_file:
        files = {'fileToUpload': image_file}
        response = requests.post('https://catbox.moe/user/api.php', files=files, data={'reqtype': 'fileupload'})

    if response.status_code == 200:
        # Get the Catbox URL of the uploaded image
        catbox_url = response.text.strip()

        # Respond with the formatted output
        await update.message.reply_text(f"/upload {catbox_url} <character_name>")
    else:
        await update.message.reply_text("Image upload failed. Please try again.")

# Main function to set up the bot
def main():
    # Initialize the application using the updated builder pattern
    application = Application.builder().token(TELEGRAM_BOT_API_KEY).build()

    # Define command handlers
    application.add_handler(CommandHandler("start", start))

    # Define a message handler for images
    application.add_handler(MessageHandler(filters.PHOTO, handle_image))

    # Start polling
    application.run_polling()

# Entry point to run the bot
if __name__ == '__main__':
    main()
