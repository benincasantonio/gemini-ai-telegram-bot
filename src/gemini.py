from os import getenv

import PIL.Image
import google.generativeai as gen_ai
from .plugin_manager import PluginManager
import PIL as PIL


class Gemini:
    __generation_config: gen_ai.GenerationConfig = gen_ai.GenerationConfig(
        temperature=0.5,
        max_output_tokens=1024,
    )
    __plugin_manager = PluginManager()

    def __init__(self):
        gen_ai.configure(api_key=getenv('GEMINI_API_KEY'))
        self.__pro_model = gen_ai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=self.__generation_config
        )
        self.__pro_model_vision = gen_ai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=self.__generation_config
        )

    def get_model(self):
        return self.__pro_model

    def generate_content(self, prompt: str):
        return self.__pro_model.generate_content(prompt, generation_config=self.__generation_config)

    def send_message(self, prompt: str, chat: gen_ai.ChatSession) -> str:
        function_request = chat.send_message(prompt, tools=self.__plugin_manager.get_tools())
        
        print("Function Request: " + function_request.__str__())

        function_call = function_request.candidates[0].content.parts[0].function_call

        if not function_call:
            chat.rewind()
            response = chat.send_message(prompt)
            return response.text

        function_response = self.__plugin_manager.get_function_response(function_call, chat)

        print("Response: " + function_response.__str__())

        if(function_response.text == None):
            return "I'm sorry, An error occurred. Please try again."

        return function_response.parts[0].text
    

    def send_image(self, prompt: str, image: PIL.Image):
        response = self.__pro_model_vision.generate_content([prompt, image])
        print("Image response: " + response.text)
        return response.text
