import os
import requests
import telebot
from flask import Flask
from threading import Thread

# ENV settings - Bot Token mathram mathi
BOT_TOKEN = os.environ.get("BOT_TOKEN")
KOYEB_API_URL = os.environ.get("API_URL", "https://top-warbler-brofbdb699965-a3727b0a.koyeb.app/bypass")

bot = telebot.TeleBot(BOT_TOKEN)
server = Flask('')

@server.route('/')
def home():
    return "Bot is Running!"

def run():
    server.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hello! Terabox link ayakkuka. 400MB-yil thazhe aanel file ayachu tharaam, illenkil direct link nalkaam.")

@bot.message_handler(func=lambda message: "terabox" in message.text or "1024tera" in message.text)
def handle_terabox(message):
    sent_msg = bot.reply_to(message, "🔍 Processing...")
    url = message.text

    try:
        # API Call
        response = requests.get(f"{KOYEB_API_URL}?url={url}")
        data = response.json()

        if data.get("status") == True:
            file_info = data["result"]["list"][0]
            file_name = file_info["server_filename"]
            direct_link = file_info["direct_link"]
            size_bytes = int(file_info["size"])
            size_mb = round(size_bytes / (1024 * 1024), 2)

            # --- CONDITION: 400MB LIMIT ---
            if size_mb > 400:
                caption = (
                    f"⚠️ **File is too large for direct send!**\n\n"
                    f"📁 **Name:** `{file_name}`\n"
                    f"📊 **Size:** {size_mb} MB\n\n"
                    f"🔗 [Direct Download Link]({direct_link})"
                )
                bot.edit_message_text(caption, message.chat.id, sent_msg.message_id, parse_mode="Markdown")
            
            else:
                bot.edit_message_text(f"📥 Downloading: `{file_name}` ({size_mb} MB)", message.chat.id, sent_msg.message_id)
                
                # Download to Disk
                with requests.get(direct_link, stream=True) as r:
                    r.raise_for_status()
                    with open(file_name, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)

                bot.edit_message_text("📤 Uploading to Telegram...", message.chat.id, sent_msg.message_id)
                
                # Uploading File
                with open(file_name, 'rb') as f:
                    bot.send_document(message.chat.id, f, caption=f"✅ **File:** `{file_name}`\n📊 **Size:** {size_mb} MB")
                
                # Cleanup
                if os.path.exists(file_name):
                    os.remove(file_name)
                bot.delete_message(message.chat.id, sent_msg.message_id)

        else:
            bot.edit_message_text("❌ Error: Bypass failed.", message.chat.id, sent_msg.message_id)

    except Exception as e:
        if 'file_name' in locals() and os.path.exists(file_name):
            os.remove(file_name)
        bot.edit_message_text(f"❌ Error: {str(e)}", message.chat.id, sent_msg.message_id)

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN ENV set cheythittilla!")
    else:
        keep_alive()
        print("Bot started!")
        bot.infinity_polling()
