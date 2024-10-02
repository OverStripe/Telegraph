import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Your Bot API Key from BotFather
TELEGRAM_BOT_API_KEY = '7461790177:AAHh5a1DdjfajhppuFcsNV_b9Siuos0vJT8'

# Function to handle the /start command
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Welcome! Send me an image and I will upload it to Catbox and return the formatted URL.")

# Function to upload image to Catbox and return the formatted link
def handle_image(update: Update, context: CallbackContext):
    # Get the image file from the message
    photo_file = update.message.photo[-1].get_file()
    photo_file.download('received_image.jpg')  # Save the image temporarily

    # Upload image to Catbox
    with open('received_image.jpg', 'rb') as image_file:
        files = {'fileToUpload': image_file}
        response = requests.post('https://catbox.moe/user/api.php', files=files, data={'reqtype': 'fileupload'})

    if response.status_code == 200:
        # Get the Catbox URL of the uploaded image
        catbox_url = response.text.strip()

        # Respond with the formatted output
        update.message.reply_text(f"/upload {catbox_url} <character_name>")
    else:
        update.message.reply_text("Image upload failed. Please try again.")

# Main function to set up the bot
def main():
    # Initialize the updater and dispatcher with your bot's API key
    updater = Updater(TELEGRAM_BOT_API_KEY, use_context=True)
    dp = updater.dispatcher

    # Define command handlers
    dp.add_handler(CommandHandler("start", start))

    # Define a message handler for images
    dp.add_handler(MessageHandler(Filters.photo, handle_image))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
