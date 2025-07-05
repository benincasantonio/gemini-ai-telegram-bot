from os import getenv

import PIL.Image
from langchain_core.language_models import LanguageModelInput

from .config import Config
from .plugin_manager import PluginManager
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain import hub
from langchain.agents import create_react_agent, AgentExecutor


class Gemini:
    # __generation_config: gen_ai.GenerationConfig = gen_ai.GenerationConfig(
    #     temperature=0.5,
    #     max_output_tokens=1024,
    # )
    __plugin_manager = PluginManager()

    def __init__(self):
        self.gemini_api_key = getenv("GEMINI_API_KEY")

        self.__model_name = getenv(
            "GEMINI_MODEL_NAME", Config.DEFAULT_GEMINI_MODEL_NAME
        )

        self.__llm: ChatGoogleGenerativeAI = ChatGoogleGenerativeAI(
            model=self.__model_name, temperature=0.5, google_api_key=self.gemini_api_key
        )

        
        print("Setup Agent")

    def get_model(self):
        return self.__model

    def send_message(self, prompt: LanguageModelInput) -> str:
        prompt = (
            "You are a helpful assistant. "
            "You may not need to use tools for every query - the user may just want to chat!"
        )

        self.__agent = create_react_agent(model=self.__llm, tools=self.__plugin_manager.get_tools(), prompt=prompt)


        base_message = self.__agent.invoke({
            "messages": prompt,
        })

        # function_request = chat.send_message(prompt, tools=self.__plugin_manager.get_tools())

        # print("Function Request: " + function_request.__str__())

        # function_call = function_request.candidates[0].content.parts[0].function_call
        #
        # if not function_call:
        #     chat.rewind()
        #     response = chat.send_message(prompt)
        #     return response.text
        #
        # function_response = self.__plugin_manager.get_function_response(function_call, chat)
        #
        # print("Response: " + function_response.__str__())
        #
        # if(function_response.text == None):
        #     return "I'm sorry, An error occurred. Please try again."

        return base_message.text()

    def send_image(self, prompt: str, image: PIL.Image):
        response = self.__model.generate_content([prompt, image])
        print("Image response: " + response.text)
        return response.text
