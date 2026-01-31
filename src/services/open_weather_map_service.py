"""OpenWeatherMap API service for weather data retrieval."""
from typing import Literal, Optional
from httpx import AsyncClient, HTTPStatusError

from ..models.weather_models import (
    CurrentWeatherResponse,
    OneCallResponse,
    TimeMachineResponse,
)
from ..exceptions.weather_exceptions import (
    BadRequestError,
    InvalidAPIKeyError,
    LocationNotFoundError,
    OpenWeatherMapError,
    RateLimitError,
    ServerError,
)

# Type alias for units of measurement
Units = Literal["standard", "metric", "imperial"]


class OpenWeatherMapService:
    """Service for interacting with OpenWeatherMap API.

    This service provides methods to retrieve current weather, forecasts,
    and historical weather data using OpenWeatherMap API v2.5 and v3.0.
    """

    BASE_URL_V2: str = "https://api.openweathermap.org/data/2.5/"
    BASE_URL_V3: str = "https://api.openweathermap.org/data/3.0/"

    def __init__(self, api_key: str, units: Units = "metric") -> None:
        """Initialize the OpenWeatherMap service.

        Args:
            api_key: Your OpenWeatherMap API key
            units: Units of measurement. Options:
                   - "standard" (Kelvin for temperature)
                   - "metric" (Celsius for temperature) - default
                   - "imperial" (Fahrenheit for temperature)

        Raises:
            ValueError: If api_key is None or empty
        """
        if not api_key:
            raise ValueError("API key is required and cannot be None or empty")

        self.api_key: str = api_key
        self.units: Units = units
        self.client_v2: AsyncClient = AsyncClient(base_url=self.BASE_URL_V2)
        self.client_v3: AsyncClient = AsyncClient(base_url=self.BASE_URL_V3)

    def _handle_http_error(self, error: HTTPStatusError) -> None:
        """Convert HTTP errors to custom exceptions with user-friendly messages.

        Args:
            error: The HTTP status error from httpx

        Raises:
            InvalidAPIKeyError: For 401 Unauthorized errors
            LocationNotFoundError: For 404 Not Found errors
            BadRequestError: For 400 Bad Request errors
            RateLimitError: For 429 Too Many Requests errors
            ServerError: For 5xx Server errors
            OpenWeatherMapError: For any other HTTP errors
        """
        status_code = error.response.status_code

        # Try to parse error response JSON
        try:
            error_data = error.response.json()
            message = error_data.get("message", str(error))
            parameters = error_data.get("parameters", [])
        except Exception:
            message = str(error)
            parameters = []

        # Map status codes to custom exceptions
        if status_code == 401:
            raise InvalidAPIKeyError(message)
        elif status_code == 404:
            raise LocationNotFoundError(message)
        elif status_code == 400:
            raise BadRequestError(message, parameters=parameters)
        elif status_code == 429:
            raise RateLimitError(message)
        elif status_code >= 500:
            raise ServerError(message)
        else:
            raise OpenWeatherMapError(message, status_code=status_code)

    async def get_current_weather(
        self,
        city: str,
        units: Optional[Units] = None
    ) -> CurrentWeatherResponse:
        """Get current weather data for a specific city.

        Uses the Current Weather Data API (v2.5).

        Args:
            city: City name (e.g., "London" or "London,UK")
            units: Units of measurement (defaults to instance units)

        Returns:
            CurrentWeatherResponse with current weather data

        Raises:
            InvalidAPIKeyError: If the API key is invalid or unauthorized
            LocationNotFoundError: If the city is not found
            BadRequestError: If the request parameters are invalid
            RateLimitError: If the API rate limit is exceeded
            ServerError: If the OpenWeatherMap server encounters an error
            OpenWeatherMapError: For any other API errors
        """
        params = {
            "q": city,
            "appid": self.api_key,
            "units": units or self.units
        }
        try:
            response = await self.client_v2.get("weather", params=params)
            response.raise_for_status()
            return CurrentWeatherResponse(**response.json())
        except HTTPStatusError as e:
            self._handle_http_error(e)

    async def forecast(
        self,
        lat: float,
        lon: float,
        exclude: Optional[list[str]] = None,
        lang: Optional[str] = None,
        units: Optional[Units] = None
    ) -> OneCallResponse:
        """Get comprehensive weather forecast using One Call API 3.0.

        Provides current weather, minute forecast for 1 hour, hourly forecast
        for 48 hours, daily forecast for 8 days, and weather alerts.

        Args:
            lat: Latitude (-90 to 90)
            lon: Longitude (-180 to 180)
            exclude: Optional list to exclude parts of response.
                     Options: "current", "minutely", "hourly", "daily", "alerts"
            lang: Optional language code for weather descriptions
            units: Units of measurement (defaults to instance units)

        Returns:
            OneCallResponse with comprehensive weather forecast data

        Raises:
            InvalidAPIKeyError: If the API key is invalid or unauthorized
            LocationNotFoundError: If the coordinates are not found
            BadRequestError: If the request parameters are invalid
            RateLimitError: If the API rate limit is exceeded
            ServerError: If the OpenWeatherMap server encounters an error
            OpenWeatherMapError: For any other API errors
        """
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": units or self.units
        }

        if exclude:
            params["exclude"] = ",".join(exclude)

        if lang:
            params["lang"] = lang

        try:
            response = await self.client_v3.get("onecall", params=params)
            response.raise_for_status()
            return OneCallResponse(**response.json())
        except HTTPStatusError as e:
            self._handle_http_error(e)

    async def get_timemachine_data(
        self,
        lat: float,
        lon: float,
        dt: int,
        lang: Optional[str] = None,
        units: Optional[Units] = None
    ) -> TimeMachineResponse:
        """Get historical or future weather data using Time Machine API.

        Provides weather data for a specific date and time. Data is available
        from January 1st, 1979 till 4 days ahead.

        Args:
            lat: Latitude (-90 to 90)
            lon: Longitude (-180 to 180)
            dt: Unix timestamp (UTC) for the desired date/time
            lang: Optional language code for weather descriptions
            units: Units of measurement (defaults to instance units)

        Returns:
            TimeMachineResponse with historical/future weather data

        Raises:
            InvalidAPIKeyError: If the API key is invalid or unauthorized
            LocationNotFoundError: If the coordinates are not found
            BadRequestError: If the request parameters are invalid
            RateLimitError: If the API rate limit is exceeded
            ServerError: If the OpenWeatherMap server encounters an error
            OpenWeatherMapError: For any other API errors
        """
        params = {
            "lat": lat,
            "lon": lon,
            "dt": dt,
            "appid": self.api_key,
            "units": units or self.units
        }

        if lang:
            params["lang"] = lang

        try:
            response = await self.client_v3.get("onecall/timemachine", params=params)
            response.raise_for_status()
            return TimeMachineResponse(**response.json())
        except HTTPStatusError as e:
            self._handle_http_error(e)

    async def close(self) -> None:
        """Close the HTTP clients. Call this when done using the service."""
        await self.client_v2.aclose()
        await self.client_v3.aclose()

    async def __aenter__(self) -> "OpenWeatherMapService":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()