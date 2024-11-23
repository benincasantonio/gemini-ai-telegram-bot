from enum import Enum

class TelegramBotCommands(str, Enum):
    START = "/start"
    NEW_CHAT = "/new_chat"