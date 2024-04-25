from datetime import datetime
from pytz import timezone
from google.generativeai.types import FunctionDeclaration, Tool


class DateTimePlugin:

    def __init__(self):
        self.__name: str = "get_date_time"
        self.__description: str = "A plugin that returns the current date and time."
        self.__parameters: dict[str, any] = {
            "type": "object",
            "properties": {
                "time_zone": {
                    "type": "string",
                    "description": "The timezone to use for the date and time."
                }
            }
        }

    def function_declaration(self):
        return FunctionDeclaration(
            name=self.__name,
            description=self.__description,
            parameters=self.__parameters,
        )

    def get_tool(self) -> Tool:
        return Tool(
            function_declarations=[self.function_declaration()]
        )

    @staticmethod
    def get_date_time(time_zone="Europe/Rome") -> str:
        return datetime.now(timezone(time_zone)).strftime("%Y-%m-%d %H:%M:%S")
