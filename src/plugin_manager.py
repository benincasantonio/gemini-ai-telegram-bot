from .plugins.weather_plugin import WeatherPlugin
from .plugins.date_time_plugin import DateTimePlugin
import google.ai.generativelanguage as glm
from google.generativeai import ChatSession


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

    def get_function_response(self, function_call: glm.FunctionCall, chat: ChatSession):
        function_declarations = self.get_function_declarations()

        if function_call.name in function_declarations:
            args = {key: value for key, value in function_call.args.items()}
            result = function_declarations[function_call.name](**args)

            print('RESULT: ' + str(result))

            function_response = chat.send_message(
                content=[
                    glm.Part(
                        function_response=glm.FunctionResponse(
                            name=function_call.name,
                            response={'result': result}
                        )
                    )
                ]
            )
            print('FUNCTION RESPONSE: ' + str(function_response))
            return function_response
        else:
            return None
