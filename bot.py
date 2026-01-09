import os
import telebot
import requests
from flask import Flask
from threading import Thread

# ENV-il ninnu data edukunnu
BOT_TOKEN = os.environ.get("BOT_TOKEN")
KOYEB_API_URL = os.environ.get("API_URL", "https://top-warbler-brofbdb699965-a3727b0a.koyeb.app/bypass")

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask('')

@app.route('/')
def home():
    return "Bot is Alive!"

# ... (baki ella functions-um pazhayathu pole thanne) ...

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN env variable set cheythittilla!")
    else:
        keep_alive()
        print("Bot is running...")
        bot.infinity_polling()
      
