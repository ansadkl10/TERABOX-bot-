import os
import requests
from pyrogram import Client, filters
from flask import Flask
from threading import Thread

# ENV settings
BOT_TOKEN = os.environ.get("BOT_TOKEN")
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
KOYEB_API_URL = os.environ.get("API_URL", "https://top-warbler-brofbdb699965-a3727b0a.koyeb.app/bypass")

app = Client("terabox_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
server = Flask('')

@server.route('/')
def home():
    return "Bot is Running!"

def run():
    server.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("Hello! Terabox link ayakkuka. 400MB-yil thazhe aanel file ayachu tharaam, illenkil direct link nalkaam.")

@app.on_message(filters.regex(r'https?://.*terabox.*|https?://.*1024tera.*'))
async def handle_link(client, message):
    msg = await message.reply_text("🔍 Processing...")
    terabox_url = message.text

    try:
        # API Call to Koyeb
        response = requests.get(f"{KOYEB_API_URL}?url={terabox_url}")
        data = response.json()

        if data.get("status"):
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
                await msg.edit_text(caption)
            
            else:
                await msg.edit_text(f"📥 Downloading: `{file_name}` ({size_mb} MB)")
                
                # Streaming Download to Disk
                with requests.get(direct_link, stream=True) as r:
                    with open(file_name, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)

                await msg.edit_text("📤 Uploading to Telegram...")
                await message.reply_document(
                    document=file_name,
                    caption=f"✅ **File:** `{file_name}`\n📊 **Size:** {size_mb} MB"
                )
                
                # Cleanup
                if os.path.exists(file_name):
                    os.remove(file_name)
                await msg.delete()

        else:
            await msg.edit_text("❌ Error: Bypass failed.")

    except Exception as e:
        if 'file_name' in locals() and os.path.exists(file_name):
            os.remove(file_name)
        await msg.edit_text(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    keep_alive()
    print("Bot started!")
    app.run()
