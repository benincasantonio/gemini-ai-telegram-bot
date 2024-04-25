import google.generativeai as gen_ai
from os import getenv
from dotenv import load_dotenv
from functions.src.gemini import Gemini

load_dotenv()
api = getenv('GEMINI_API_KEY')
gen_ai.configure(api_key=api)



gemini = Gemini()
chat = gemini.get_model().start_chat()

def chat_with_ai(chat):
    text = input("What can I do for you? ")

    responseText = gemini.send_message(text, chat)
    print(responseText)
    chat_with_ai(chat)


chat_with_ai(chat)


