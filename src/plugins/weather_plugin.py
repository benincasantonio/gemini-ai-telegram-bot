from google.genai.types import FunctionDeclaration, Tool, Schema, Type
from dotenv import load_dotenv
from os import getenv
from datetime import datetime

from src.models.weather_models import CurrentWeatherResponse, TimeMachineResponse
from src.services.open_weather_map_service import OpenWeatherMapService
# TODO: Move this to a better place
load_dotenv()

class WeatherPlugin: 
    def __init__(self):
        self.openweathermap_service = OpenWeatherMapService(api_key=getenv('OWM_API_KEY'))
        self.name: str = "get_weather"
        self.description: str = "Get the weather of a city at a particular date and time. If the date is today, the current weather will be returned. Otherwise, the weather at the specified date and time will be returned. If the user does not specify a date and time, the current date and time will be used. If the user types a date like 'tomorrow' or 'in 2 days', you should convert it to the appropriate date. If the user does not specify a unit, the temperature will be returned in Celsius. If the user specifies a unit, the temperature will be returned in that unit."
        self.parameters = Schema(
            type=Type.OBJECT,
            properties={
                "city": {
                    "type": Type.STRING,
                    "description": "The city to get the weather for."
                },
                "latitude": {
                    "type": Type.NUMBER,
                    "description": "The latitude of the location to get the weather for."
                },
                "longitude": {
                    "type": Type.NUMBER,
                    "description": "The longitude of the location to get the weather for."
                },
                "date_time": {
                    "type": Type.INTEGER,
                    "description": "The datetime timestamp for the weather in Unix format."
                },
                "unit": {
                    "type": Type.STRING,
                    "description": "The unit of temperature. Should be one of 'standard' (Kelvin), 'metric' (Celsius), or 'imperial' (Fahrenheit).",
                    "enum": ["standard", "metric", "imperial"],
                    "default": "metric"
                }
            }
        )

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
    

    async def get_weather(self, city: str, latitude: float, longitude: float, date_time: int = int(datetime.now().timestamp()), unit: str = 'metric') -> dict:

        print("Getting weather for city: ", city, " at date time: ", date_time, " with unit: ", unit)
        parsed_date = datetime.fromtimestamp(date_time)

        print("Parsed date: ", parsed_date)

        if parsed_date is None:
            return "Invalid date and time format. Please enter a valid date and time format."

        
        weather = None

        if parsed_date.date() == datetime.now().date():
            weather = await self.openweathermap_service.get_current_weather(city, units=unit)
           
        else: 
            weather = await self.openweathermap_service.get_timemachine_data(latitude, longitude, dt=int(parsed_date.timestamp()), units=unit)


        if isinstance(weather, CurrentWeatherResponse):
            return {
                "description": weather.weather[0].description,
                "temperature": weather.main.temp,
                "feels_like": weather.main.feels_like,
                "humidity": weather.main.humidity,
                "wind_speed": weather.wind.speed,
                "pressure": weather.main.pressure,
                "conditions": weather.weather[0].main,
            }
        elif isinstance(weather, TimeMachineResponse):
            hourly_weather = weather.data[0]
            return {
                "description": hourly_weather.weather[0].description,
                "temperature": hourly_weather.temp,
                "feels_like": hourly_weather.feels_like,
                "humidity": hourly_weather.humidity,
                "wind_speed": hourly_weather.wind_speed,
                "pressure": hourly_weather.pressure,
            }
        
        
    

