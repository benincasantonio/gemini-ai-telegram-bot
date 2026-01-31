from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Request
from telegram import Update

from src.chat_service import ChatService
from src.enums import TelegramBotCommands
from src.gemini import Gemini
from src.services.database_service import get_db
from src.services.telegram_service import TelegramService
from telegram.ext import ApplicationBuilder
from os import getenv
from sqlalchemy.ext.asyncio import AsyncSession

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code can go here
    yield
    # Shutdown code can go here

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.post("/webhook")
async def webhook(request: Request, db: AsyncSession = Depends(get_db)):
    try:
        # Understand better how to initialize outside the endpoint
        telegram_service = TelegramService()
        gemini = Gemini()

        request.body = await request.json()

        telegram_update = Update.de_json(request.body, telegram_service._telegram_app_bot)

        chat_id = telegram_update.message.chat_id

        
        webhook_secret_token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")

        if(telegram_service.is_secure_webhook_enabled() and telegram_service.is_secure_webhook_token_valid(webhook_secret_token) is False):
            await telegram_service.send_unauthorized_message(chat_id=chat_id)
            return 'OK'
        
        chat_service = ChatService()

        chat_session = await chat_service.get_or_create_session(db, chat_id)

        if telegram_update.edited_message:
            # Handle edited message
            return 'OK'
        elif telegram_update.message.text == TelegramBotCommands.START:
            await telegram_service.send_start_message(chat_id=chat_id)
            return 'OK'
        elif telegram_update.message.text == TelegramBotCommands.NEW_CHAT:
            await chat_service.clear_chat_history(db, chat_session.id)
            await telegram_service.send_new_chat_message(chat_id=chat_id)
            return 'OK'
        
        message = await telegram_service.send_message(chat_id=chat_id, text="Processing your request...")

        response_text = ""
        
        if telegram_update.message.photo:
            image = await telegram_service.get_image_from_message(telegram_update.message)

            prompt = "Describe this image in detail."

            if telegram_update.message.caption:
                prompt = telegram_update.message.caption


            history = await chat_service.get_chat_history(db, chat_session.id)
            chat = gemini.get_chat(history=history)

            response_text = await gemini.send_image(prompt, image, chat)

            await chat_service.add_message(db, chat_session.id, prompt, telegram_update.message.date, "user")
            await chat_service.add_message(db, chat_session.id, response_text, telegram_update.message.date, "model")
        else:
            chat = gemini.get_chat(history=await chat_service.get_chat_history(db, chat_session.id))

            response_text = await gemini.send_message(telegram_update.message.text, chat)

            await chat_service.add_message(db, chat_session.id, telegram_update.message.text, telegram_update.message.date, "user")
            await chat_service.add_message(db, chat_session.id, response_text, telegram_update.message.date, "model")

        #Add support to markdown v2
        await telegram_service.update_message(chat_id=chat_id, message_id=message.message_id, text=response_text)
        return 'OK' 
    except Exception as error:
        print(f"Error Occurred: {error}")
        return {
            "method": "sendMessage",
            "chat_id": chat_id,
            "text": 'Sorry, I am not able to generate content for you right now. Please try again later. '
        }