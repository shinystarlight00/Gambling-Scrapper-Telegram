import os
import requests
import threading
import traceback
from time import sleep
from colorama import init, Fore
from dotenv import load_dotenv
from telegram import Update, Bot
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater, CallbackContext

def reset():
    print(Fore.BLUE + "Telegram failed, restarting in 10 seconds")
    print("Error Message: \n")
    print(Fore.RED + traceback.format_exc())
    sleep(20)
    os.system("pm2 restart main.py --interpreter=python3")

class Telegram:
    def __init__(self):
        # Get environment variables
        try:
            load_dotenv(dotenv_path=os.path.abspath('./.env'))
            self.TOKEN = os.getenv("TELEGRAM_API_KEY")
            self.chatID = os.getenv("TELEGRAM_CHAT_ID")
            self.endpoint = os.getenv("TELEGRAM_NOTIFICATION_ENDPOINT")

            # Optional second chat
            if os.getenv("TELEGRAM_CHAT_ID_2"): self.chatID_2 = os.getenv("TELEGRAM_CHAT_ID_2")

            self.update = Updater(self.TOKEN, use_context = True)
            self.bot = Bot(token = self.TOKEN)

            # Telegram Updater
            self.dp = self.update.dispatcher
            self.dp.add_handler(CommandHandler("start", self.start_command))
            self.dp.add_handler(CommandHandler("help", self.help_command))
            self.dp.add_handler(MessageHandler(Filters.chat_type.groups & Filters.text, self.listen_chat))
            self.update.start_polling()
        except: reset()

    def listen_chat(self, update, context):
        try:
            msg = update.message.text
            if msg == "/start": return self.start_command
            if msg == "/help": return self.help_command
        except: reset()

    def start_command(self, update: Update, context: CallbackContext):
        try: update.message.reply_text("Hi, I'm the Gambling Scraper Bot.")
        except: reset()

    def help_command(self, update: Update, context: CallbackContext):
        try:
            update.message.reply_text("""
/start: Shows welcome text
/help: Shows all commands.
            """)
        except: reset()

    def log(self, message):
        self.bot.send_message(chat_id=self.chatID, text=message)
        if (self.chatID_2): self.bot.send_message(chat_id=self.chatID_2, text=message)

    def idle(self):
        self.update.idle()

def logging():
    while True:
        try:
            sleep(7200) # 2 Hour

            try:
                status = requests.get(url = telegram.endpoint + "/get").json()
            except:
                print(traceback.format_exc())
                telegram.log("🚨🚨🚨 All of the scraper services are down!")
                sleep(20)
                continue

            if len(status.keys()) == 0:
                telegram.log("🚨🚨🚨 All of the scraper services are down!")
                sleep(20)
                continue

            for key in status.keys():
                print(key, status[key])
                if status[key]: telegram.log("✅ " + key + " service is working.")
                else: telegram.log("⚠️ " + key + " service might be down.")
        except:
            pass

if __name__ == "__main__":
    init()
    try:
        telegram = Telegram()
        telegram.log("Scraping has started, Telegram communication is active. Type /help to see all commands.")
        threading.Thread(target=logging).start()
        telegram.idle()
    except: reset()