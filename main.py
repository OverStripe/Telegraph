import telebot
import requests
import os

# Initialize the bot with your Telegram API token
bot = telebot.TeleBot('7461790177:AAFrplKOYxxAF8X-zSigAB8_zFDsORBMjm4')

# Function to upload the image to Postimages and get the URL
def upload_to_postimages(image_path):
    try:
        print(f"Uploading image to Postimages: {image_path}")
        
        # Upload the image to Postimages
        with open(image_path, 'rb') as image_file:
            files = {'file': image_file}
            data = {
                'upload_session': '',  # Empty session to avoid issues
                'expire': '0'  # Set expiration to '0' for no expiration
            }
            response = requests.post("https://postimages.org/json", data=data, files=files)
        
        # Parse the response
        if response.status_code == 200:
            json_response = response.json()
            img_url = json_response.get('url', {}).get('viewer', '')
            return img_url
        else:
            print(f"Failed to upload to Postimages. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error during upload to Postimages: {e}")
        return None

# Handle the /start command to greet the user
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Welcome! Simply upload an image, and I'll convert it to a Postimages link.")

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

        # Download the image from Telegram
        image_response = requests.get(image_url)
        if image_response.status_code != 200:
            bot.send_message(message.chat.id, "Failed to download the image. Please try again.")
            return
        
        # Save the image locally
        file_name = file_info.file_path.split('/')[-1]
        with open(file_name, 'wb') as f:
            f.write(image_response.content)
        
        # Upload to Postimages
        postimages_url = upload_to_postimages(file_name)
        
        # Clean up the local image file
        os.remove(file_name)
        
        if postimages_url:
            bot.send_message(message.chat.id, f"Here is your Postimages link: {postimages_url}")
        else:
            bot.send_message(message.chat.id, "Failed to upload the image to Postimages. Please try again.")
    except Exception as e:
        bot.send_message(message.chat.id, "An error occurred while processing the image.")
        print(f"Error: {e}")

# Start polling for messages
bot.polling()
