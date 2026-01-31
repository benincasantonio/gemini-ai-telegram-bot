from dotenv import load_dotenv
from flask import request
from .gemini import Gemini
from md2tgmd import escape
from telegram.ext import ApplicationBuilder
from telegram import Update
from os import getenv
from io import BytesIO
from PIL import Image
from .enums import TelegramBotCommands
from .flask_app import app, db, ChatSession
from .chat_service import ChatService
import atexit
import asyncio

load_dotenv()

chat_service = ChatService()
gemini = None

_telegram_app = None


def cleanup_resources():
    """Cleanup resources on application shutdown.

    This function is called automatically when the application exits
    to ensure all HTTP connections are properly closed.

    Note: This runs in a synchronous context (atexit) where there may be
    no running event loop, so we create a new one if needed.
    """
    try:
        # Try to get the current event loop, but it may not exist
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # No running loop, create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(Gemini.close_plugins())
            finally:
                loop.close()
        else:
            # There's a running loop (shouldn't happen in atexit, but handle it)
            # We can't block on it, so just create a task
            loop.create_task(Gemini.close_plugins())
    except Exception as e:
        print(f"Error during cleanup: {e}")


# Register cleanup function to run on exit
atexit.register(cleanup_resources)

def get_telegram_app():
    global _telegram_app

    if _telegram_app is None:
        _telegram_app = ApplicationBuilder().token(getenv('TELEGRAM_BOT_TOKEN')).build()

    return _telegram_app

def get_gemini():
    global gemini

    if gemini is None:
        gemini = Gemini()
        
    return gemini



@app.get('/')
def hello_world():
    return 'Hello, World!'


@app.post('/webhook')
async def webhook():
    chat_id = None

    telegram_app = get_telegram_app()
    gemini_instance = get_gemini()

    enable_secure_webhook_token = getenv('ENABLE_SECURE_WEBHOOK_TOKEN') in ('True', None)

    try:
        body = request.get_json()

        update = Update.de_json(body, telegram_app.bot)

        chat_id = update.message.chat_id

        if enable_secure_webhook_token:
            headers_secret_token = request.headers.get('X-Telegram-Bot-Api-Secret-Token')
            secret_token = getenv('TELEGRAM_WEBHOOK_SECRET')
            if headers_secret_token != secret_token or headers_secret_token is None:
                await telegram_app.bot.send_message(chat_id=chat_id, text="You are not authorized to access this service.")
                return 'OK'

        session = db.session.query(ChatSession).filter_by(chat_id=chat_id).first()

        if not session:
            session = ChatSession(chat_id=chat_id, messages=[])
            db.session.add(session)
            db.session.commit()
        

        if update.edited_message:
            return 'OK'        
        if update.message.text == TelegramBotCommands.START:
            await telegram_app.bot.send_message(chat_id=chat_id, text="Welcome to Gemini Bot. Send me a message or an image to get started.")
            return 'OK'
        if update.message.text == TelegramBotCommands.NEW_CHAT:
            chat_service.clear_chat_history(session.id)

            await telegram_app.bot.send_message(chat_id=chat_id, text="New chat started.")
            return 'OK'
        else:
            message = await telegram_app.bot.send_message(chat_id=chat_id, text="Processing your request...")
            message_id = message.message_id

        history = chat_service.get_chat_history(session.id)

        if update.message.photo:
            
            app.logger.info("Image received")
            
            file_id = update.message.photo[-1].file_id

            app.logger.info("Image file id: " + str(file_id))

            file = await telegram_app.bot.get_file(file_id)
            bytes_array = await file.download_as_bytearray()
            bytesIO = BytesIO(bytes_array)
            image = Image.open(bytesIO)
            app.logger.info("Image loaded")

            prompt = 'Describe the image'

            if update.message.caption:
                prompt = update.message.caption
            print("Prompt is ", prompt)
            chat = await gemini_instance.get_chat(history=history)
            text = await gemini_instance.send_image(prompt, image, chat)

            # Add user and model messages to the chat session
            chat_service.add_message(session.id, prompt, update.message.date, "user")
            chat_service.add_message(session.id, text, update.message.date, "model")
        else:

            print("History: ", history.__str__())
            chat = await gemini_instance.get_chat(history=history)
            text = await gemini_instance.send_message(update.message.text, chat)
            
            # Add user and model messages to the chat session
            chat_service.add_message(session.id, update.message.text, update.message.date, "user")
            chat_service.add_message(session.id, text, update.message.date, "model")
            
            print('Response: ', text)
        await telegram_app.bot.edit_message_text(chat_id= chat_id, text=escape(text), message_id=message_id, parse_mode="MarkdownV2")
        return 'OK'
    except Exception as error:
        print(f"Error Occurred: {error}")
        return {
            "method": "sendMessage",
            "chat_id": chat_id,
            "text": 'Sorry, I am not able to generate content for you right now. Please try again later. '
        }
