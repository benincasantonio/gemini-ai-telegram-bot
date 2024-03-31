from flask import Flask, request
from firebase_functions import logger
from dotenv import load_dotenv
from gemini import Gemini

load_dotenv()

app = Flask(__name__)

gemini = Gemini()


@app.get('/')
def hello_world():
    return 'Hello, World!'


@app.post('/webhook')
def webhook():
    try:
        body = request.get_json()
        logger.info(f"Body: {body}")

        content = gemini.generate_content(body['message']['text'])

        return {
            "method": "sendMessage",
            "chat_id": body['message']['chat']['id'],
            "text": content.text
        }
    except Exception as error:
        logger.error(f"Error occured in webhook: {error}")

        body = request.get_json()
        return {
            "method": "sendMessage",
            "chat_id": body['message']['chat']['id'],
            "text": 'Sorry, I am not able to generate content for you right now. Please try again later.'
        }

