import ssl
import requests
from telegraph import Telegraph, exceptions, upload_file
from telebot import TeleBot, apihelper
import time
import os

# Initialize Telegraph API
telegraph = Telegraph()
response = telegraph.create_account(short_name='YourBot')
auth_url = response["auth_url"]

# Bot setup
API_TOKEN = '7461790177:AAFrplKOYxxAF8X-zSigAB8_zFDsORBMjm4'
bot = TeleBot(API_TOKEN)

# Function to retry requests
def retry_request(url, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise HTTPError for bad responses
            return response
        except requests.exceptions.RequestException as e:
            retries += 1
            print(f"Retry {retries}/{max_retries} failed: {e}")
            time.sleep(2)  # Wait before retrying
    raise Exception("Max retries exceeded")

# Function to download and upload image
def handle_image_download(message, file_id):
    try:
        file_info = bot.get_file(file_id)
        file_path = file_info.file_path
        file_url = f"https://api.telegram.org/file/bot{API_TOKEN}/{file_path}"
        
        # Log the URL
        print(f"Downloading image from: {file_url}")
        
        # Retry the download if there is a connection issue
        response = retry_request(file_url)
        
        # Save the image locally
        image_path = os.path.join("/tmp", file_info.file_path.split('/')[-1])
        with open(image_path, 'wb') as f:
            f.write(response.content)
        
        print(f"File size: {len(response.content) / (1024 * 1024):.2f} MB")

        # Upload to Telegraph
        print(f"Uploading {image_path} to Telegraph...")
        media_url = upload_file(image_path)
        return media_url
    except exceptions.TelegraphException as exc:
        print(f"Error during upload to Telegraph: {exc}")
        return None

# Function to handle bot messages
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome! Simply upload an image, and I'll convert it to a link using Telegraph.")

@bot.message_handler(content_types=['photo'])
def handle_photos(message):
    file_id = message.photo[-1].file_id
    media_url = handle_image_download(message, file_id)
    
    if media_url:
        bot.reply_to(message, f"Uploaded to [Telegraph](https://telegra.ph{media_url[0]})", parse_mode="Markdown")
    else:
        bot.reply_to(message, "Failed to upload the image to Telegraph.")

# Exception handling for bot blocking
@bot.message_handler(func=lambda message: True)
def default_handler(message):
    try:
        bot.reply_to(message, "Send me a photo to upload.")
    except apihelper.ApiTelegramException as e:
        if "bot was blocked by the user" in str(e):
            print(f"Bot was blocked by the user: {message.chat.id}")
        else:
            print(f"Unhandled Telegram API Exception: {e}")

# Main polling loop
if __name__ == '__main__':
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Error during polling: {e}")
