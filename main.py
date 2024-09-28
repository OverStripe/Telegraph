import telebot
import requests
import os
import sqlite3
from telegraph import Telegraph
from datetime import datetime

# Initialize the bot with your Telegram API token
bot = telebot.TeleBot('7461790177:AAERCiMrYi9uK0mCQ7Stkvylw1MeRmDdqgY')

# Initialize Telegraph API
telegraph = Telegraph()
telegraph.create_account(short_name='image_bot')

# Connect to SQLite database (or create if it doesn't exist)
conn = sqlite3.connect('bot_data.db', check_same_thread=False)
cursor = conn.cursor()

# Create a table for storing user data and image links
cursor.execute('''CREATE TABLE IF NOT EXISTS user_images (
                    user_id INTEGER,
                    catbox_url TEXT,
                    telegraph_url TEXT,
                    timestamp DATETIME
                )''')
conn.commit()

# Function to upload the image to Catbox and get the URL
def upload_to_catbox(file_path):
    try:
        print(f"Uploading image to Catbox: {file_path}")
        with open(file_path, 'rb') as file_to_upload:
            files = {'fileToUpload': file_to_upload}
            data = {'reqtype': 'fileupload'}
            response = requests.post("https://catbox.moe/user/api.php", files=files, data=data)
        if response.status_code == 200:
            return response.text
        else:
            print(f"Failed to upload to Catbox. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error during upload to Catbox: {e}")
        return None

# Function to create a Telegraph page with the image
def create_telegraph_page(image_url):
    try:
        response = telegraph.create_page(
            title='Image from Bot',
            content=f'<img src="{image_url}"/>'
        )
        return f"https://telegra.ph/{response['path']}"
    except Exception as e:
        print(f"Error creating Telegraph page: {e}")
        return None

# Save the last uploaded image for the user
def save_image_data(user_id, catbox_url, telegraph_url):
    cursor.execute('INSERT INTO user_images (user_id, catbox_url, telegraph_url, timestamp) VALUES (?, ?, ?, ?)',
                   (user_id, catbox_url, telegraph_url, datetime.now()))
    conn.commit()

# Retrieve the last image uploaded by the user
def get_last_image(user_id):
    cursor.execute('SELECT catbox_url, telegraph_url FROM user_images WHERE user_id = ? ORDER BY timestamp DESC LIMIT 1', (user_id,))
    return cursor.fetchone()

# Handle the /start command to greet the user and show available commands
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "Welcome! Here's what you can do:\n"
        "/start - Welcome message and available commands\n"
        "/cmds - List of commands\n"
        "/last_image - Retrieve the last image you uploaded\n"
        "Upload an image, and I'll upload it to Catbox and create a Telegraph page!"
    )
    bot.send_message(message.chat.id, welcome_text)

# Handle the /cmds command to list available commands
@bot.message_handler(commands=['cmds'])
def list_commands(message):
    commands_text = (
        "Available commands:\n"
        "/start - Welcome message and commands\n"
        "/cmds - List of commands\n"
        "/last_image - Retrieve the last image you uploaded\n"
        "Simply upload an image, and I'll upload it to Catbox and create a Telegraph page."
    )
    bot.send_message(message.chat.id, commands_text)

# Handle the /last_image command to return the last image uploaded by the user
@bot.message_handler(commands=['last_image'])
def send_last_image(message):
    user_id = message.from_user.id
    last_image = get_last_image(user_id)
    if last_image:
        catbox_url, telegraph_url = last_image
        bot.send_message(message.chat.id, f"Here is your last image:\nCatbox URL: {catbox_url}\nTelegraph URL: {telegraph_url}")
    else:
        bot.send_message(message.chat.id, "You haven't uploaded any images yet.")

# Handle image uploads automatically
@bot.message_handler(content_types=['photo'])
def handle_image(message):
    try:
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        image_url = f"https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}"
        print(f"Image URL from Telegram: {image_url}")

        # Download the image from Telegram
        image_response = requests.get(image_url)
        if image_response.status_code != 200:
            bot.send_message(message.chat.id, "Failed to download the image. Please try again.")
            return
        
        file_name = file_info.file_path.split('/')[-1]
        with open(file_name, 'wb') as f:
            f.write(image_response.content)
        
        # Upload to Catbox
        catbox_url = upload_to_catbox(file_name)
        os.remove(file_name)
        
        if catbox_url:
            # Create a Telegraph page
            telegraph_url = create_telegraph_page(catbox_url)
            if telegraph_url:
                bot.send_message(message.chat.id, f"Here is your Telegraph page: {telegraph_url}")
                save_image_data(message.from_user.id, catbox_url, telegraph_url)
            else:
                bot.send_message(message.chat.id, "Failed to create the Telegraph page. Please try again.")
        else:
            bot.send_message(message.chat.id, "Failed to upload the image to Catbox. Please try again.")
    except Exception as e:
        bot.send_message(message.chat.id, "An error occurred while processing the image.")
        print(f"Error: {e}")

# Start polling for messages
bot.polling()
