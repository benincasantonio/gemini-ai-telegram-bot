from google.generativeai.types import FunctionDeclaration, Tool
from pyowm import OWM
from dotenv import load_dotenv
from os import getenv

load_dotenv()
owm = OWM(getenv('OWM_API_KEY'))

class WeatherPlugin: 
    def __init__(self):
        self.name: str = "get_weather"
        self.description: str = "A plugin that returns the current weather."
        ## The parameters are, the city name and the latitude and longitude of the city.
        self.parameters: dict[str, any] = {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The city name."
                },
                "latitude": {
                    "type": "number",
                    "description": "The latitude of the city."
                },
                "longitude": {
                    "type": "number",
                    "description": "The longitude of the city."
                }
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
    def get_weather(city: str, latitude: float, longitude: float) -> str:
        mgr = owm.weather_manager()
        print('WEATHER: ', city, latitude, longitude)
        weather = mgr.weather_at_coords(latitude, longitude).weather
        return f"The weather in {city} is {weather.status} with a temperature of {weather.temperature('celsius')['temp']}°C."
    

