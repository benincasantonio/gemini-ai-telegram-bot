from flask import Flask, request
from firebase_functions import logger
from .gemini import Gemini
from md2tgmd import escape


app = Flask(__name__)

gemini = Gemini()


@app.get('/')
def hello_world():
    return 'Hello, World!'


@app.post('/webhook')
def webhook():
    chat_id = None
    try:
        body = request.get_json()
        logger.info(f"Body: {body}")

        if 'message' in body:
            chat_id = body['message']['chat']['id']
            logger.info(f"Chat ID: {chat_id}")
        elif 'edited_message' in body:
            chat_id = body['edited_message']['chat']['id']
            logger.info(f"Chat ID: {chat_id}")
        else:
            return {
                "method": "sendMessage",
                "chat_id": chat_id,
                "text": 'Sorry, I am not able to generate content for you right now. Please try again later.'
            }

        if body['message']['text'] == '/start':
            return {
                "method": "sendMessage",
                "chat_id": chat_id,
                "text": 'Welcome!'
            }

        if 'message' in body:
            message_text = body['message']['text']
        elif 'edited_message' in body:
            message_text = body['edited_message']['text']
        else:
            return {
                "method": "sendMessage",
                "chat_id": chat_id,
                "text": 'Sorry, I am not able to generate content for you right now. Please try again later.'
            }
        chat = gemini.get_model().start_chat()
        text = gemini.send_message(message_text, chat)

        return {
            "method": "sendMessage",
            "chat_id": chat_id,
            "text": escape(text),
            "parse_mode": "MarkdownV2"
        }
    except Exception as error:
        logger.error(f"Error occured in webhook: {error}")
        return {
            "method": "sendMessage",
            "chat_id": chat_id,
            "text": 'Sorry, I am not able to generate content for you right now. Please try again later.'
        }
