from google.generativeai.types import FunctionDeclaration, Tool
from pyowm import OWM
from dotenv import load_dotenv
from os import getenv
from datetime import datetime
import dateparser

load_dotenv()
owm = OWM(getenv('OWM_API_KEY'))

class WeatherPlugin: 
    def __init__(self):
        self.name: str = "get_weather"
        self.description: str = "Get the weather of a city at a particular date and time. If the date is today, the current weather will be returned. Otherwise, the weather at the specified date and time will be returned. If the user does not specify a date and time, the current date and time will be used. If the user types a date like 'tomorrow' or 'in 2 days', you should convert it to the appropriate date. If the user does not specify a unit, the temperature will be returned in Celsius. If the user specifies a unit, the temperature will be returned in that unit."
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

        print("DATE: " + date_time)

        parsed_date = dateparser.parse(date_time)

        if(parsed_date == None):
            return "Invalid date and time format. Please enter a valid date and time format."

        date = parsed_date.strftime('%Y-%m-%d %H:%M:%S')

        
        print("DATETIME: " + date)

        if parsed_date.date() == datetime.now().date():
            weather = mgr.weather_at_place(city).weather
        else: 
            forecast = mgr.forecast_at_place(city, '3h')

            weather = forecast.get_weather_at(date)
        

        return {
            "status": weather.status,
            "detailed_status": weather.detailed_status,
            "temperature": weather.temperature(unit)['temp'],
            "city": city,
            "unit": "°C" if unit == 'celsius' else "°F",
            "date": datetime.fromtimestamp(weather.reference_time()).strftime('%d-%m-%Y %H:%M:%S')
        }
        
        
    

