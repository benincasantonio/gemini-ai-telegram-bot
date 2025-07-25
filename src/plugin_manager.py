from .plugins.weather_plugin import WeatherPlugin
from .plugins.date_time_plugin import DateTimePlugin
from google.genai.chats import Chat

from google.genai.types import PartDict, FunctionResponseDict, FunctionCall, Part


class PluginManager:
    def __init__(self):
        self.__date_time_plugin = DateTimePlugin()
        self.__weather_plugin = WeatherPlugin()

    def get_tools(self):
        return [
            self.__date_time_plugin.get_tool(),
            self.__weather_plugin.get_tool()
        ]

    def get_function_declarations(self):
        return {
            "get_date_time": self.__date_time_plugin.get_date_time,
            "get_weather": self.__weather_plugin.get_weather

        }

    def get_function_response(self, function_call: FunctionCall, chat: Chat):
        function_declarations = self.get_function_declarations()

        if function_call.name in function_declarations:
            args = {key: value for key, value in function_call.args.items()}
            result = function_declarations[function_call.name](**args)

            function_response_part = Part.from_function_response(
                name=function_call.name,
                response={
                    "result": result
                }
            )

            function_response = chat.send_message(
                message=function_response_part
            )

            print('FUNCTION RESPONSE: ' + str(function_response))
            return function_response
        else:
            return None
