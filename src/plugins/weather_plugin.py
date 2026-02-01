from typing import Optional
from google.genai.types import FunctionDeclaration, Tool, Schema, Type
from os import getenv
from datetime import datetime as dt

from ..models.weather_models import CurrentWeatherResponse, TimeMachineResponse
from ..services.open_weather_map_service import OpenWeatherMapService
from ..exceptions.weather_exceptions import (
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

    Raises:
        ValueError: If OWM_API_KEY environment variable is not set or empty
    """

    def __init__(self):
        api_key = getenv("OWM_API_KEY")
        if not api_key:
            raise ValueError(
                "OWM_API_KEY environment variable is not set or is empty. "
                "Please configure your OpenWeatherMap API key in the .env file."
            )

        try:
            self.openweathermap_service = OpenWeatherMapService(api_key=api_key)
        except ValueError as e:
            # Re-raise with more context about where the error occurred
            raise ValueError(
                f"Failed to initialize OpenWeatherMap service: {str(e)}"
            ) from e
        self.get_current_weather_function_name: str = "get_current_weather"
        self.get_current_weather_description: str = (
            "Fetches the current weather conditions for a specified city, including temperature, humidity, wind speed, atmospheric pressure, and weather description. Temperature units default to Celsius but can be specified as Fahrenheit or Kelvin."
        )
        self.get_current_weather_parameters = Schema(
            type=Type.OBJECT,
            required=["city"],
            properties={
                "city": {
                    "type": Type.STRING,
                    "description": "The city to get the weather for.",
                },
                "unit": {
                    "type": Type.STRING,
                    "description": "The unit of temperature. Should be one of 'standard' (Kelvin), 'metric' (Celsius), or 'imperial' (Fahrenheit).",
                    "enum": ["standard", "metric", "imperial"],
                    "default": "metric",
                },
            },
        )

        self.get_forecast_weather_function_name: str = "get_forecast_weather"
        self.get_forecast_weather_description: str = (
            "Fetches the historical weather forecast for a specified location (latitude and longitude) and time range. Returns temperature, humidity, wind speed, atmospheric pressure, and weather description for each time point."
        )
        self.get_forecast_weather_parameters = Schema(
            type=Type.OBJECT,
            required=["latitude", "longitude"],
            properties={
                "latitude": {
                    "type": Type.NUMBER,
                    "description": "The latitude of the location to get the forecast for.",
                },
                "longitude": {
                    "type": Type.NUMBER,
                    "description": "The longitude of the location to get the forecast for.",
                },
                "datetime": {
                    "type": Type.STRING,
                    "description": "The date and time for the forecast in ISO 8601 format (e.g., '2023-10-01T15:00:00Z').",
                },
                "unit": {
                    "type": Type.STRING,
                    "description": "The unit of temperature. Should be one of 'standard' (Kelvin), 'metric' (Celsius), or 'imperial' (Fahrenheit).",
                    "enum": ["standard", "metric", "imperial"],
                    "default": "metric",
                },
            },
        )

    def get_current_weather_function_declaration(self):
        return FunctionDeclaration(
            name=self.get_current_weather_function_name,
            description=self.get_current_weather_description,
            parameters=self.get_current_weather_parameters,
        )

    def get_forecast_weather_function_declaration(self):
        return FunctionDeclaration(
            name=self.get_forecast_weather_function_name,
            description=self.get_forecast_weather_description,
            parameters=self.get_forecast_weather_parameters,
        )

    def get_tool(self) -> Tool:
        return Tool(
            function_declarations=[
                self.get_current_weather_function_declaration(),
                self.get_forecast_weather_function_declaration(),
            ]
        )

    async def get_current_weather(self, city: str, unit: str = "metric") -> dict:
        """Get weather data for a location.

        Args:
            city: City name for current weather
            unit: Temperature unit (standard/metric/imperial)

        Returns:
            Dict with weather data or error message
        """

        try:

            # Determine if we need current weather or historical/forecast
            weather = await self.openweathermap_service.get_current_weather(
                city, units=unit
            )

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

        except InvalidAPIKeyError as e:
            return {
                "success": False,
                "error": f"API key error: {e.message}. Please check your OpenWeatherMap API key configuration.",
            }
        except LocationNotFoundError as e:
            return {
                "success": False,
                "error": f"Location not found: {e.message}. Please check the city name or coordinates.",
            }
        except BadRequestError as e:
            params_info = (
                f" (parameters: {', '.join(e.parameters)})" if e.parameters else ""
            )
            return {
                "success": False,
                "error": f"Invalid request: {e.message}{params_info}",
            }
        except RateLimitError as e:
            return {
                "success": False,
                "error": f"Rate limit exceeded: {e.message}. Please try again later.",
            }
        except ServerError as e:
            return {
                "success": False,
                "error": f"Weather service error: {e.message}. Please try again later.",
            }
        except OpenWeatherMapError as e:
            return {"success": False, "error": f"Weather API error: {e.message}"}
        except ValueError as e:
            return {"success": False, "error": f"Invalid timestamp: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"Unexpected error: {str(e)}"}

    async def get_forecast_weather(
        self, latitude: float, longitude: float, datetime: Optional[str] = None, unit: str = "metric"
    ) -> dict:
        """Get forecast weather data for a location.

        Args:
            latitude: Latitude for forecast weather
            longitude: Longitude for forecast weather
            datetime: The date and time for the forecast in ISO 8601 format (e.g., '2023-10-01T15:00:00Z').
            unit: Temperature unit (standard/metric/imperial)
        Returns:
            Dict with forecast weather data or error message
        """

        try:
            if not datetime:
                datetime_unix = int(dt.now().timestamp())
            else:
                datetime_unix = int(dt.fromisoformat(datetime).timestamp())
            forecast: TimeMachineResponse = (
                await self.openweathermap_service.get_timemachine_data(
                    latitude, longitude, dt=datetime_unix, units=unit
                )
            )
            return {
                "success": True,
                "forecast": [
                    {
                        "datetime": dt.fromtimestamp(entry.dt).isoformat(),
                        "temperature": entry.temp,
                        "feels_like": entry.feels_like,
                        "humidity": entry.humidity,
                        "wind_speed": entry.wind_speed,
                        "pressure": entry.pressure,
                        "description": entry.weather[0].description,
                        "conditions": entry.weather[0].main if entry.weather else "",
                    }
                    for entry in forecast.data
                ],
            }
        except OpenWeatherMapError as e:
            return {"success": False, "error": f"Weather API error: {e.message}"}
        except Exception as e:
            return {"success": False, "error": f"Unexpected error: {str(e)}"}

    async def close(self) -> None:
        """Close the OpenWeatherMap service and cleanup resources.

        This should be called when the plugin is no longer needed to
        properly close HTTP connections and prevent resource leaks.
        """
        await self.openweathermap_service.close()

    async def __aenter__(self) -> "WeatherPlugin":
        """Async context manager entry."""
        return self

    async def __aexit__(self) -> None:
        """Async context manager exit. Ensures cleanup of resources."""
        await self.close()
