from google.genai.types import FunctionDeclaration, Tool, Schema, Type
from os import getenv
from datetime import datetime

from src.models.weather_models import CurrentWeatherResponse, TimeMachineResponse
from src.services.open_weather_map_service import OpenWeatherMapService
from src.exceptions.weather_exceptions import (
    InvalidAPIKeyError,
    LocationNotFoundError,
    BadRequestError,
    RateLimitError,
    ServerError,
    OpenWeatherMapError,
)

class WeatherPlugin:
    """Weather plugin for getting current and historical weather data.

    This plugin uses OpenWeatherMap API to fetch weather information.
    It should be used as an async context manager or properly closed when done.
    """

    def __init__(self):
        self.openweathermap_service = OpenWeatherMapService(api_key=getenv('OWM_API_KEY'))
        self.name: str = "get_weather"
        self.description: str = "Get the weather of a city at a particular date and time. If the date is today, the current weather will be returned. Otherwise, the weather at the specified date and time will be returned. If the user does not specify a date and time, the current date and time will be used. If the user types a date like 'tomorrow' or 'in 2 days', you should convert it to the appropriate date. If the user does not specify a unit, the temperature will be returned in Celsius. If the user specifies a unit, the temperature will be returned in that unit."
        self.parameters = Schema(
            type=Type.OBJECT,
            required=["city", "latitude", "longitude"],
            properties={
                "city": {
                    "type": Type.STRING,
                    "description": "The city to get the weather for.",
                },
                "latitude": {
                    "type": Type.NUMBER,
                    "description": "The latitude of the location to get the weather for.",
                },
                "longitude": {
                    "type": Type.NUMBER,
                    "description": "The longitude of the location to get the weather for.",
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
    

    async def get_weather(self, city: str, latitude: float, longitude: float, date_time: int = None, unit: str = 'metric') -> dict:
        """Get weather data for a location.

        Args:
            city: City name for current weather
            latitude: Latitude for historical/forecast weather
            longitude: Longitude for historical/forecast weather
            date_time: Unix timestamp (defaults to current time)
            unit: Temperature unit (standard/metric/imperial)

        Returns:
            Dict with weather data or error message
        """
        if date_time is None:
            date_time = int(datetime.now().timestamp())

        print("Getting weather for city: ", city, " at date time: ", date_time, " with unit: ", unit)

        try:
            parsed_date = datetime.fromtimestamp(date_time)
            print("Parsed date: ", parsed_date)

            weather = None

            # Determine if we need current weather or historical/forecast
            if parsed_date.date() == datetime.now().date():
                weather = await self.openweathermap_service.get_current_weather(city, units=unit)
            else:
                weather = await self.openweathermap_service.get_timemachine_data(
                    latitude, longitude, dt=int(parsed_date.timestamp()), units=unit
                )

            # Format response based on weather type
            if isinstance(weather, CurrentWeatherResponse):
                return {
                    "success": True,
                    "description": weather.weather[0].description,
                    "temperature": weather.main.temp,
                    "feels_like": weather.main.feels_like,
                    "humidity": weather.main.humidity,
                    "wind_speed": weather.wind.speed,
                    "pressure": weather.main.pressure,
                    "conditions": weather.weather[0].main if weather.weather else "",
                }
            elif isinstance(weather, TimeMachineResponse):
                if not weather.data:
                    return {
                        "success": False,
                        "error": "No weather data available for the specified time."
                    }

                hourly_weather = weather.data[0]
                return {
                    "success": True,
                    "description": hourly_weather.weather[0].description if hourly_weather.weather else "",
                    "temperature": hourly_weather.temp,
                    "feels_like": hourly_weather.feels_like,
                    "humidity": hourly_weather.humidity,
                    "wind_speed": hourly_weather.wind_speed,
                    "pressure": hourly_weather.pressure,
                }
            else:
                return {
                    "success": False,
                    "error": "Unexpected weather response type received."
                }

        except InvalidAPIKeyError as e:
            return {
                "success": False,
                "error": f"API key error: {e.message}. Please check your OpenWeatherMap API key configuration."
            }
        except LocationNotFoundError as e:
            return {
                "success": False,
                "error": f"Location not found: {e.message}. Please check the city name or coordinates."
            }
        except BadRequestError as e:
            params_info = f" (parameters: {', '.join(e.parameters)})" if e.parameters else ""
            return {
                "success": False,
                "error": f"Invalid request: {e.message}{params_info}"
            }
        except RateLimitError as e:
            return {
                "success": False,
                "error": f"Rate limit exceeded: {e.message}. Please try again later."
            }
        except ServerError as e:
            return {
                "success": False,
                "error": f"Weather service error: {e.message}. Please try again later."
            }
        except OpenWeatherMapError as e:
            return {
                "success": False,
                "error": f"Weather API error: {e.message}"
            }
        except ValueError as e:
            return {
                "success": False,
                "error": f"Invalid timestamp: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }

    async def close(self) -> None:
        """Close the OpenWeatherMap service and cleanup resources.

        This should be called when the plugin is no longer needed to
        properly close HTTP connections and prevent resource leaks.
        """
        await self.openweathermap_service.close()

    async def __aenter__(self) -> "WeatherPlugin":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit. Ensures cleanup of resources."""
        await self.close()
