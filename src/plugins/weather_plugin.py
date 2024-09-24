from google.generativeai.types import FunctionDeclaration, Tool
from pyowm import OWM
from dotenv import load_dotenv
from os import getenv

load_dotenv()
owm = OWM(getenv('OWM_API_KEY'))

class WeatherPlugin: 
    def __init__(self):
        self.name: str = "get_weather"
        self.description: str = "A plugin that returns the current weather. "
        self.parameters: dict[str, any] = {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The city name."
                },                
            }
        }

    def function_declaration(self):
        return FunctionDeclaration(
            name=self.name,
            description=self.description,
            parameters=self.parameters,
        )
    
    def get_tool(self) -> Tool:
        return Tool(
            function_declarations=[self.function_declaration()]
        )
    

    @staticmethod
    def get_weather(city: str) -> str:
        mgr = owm.weather_manager()
        weather = mgr.weather_at_place(city).weather
        return f"The weather in {city} is {weather.status} with a temperature of {weather.temperature('celsius')['temp']}°C."
    

