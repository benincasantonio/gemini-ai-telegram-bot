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
        self.description: str = "A plugin that returns the current weather or the weather forecast for other days."
        self.parameters: dict[str, any] = {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The city name."
                },
                "date_time": {
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
    def get_weather(city: str, date_time: str = datetime.now().strftime('%d-%m-%Y'), unit: str = 'celsius') -> str:
        mgr = owm.weather_manager()
        print("DATETIME: " + date_time)
        date = datetime.strptime(date_time, '%d-%m-%Y')

        if date.date() == datetime.now().date():
            weather = mgr.weather_at_place(city).weather
        else: 
            forecast = mgr.forecast_at_place(city, '3h')
            weather = forecast.get_weather_at(date)

            print('WEATHER: ' + str(weather))

            print({
                "status": weather.status,
                "detailed_status": weather.detailed_status,
                "temperature": weather.temperature(unit)['temp'],
                "city": city,
                "unit": "°C",
                "reference_time": weather.reference_time()
            })

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
        
        
    

