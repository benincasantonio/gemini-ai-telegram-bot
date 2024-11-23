from telegram.ext import ApplicationBuilder
from os import getenv
from .enums import TelegramBotCommands

def set_telegram_bot_commands():
    telegram_app = ApplicationBuilder().token(getenv('TELEGRAM_BOT_TOKEN')).build()

    telegram_app.bot.set_my_commands(TelegramBotCommands.NEW_CHAT)