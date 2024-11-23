from flask import request
from .gemini import Gemini
from md2tgmd import escape
from telegram.ext import ApplicationBuilder
from telegram import Update
from os import getenv
from io import BytesIO
from PIL import Image
from .enums import TelegramBotCommands
from .flask_app import app, db
from .models import ChatSession


@app.get('/')
def hello_world():
    return 'Hello, World!'


@app.post('/webhook')
async def webhook():
    chat_id = None
    

    telegram_app = ApplicationBuilder().token(getenv('TELEGRAM_BOT_TOKEN')).build()
    gemini = Gemini()


    try:
        body = request.get_json()

        update = Update.de_json(body, telegram_app.bot)

        chat_id = update.message.chat_id

        session = db.session.query(ChatSession).filter_by(chat_id=chat_id).first()

        if not session:
            session = ChatSession(chat_id=chat_id, messages=[])
            db.session.add(session)
            db.session.commit()

        if update.edited_message:
            return 'OK'
        else:
            print('sending message')
            message = await telegram_app.bot.send_message(chat_id=chat_id, text="Processing your request...")
            message_id = message.message_id
            print('message sent')
        if update.message.text == TelegramBotCommands.START:
            await telegram_app.bot.send_message(chat_id=chat_id, text="Welcome to Gemini Bot. Send me a message or an image to get started.")
            return 'OK'

        
        if update.message.photo:
            print('Generating images')
            file_id = update.message.photo[-1].file_id
            print(f"Images file id is {file_id}")
            file = await telegram_app.bot.get_file(file_id)
            print("Image file found")
            bytes_array = await file.download_as_bytearray()
            bytesIO = BytesIO(bytes_array)
            print("Images file as bytes")
            image = Image.open(bytesIO)
            print("Image opened")

            prompt = 'Describe the image'

            if update.message.caption:
                prompt = update.message.caption
            print("Prompt is ", prompt)

            text = gemini.send_image(prompt, image)

        else:
            print('Message')
            chat = gemini.get_model().start_chat()
            text = gemini.send_message(update.message.text, chat)
            
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
