from google.generativeai.types import FunctionDeclaration, Tool
from pyowm import OWM
from dotenv import load_dotenv
from os import getenv
from datetime import datetime

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
                "date": {
                    "type": "string",
                    "description": "The datetime timestamp for the weather."
                },
                "unit": {
                    "type": "string",
                    "description": "The unit of temperature",
                    "enum": ["celsius", "fahrenheit"]
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
    def get_weather(city: str, date: str = datetime.now().strftime('%Y-%m-%d'), unit: str = 'celsius') -> str:
        mgr = owm.weather_manager()

        date = datetime.strptime(date, '%Y-%m-%d')

        if date.date() == datetime.now().date():
            weather = mgr.weather_at_place(city).weather
        else: 
            forecast = mgr.forecast_at_place(city, '3h').forecast
            weather = forecast.get_weather_at(date)

            return {
                "status": weather.status,
                "detailed_status": weather.detailed_status,
                "temperature": weather.temperature(unit)['temp'],
                "city": city,
                "unit": "°C",
                "reference_time": weather.reference_time()
            }
        

        return {
            "status": weather.status,
            "detailed_status": weather.detailed_status,
            "temperature": weather.temperature(unit)['temp'],
            "city": city,
            "unit": "°C",
            "reference_time": weather.reference_time()
        }
        
        
    

