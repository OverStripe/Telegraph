import telebot
from telegraph import Telegraph
import requests
import os

# Initialize the bot with your Telegram API token and the Telegraph API
bot = telebot.TeleBot('7461790177:AAFrplKOYxxAF8X-zSigAB8_zFDsORBMjm4')
telegraph = Telegraph()
telegraph.create_account(short_name='YourBot')

# Function to upload the image to Telegraph and get the URL
def upload_to_telegraph(image_url):
    try:
        print(f"Downloading image from: {image_url}")
        image_response = requests.get(image_url)
        if image_response.status_code != 200:
            print(f"Failed to download image from Telegram. Status code: {image_response.status_code}")
            return None

        file_name = image_url.split('/')[-1]
        
        # Save the image temporarily
        with open(file_name, 'wb') as f:
            f.write(image_response.content)
        
        # Check the file size (Telegraph limit is 5MB)
        file_size = os.path.getsize(file_name)
        print(f"File size: {file_size / (1024 * 1024):.2f} MB")

        if file_size > 5 * 1024 * 1024:
            print("File is too large for Telegraph (exceeds 5MB limit).")
            os.remove(file_name)
            return "Image exceeds the 5MB size limit."

        # Upload the image to Telegraph
        print(f"Uploading {file_name} to Telegraph...")
        response = telegraph.upload_file(file_name)
        print(f"Telegraph response: {response}")
        
        # Delete the temporary file
        os.remove(file_name)

        # Return the Telegraph link
        return 'https://telegra.ph/' + response[0]['src']
    except Exception as e:
        print(f"Error during upload to Telegraph: {e}")
        return None

# Handle the /start command to greet the user
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome! Simply upload an image, and I'll convert it to a Telegraph link.")

# Handle image uploads automatically
@bot.message_handler(content_types=['photo'])
def handle_image(message):
    try:
        # Get the largest available image from the photo sizes
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        
        # Get the full image URL
        image_url = f"https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}"
        print(f"Image URL from Telegram: {image_url}")

        # Try to upload to Telegraph
        telegraph_url = upload_to_telegraph(image_url)
        
        if telegraph_url:
            bot.reply_to(message, f"Here is your Telegraph link: {telegraph_url}")
        else:
            bot.reply_to(message, "Failed to upload the image to Telegraph. Please try again.")
    except Exception as e:
        bot.reply_to(message, "An error occurred while processing the image.")
        print(f"Error: {e}")

# Start polling for messages
bot.polling()
