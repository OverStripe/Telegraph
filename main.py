# main.py

import telebot
from telegraph import Telegraph
import requests
import os

# Initialize the bot with your token and the Telegraph API
bot = telebot.TeleBot('7461790177:AAFrplKOYxxAF8X-zSigAB8_zFDsORBMjm4')
telegraph = Telegraph()
telegraph.create_account(short_name='YourBot')

# Dictionary to track users who have invoked /tgm and are waiting for image upload
user_waiting_for_image = {}

# Function to upload the image to Telegraph and get the URL
def upload_to_telegraph(image_url):
    try:
        # Download the image
        image_response = requests.get(image_url)
        file_name = image_url.split('/')[-1]
        
        # Save the image temporarily
        with open(file_name, 'wb') as f:
            f.write(image_response.content)
        
        # Check the file size (Telegraph limit is 5MB)
        if os.path.getsize(file_name) > 5 * 1024 * 1024:
            os.remove(file_name)
            return "Image exceeds the 5MB size limit."

        # Upload the image to Telegraph
        response = telegraph.upload_file(file_name)
        
        # Delete the temporary file
        os.remove(file_name)
        
        # Return the Telegraph link
        return 'https://telegra.ph/' + response[0]['src']
    except Exception as e:
        print(f"Error during upload: {e}")
        return None

# Handle the /start command to greet the user
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome! Use /tgm to convert an image to a Telegraph link.")

# Handle the /tgm command, marking the user as waiting for an image upload
@bot.message_handler(commands=['tgm'])
def request_image(message):
    user_id = message.from_user.id
    user_waiting_for_image[user_id] = True  # Mark user as waiting for image
    bot.reply_to(message, "Please upload an image, and I'll convert it to a Telegraph link.")

# Handle image uploads
@bot.message_handler(content_types=['photo'])
def handle_image(message):
    user_id = message.from_user.id

    # Check if the user previously used the /tgm command
    if user_id in user_waiting_for_image and user_waiting_for_image[user_id]:
        try:
            # Get the largest available image from the photo sizes
            file_id = message.photo[-1].file_id
            file_info = bot.get_file(file_id)
            
            # Get the full image URL
            image_url = f"https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}"
            
            # Upload to Telegraph
            telegraph_url = upload_to_telegraph(image_url)
            
            if telegraph_url:
                bot.reply_to(message, f"Here is your Telegraph link: {telegraph_url}")
            else:
                bot.reply_to(message, "Failed to upload the image to Telegraph.")
        except Exception as e:
            bot.reply_to(message, "An error occurred while processing the image.")
            print(f"Error: {e}")
        finally:
            # Reset the user's state after processing the image
            user_waiting_for_image[user_id] = False
    else:
        bot.reply_to(message, "Please use /tgm before uploading an image.")

# Start polling for messages
bot.polling()
