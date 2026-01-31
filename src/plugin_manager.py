import asyncio
from .plugins.weather_plugin import WeatherPlugin
from .plugins.date_time_plugin import DateTimePlugin
from google.genai.chats import AsyncChat

from google.genai.types import PartDict, FunctionResponseDict, FunctionCall, Part


class PluginManager:
    """Manages plugins and their lifecycle.

    Handles plugin initialization, tool registration, and cleanup.
    Should be used as an async context manager or properly closed when done.
    """

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

    async def get_function_response(self, function_call: FunctionCall, chat: AsyncChat) -> PartDict | FunctionResponseDict | None:
        function_declarations = self.get_function_declarations()

        if function_call.name in function_declarations:
            args = {key: value for key, value in function_call.args.items()}
            if asyncio.iscoroutinefunction(function_declarations[function_call.name]):
                result = await function_declarations[function_call.name](**args)
            else:
                result = function_declarations[function_call.name](**args)

            function_response_part = Part.from_function_response(
                name=function_call.name,
                response={
                    "result": result
                }
            )

            function_response = await chat.send_message(
                message=function_response_part
            )

            print('FUNCTION RESPONSE: ' + str(function_response))
            return function_response
        else:
            return None

    async def close(self) -> None:
        """Close all plugins and cleanup resources.

        This should be called when the plugin manager is no longer needed
        to properly close HTTP connections and prevent resource leaks.
        """
        # Close plugins that have a close method
        if hasattr(self.__weather_plugin, 'close'):
            await self.__weather_plugin.close()

    async def __aenter__(self) -> "PluginManager":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit. Ensures cleanup of resources."""
        await self.close()
