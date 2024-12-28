from flask import request
from .gemini import Gemini
from md2tgmd import escape
from telegram.ext import ApplicationBuilder
from telegram import Update
from os import getenv
from io import BytesIO
from PIL import Image
from .enums import TelegramBotCommands
from .flask_app import app, db, ChatMessage, ChatSession


@app.get('/')
def hello_world():
    return 'Hello, World!'


@app.post('/webhook')
async def webhook():
    chat_id = None

    telegram_app = ApplicationBuilder().token(getenv('TELEGRAM_BOT_TOKEN')).build()
    gemini = Gemini()
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
            db.session.query(ChatMessage).filter_by(chat_id=session.id).delete()
            db.session.commit()

            await telegram_app.bot.send_message(chat_id=chat_id, text="New chat started.")
            return 'OK'
        else:
            message = await telegram_app.bot.send_message(chat_id=chat_id, text="Processing your request...")
            message_id = message.message_id

        
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

            text = gemini.send_image(prompt, image)

            # Add the user message to the chat session
            chat_message = ChatMessage(chat_id=chat_id, text=prompt, date=update.message.date, role="user")
            session.messages.append(chat_message)
            db.session.commit()
            # add the model response to the chat session
            chat_message = ChatMessage(chat_id=chat_id, text=text, date=update.message.date, role="model")
            session.messages.append(chat_message)
            db.session.commit()
        else:
            history = []
            if(len(session.messages) > 0):
                for message in session.messages:
                    history.append({
                        "role": message.role,
                        "parts": [
                            {                                
                                "text": message.text
                            }
                        ]
                    })
            print("History: ", history.__str__())
            chat = gemini.get_model().start_chat(history=history)
            text = gemini.send_message(update.message.text, chat)
            
            # Add the user message to the chat session
            chat_message = ChatMessage(chat_id=chat_id, text=update.message.text, date=update.message.date, role="user")
            session.messages.append(chat_message)
            db.session.commit()
            # add the model response to the chat session
            chat_message = ChatMessage(chat_id=chat_id, text=text, date=update.message.date, role="model")
            session.messages.append(chat_message)
            db.session.commit()
            
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
