from os import getenv

import PIL.Image
from google import genai
from google.genai import types

from google.genai.chats import Chat, GenerateContentConfigOrDict
from .config import Config
from .plugin_manager import PluginManager


class Gemini:


    __plugin_manager = PluginManager()

    def __init__(self):
        self.__model_name = getenv('GEMINI_MODEL_NAME', Config.DEFAULT_GEMINI_MODEL_NAME)
        self.__client = genai.Client(
            api_key=getenv('GEMINI_API_KEY')
        )

        self.__generation_config: GenerateContentConfigOrDict = types.GenerateContentConfig(
            temperature=0.5,
            tools=self.__plugin_manager.get_tools(),
        )

    def get_chat(self, history: list) -> Chat:
        return self.__client.chats.create(
            model=self.__model_name,
            history=history,
            config=self.__generation_config,

        )

    def send_message(self, prompt: str, chat: Chat) -> str:
        function_request = chat.send_message(prompt)
        
        print("Function Request: " + function_request.__str__())

        function_call = function_request.candidates[0].content.parts[0].function_call

        if not function_call:
            chat.get_history().pop()
            response = chat.send_message(prompt)
            return response.text

        function_response = self.__plugin_manager.get_function_response(function_call, chat)

        print("Response: " + function_response.__str__())

        if function_response.text is None:
            return "I'm sorry, An error occurred. Please try again."

        return function_response.text
    

    def send_image(self, prompt: str, image: PIL.Image, chat: Chat) -> str:
        response = chat.send_message([prompt, image])
        print("Image response: " + response.text)
        return response.text
