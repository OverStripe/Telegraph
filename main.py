import telebot
from telegraph import Telegraph
import requests
import os

# Initialize the bot with your token and the Telegraph API
bot = telebot.TeleBot('7461790177:AAFrplKOYxxAF8X-zSigAB8_zFDsORBMjm4')
telegraph = Telegraph()
telegraph.create_account(short_name='YourBot')

# Function to upload the image to Telegraph and get the URL
def upload_to_telegraph(image_url):
    image_response = requests.get(image_url)
    file_name = image_url.split('/')[-1]
    
    # Save the image temporarily
    with open(file_name, 'wb') as f:
        f.write(image_response.content)
    
    # Upload the image to Telegraph
    response = telegraph.upload_file(file_name)
    
    # Delete the temporary file
    os.remove(file_name)
    
    # Return the Telegraph link
    return 'https://telegra.ph/' + response[0]['src']

# Handle the /start command to greet the user
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome! Upload an image, and I'll convert it to a Telegraph link.")

# Handle image uploads
@bot.message_handler(content_types=['photo'])
def handle_image(message):
    # Get the largest available image from the photo sizes
    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    
    # Get the full image URL
    image_url = f"https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}"
    
    # Upload to Telegraph
    try:
        telegraph_url = upload_to_telegraph(image_url)
        bot.reply_to(message, f"Here is your Telegraph link: {telegraph_url}")
    except Exception as e:
        bot.reply_to(message, "An error occurred while uploading the image.")
        print(e)

# Start polling for messages
bot.polling()

