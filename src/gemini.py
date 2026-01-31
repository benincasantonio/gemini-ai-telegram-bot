from os import getenv

import PIL.Image
from google import genai
from google.genai import types

from google.genai.chats import AsyncChat, GenerateContentConfigOrDict
from .config import Config
from .plugin_manager import PluginManager


class Gemini:
    
    def __init__(self):
        self.__plugin_manager = PluginManager()
        
        self.__model_name = getenv('GEMINI_MODEL_NAME', Config.DEFAULT_GEMINI_MODEL_NAME)
        self.__api_key = getenv('GEMINI_API_KEY')
        self.__client = None
        self.__current_loop = None

        self.__generation_config: GenerateContentConfigOrDict = types.GenerateContentConfig(
            temperature=0.5,
            tools=self.__plugin_manager.get_tools(),
        )
    
    def _get_client(self):
        """Get or create the async client for the current event loop.
        
        In serverless environments, the event loop can change between invocations
        while the Gemini instance persists. This ensures we always use a client
        bound to the current event loop.
        """
        import asyncio
        try:
            current_loop = asyncio.get_running_loop()
        except RuntimeError:
            current_loop = None
        
        # Recreate client if loop has changed or client doesn't exist
        if self.__client is None or self.__current_loop is not current_loop:
            self.__client = genai.Client(api_key=self.__api_key).aio
            self.__current_loop = current_loop
        
        return self.__client

    def get_chat(self, history: list) -> AsyncChat:
        return self._get_client().chats.create(
            model=self.__model_name,
            history=history,
            config=self.__generation_config,
        )

    async def send_message(self, prompt: str, chat: AsyncChat) -> str:
        function_request = await chat.send_message(prompt)
        
        print("Function Request: " + function_request.__str__())

        function_call = function_request.candidates[0].content.parts[0].function_call

        if not function_call:
            chat.get_history().pop()
            response = await chat.send_message(prompt)
            return response.text

        function_response = await self.__plugin_manager.get_function_response(function_call, chat)

        print("Response: " + function_response.__str__())

        if function_response.text is None:
            return "I'm sorry, An error occurred. Please try again."

        return function_response.text


    @staticmethod
    async def send_image(prompt: str, image: PIL.Image, chat: AsyncChat) -> str:
        response = await chat.send_message([prompt, image])
        print("Image response: " + response.text)
        return response.text

    @classmethod
    async def close_plugins(cls) -> None:
        """Close all plugins and cleanup resources.

        This should be called on application shutdown to properly
        close HTTP connections and prevent resource leaks.
        """
        await cls.__plugin_manager.close()