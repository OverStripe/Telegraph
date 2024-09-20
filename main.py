import telebot
import requests
import os

# Initialize the bot with your Telegram API token
bot = telebot.TeleBot('7461790177:AAFrplKOYxxAF8X-zSigAB8_zFDsORBMjm4')

# Function to upload the image to Catbox and get the URL
def upload_to_catbox(file_path):
    try:
        print(f"Uploading image to Catbox: {file_path}")
        
        # Prepare the files and payload for Catbox upload
        files = {'fileToUpload': open(file_path, 'rb')}
        data = {'reqtype': 'fileupload'}
        
        # Send a POST request to Catbox API
        response = requests.post("https://catbox.moe/user/api.php", files=files, data=data)
        
        # Check if the response is successful
        if response.status_code == 200:
            return response.text  # Catbox returns the URL as plain text
        else:
            print(f"Failed to upload to Catbox. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error during upload to Catbox: {e}")
        return None

# Handle the /start command to greet the user
@bot.message_handler(commands=['start'])
