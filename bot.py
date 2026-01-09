import os
import requests
import telebot
from flask import Flask
from threading import Thread

# ENV settings
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
    bot.reply_to(message, "👋 Hello! Terabox link ayakkuka.\n\n✅ 400MB-yil thazhe ulla video direct ayachu tharaam.\n✅ Athil kooduthal aanel direct download link nalkaam.")

@bot.message_handler(func=lambda message: "terabox" in message.text or "1024tera" in message.text)
def handle_terabox(message):
    sent_msg = bot.reply_to(message, "🔍 Processing your link...")
    url = message.text

    try:
        # Calling your Koyeb API
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
                    f"⚠️ **File is too large (400MB+)!**\n\n"
                    f"📁 **Name:** `{file_name}`\n"
                    f"📊 **Size:** {size_mb} MB\n\n"
                    f"🔗 [Direct Download Link]({direct_link})"
                )
                bot.edit_message_text(caption, message.chat.id, sent_msg.message_id, parse_mode="Markdown")
            
            else:
                bot.edit_message_text(f"📥 Downloading: `{file_name}`\n📊 Size: {size_mb} MB", message.chat.id, sent_msg.message_id)
                
                # Streaming Download to Disk
                with requests.get(direct_link, stream=True) as r:
                    r.raise_for_status()
                    with open(file_name, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)

                bot.edit_message_text("📤 Uploading as Video...", message.chat.id, sent_msg.message_id)
                
                # Video Extensions Check
                video_exts = ['.mp4', '.mkv', '.mov', '.avi', '.webm']
                is_video = any(file_name.lower().endswith(ext) for ext in video_exts)

                with open(file_name, 'rb') as f:
                    if is_video:
                        bot.send_video(
                            message.chat.id, 
                            f, 
                            caption=f"✅ **Video:** `{file_name}`\n📊 **Size:** {size_mb} MB",
                            supports_streaming=True
                        )
                    else:
                        bot.send_document(
                            message.chat.id, 
                            f, 
                            caption=f"✅ **File:** `{file_name}`\n📊 **Size:** {size_mb} MB"
                        )
                
                # Cleanup local file
                if os.path.exists(file_name):
                    os.remove(file_name)
                bot.delete_message(message.chat.id, sent_msg.message_id)

        else:
            bot.edit_message_text("❌ Error: Link bypass cheyyan pattiyilla.", message.chat.id, sent_msg.message_id)

    except Exception as e:
        if 'file_name' in locals() and os.path.exists(file_name):
            os.remove(file_name)
        bot.edit_message_text(f"❌ Error: {str(e)}", message.chat.id, sent_msg.message_id)

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN is missing in Environment Variables!")
    else:
        keep_alive()
        print("Bot is alive and polling...")
        bot.infinity_polling()
