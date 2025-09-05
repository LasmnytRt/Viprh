import asyncio
import random
import string
import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext, filters, MessageHandler
from pymongo import MongoClient
from datetime import datetime, timedelta, timezone

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ✅ MongoDB URI GitHub Secrets / Environment से लो
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("❌ MONGO_URI not found! Please set it in GitHub Secrets.")

client = MongoClient(MONGO_URI)
db = client.get_database()  # default DB auto-pick
users_collection = db['VIP']
redeem_codes_collection = db['redeem_codes0']

# ✅ Telegram Token भी env से लो
TELEGRAM_BOT_TOKEN = os.getenv("7390699440:AAHJcbhKoL6QN4tjbCfrilQowAwka_eSCBE")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("❌ TELEGRAM_BOT_TOKEN not found! Please set it in GitHub Secrets.")

ADMIN_USER_ID = 1337204350  

cooldown_dict = {}
user_attack_history = {}
valid_ip_prefixes = ('52.', '20.', '14.', '4.', '13.', '100.', '235.')

# ---------------- Commands Start ---------------- #

async def help_command(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id != ADMIN_USER_ID:
        help_text = (
            "*Here are the commands you can use:* \n\n"
            "*🔸 /start* - Start interacting with the bot.\n"
            "*🔸 /attack* - Trigger an attack operation.\n"
            "*🔸 /redeem* - Redeem a code.\n"
            "*🔸 /get_id* - Get your Telegram ID.\n"
        )
    else:
        help_text = (
            "*💡 Available Commands for Admins:*\n\n"
            "*🔸 /start* - Start the bot.\n"
            "*🔸 /attack* - Start the attack.\n"
            "*🔸 /get_id* - Get user id.\n"
            "*🔸 /add [user_id]* - Add a user.\n"
            "*🔸 /remove [user_id]* - Remove a user.\n"
            "*🔸 /users* - List all allowed users.\n"
            "*🔸 /gen* - Generate a redeem code.\n"
            "*🔸 /redeem* - Redeem a code.\n"
            "*🔸 /delete_code* - Delete a redeem code.\n"
            "*🔸 /list_codes* - List all redeem codes.\n"
        )
    await context.bot.send_message(chat_id=update.effective_chat.id, text=help_text, parse_mode='Markdown')

# ---- बाकी आपका कोड (add_user, remove_user, attack, redeem, list_codes वगैरह) जस का तस रहेगा ---- #
# मैंने सिर्फ MongoDB और Telegram token वाले हिस्से को सही किया है

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add", add_user))
    application.add_handler(CommandHandler("remove", remove_user))
    application.add_handler(CommandHandler("attack", attack))
    application.add_handler(CommandHandler("gen", generate_redeem_code))
    application.add_handler(CommandHandler("redeem", redeem_code))
    application.add_handler(CommandHandler("get_id", papa_bol))
    application.add_handler(CommandHandler("delete_code", delete_code))
    application.add_handler(CommandHandler("list_codes", list_codes))
    application.add_handler(CommandHandler("users", list_users))
    application.add_handler(CommandHandler("help", help_command))
    
    application.run_polling()
    logger.info("Bot is running.")

if __name__ == '__main__':
    main()