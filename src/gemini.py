from os import getenv

import PIL.Image
from langchain_core.language_models import LanguageModelInput

from .config import Config
from .plugin_manager import PluginManager
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain import hub
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage


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

    def get_llm(self):
        return self.__llm

    def send_message(self, prompt: str, chat_history) -> str:

        print("Tools Binded")

        messages = chat_history + [HumanMessage(role="user", content=prompt)]

        print("Messages: " + messages.__str__())

        invoke_response = self.__llm.invoke(
            messages, tools=self.__plugin_manager.get_tools()
        )

        # get first invoke response since it is a tuple
        if isinstance(invoke_response, tuple):
            invoke_response = invoke_response[0]

        print("Base message: " + invoke_response.__str__())

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

        return invoke_response.content

    def send_image(self, prompt: str, image: PIL.Image):
        response = self.__model.generate_content([prompt, image])
        print("Image response: " + response.text)
        return response.text
