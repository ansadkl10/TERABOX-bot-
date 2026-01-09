import os
import telebot
import requests
from flask import Flask
from threading import Thread

# ENV-ൽ നിന്ന് ഡാറ്റ എടുക്കുന്നു
BOT_TOKEN = os.environ.get("BOT_TOKEN")
KOYEB_API_URL = os.environ.get("API_URL", "https://top-warbler-brofbdb699965-a3727b0a.koyeb.app/bypass")

bot = telebot.TeleBot(BOT_TOKEN)
server = Flask('')

@server.route('/')
def home():
    return "Bot is Alive!"

def run():
    server.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hello! Terabox link അയച്ചു തരൂ, ഞാൻ bypass ചെയ്ത് തരാം.")

@bot.message_handler(func=lambda message: "terabox" in message.text or "1024tera" in message.text)
def handle_terabox(message):
    sent_msg = bot.reply_to(message, "Processing... Please wait.")
    url = message.text

    try:
        response = requests.get(f"{KOYEB_API_URL}?url={url}")
        data = response.json()

        if data.get("status") == True:
            file_info = data["result"]["list"][0]
            file_name = file_info["server_filename"]
            direct_link = file_info["direct_link"]
            
            caption = f"✅ **File Found!**\n\n**Name:** `{file_name}`\n\n[Click here to Download]({direct_link})"
            bot.edit_message_text(caption, message.chat.id, sent_msg.message_id, parse_mode="Markdown")
        else:
            bot.edit_message_text("Sorry, link bypass ചെയ്യാൻ പറ്റിയില്ല.", message.chat.id, sent_msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"Error: {str(e)}", message.chat.id, sent_msg.message_id)

# പ്രധാനപ്പെട്ട ഭാഗം: ഇവിടെയാണ് ബോട്ട് സ്റ്റാർട്ട് ചെയ്യുന്നത്
if __name__ == "__main__":
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN env variable set ചെയ്തിട്ടില്ല!")
    else:
        keep_alive() # ഇപ്പോൾ ഈ ഫങ്ക്ഷൻ മുകളിൽ ഉള്ളതുകൊണ്ട് Error വരില്ല
        print("Bot is running...")
        bot.infinity_polling()
