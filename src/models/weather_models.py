"""OpenWeatherMap API response models for type safety and autocomplete."""
from typing import Optional
from pydantic import BaseModel, Field


class WeatherCondition(BaseModel):
    """Weather condition details."""
    id: int = Field(..., description="Weather condition id")
    main: str = Field(..., description="Group of weather parameters (Rain, Snow, Clouds, etc.)")
    description: str = Field(..., description="Weather condition description")
    icon: str = Field(..., description="Weather icon id")


class CurrentWeatherCoord(BaseModel):
    """Geographical coordinates."""
    lon: float = Field(..., description="Longitude")
    lat: float = Field(..., description="Latitude")


class CurrentWeatherMain(BaseModel):
    """Main weather parameters."""
    temp: float = Field(..., description="Temperature in Celsius")
    feels_like: float = Field(..., description="Perceived temperature in Celsius")
    temp_min: float = Field(..., description="Minimum temperature in Celsius")
    temp_max: float = Field(..., description="Maximum temperature in Celsius")
    pressure: int = Field(..., description="Atmospheric pressure in hPa")
    humidity: int = Field(..., description="Humidity percentage")
    sea_level: Optional[int] = Field(None, description="Atmospheric pressure at sea level in hPa")
    grnd_level: Optional[int] = Field(None, description="Atmospheric pressure at ground level in hPa")


class CurrentWeatherWind(BaseModel):
    """Wind information."""
    speed: float = Field(..., description="Wind speed in m/s")
    deg: int = Field(..., description="Wind direction in degrees")
    gust: Optional[float] = Field(None, description="Wind gust in m/s")


class CurrentWeatherClouds(BaseModel):
    """Cloud information."""
    all: int = Field(..., description="Cloudiness percentage")


class CurrentWeatherRain(BaseModel):
    """Rain volume."""
    one_h: Optional[float] = Field(None, alias="1h", description="Rain volume for last hour in mm")
    three_h: Optional[float] = Field(None, alias="3h", description="Rain volume for last 3 hours in mm")


class CurrentWeatherSnow(BaseModel):
    """Snow volume."""
    one_h: Optional[float] = Field(None, alias="1h", description="Snow volume for last hour in mm")
    three_h: Optional[float] = Field(None, alias="3h", description="Snow volume for last 3 hours in mm")


class CurrentWeatherSys(BaseModel):
    """System information."""
    type: Optional[int] = Field(None, description="Internal parameter")
    id: Optional[int] = Field(None, description="Internal parameter")
    country: str = Field(..., description="Country code (e.g., GB, US)")
    sunrise: int = Field(..., description="Sunrise time, Unix, UTC")
    sunset: int = Field(..., description="Sunset time, Unix, UTC")


class CurrentWeatherResponse(BaseModel):
    """Current weather data response from OpenWeatherMap API."""
    coord: CurrentWeatherCoord = Field(..., description="Geographical coordinates")
    weather: list[WeatherCondition] = Field(..., description="Weather conditions")
    base: str = Field(..., description="Internal parameter")
    main: CurrentWeatherMain = Field(..., description="Main weather parameters")
    visibility: int = Field(..., description="Visibility in meters (max 10km)")
    wind: CurrentWeatherWind = Field(..., description="Wind information")
    clouds: CurrentWeatherClouds = Field(..., description="Cloud information")
    rain: Optional[CurrentWeatherRain] = Field(None, description="Rain volume")
    snow: Optional[CurrentWeatherSnow] = Field(None, description="Snow volume")
    dt: int = Field(..., description="Time of data calculation, Unix, UTC")
    sys: CurrentWeatherSys = Field(..., description="System information")
    timezone: int = Field(..., description="Shift in seconds from UTC")
    id: int = Field(..., description="City ID")
    name: str = Field(..., description="City name")
    cod: int = Field(..., description="Internal parameter")


class OneCallCurrentWeather(BaseModel):
    """Current weather data in One Call API response."""
    dt: int = Field(..., description="Current time, Unix, UTC")
    sunrise: Optional[int] = Field(None, description="Sunrise time, Unix, UTC")
    sunset: Optional[int] = Field(None, description="Sunset time, Unix, UTC")
    temp: float = Field(..., description="Temperature in Celsius")
    feels_like: float = Field(..., description="Perceived temperature in Celsius")
    pressure: int = Field(..., description="Atmospheric pressure at sea level in hPa")
    humidity: int = Field(..., description="Humidity percentage")
    dew_point: float = Field(..., description="Dew point temperature in Celsius")
    uvi: float = Field(..., description="UV index")
    clouds: int = Field(..., description="Cloudiness percentage")
    visibility: int = Field(..., description="Average visibility in meters (max 10km)")
    wind_speed: float = Field(..., description="Wind speed in m/s")
    wind_deg: int = Field(..., description="Wind direction in degrees")
    wind_gust: Optional[float] = Field(None, description="Wind gust in m/s")
    rain: Optional[dict[str, float]] = Field(None, description="Rain volume for last hour")
    snow: Optional[dict[str, float]] = Field(None, description="Snow volume for last hour")
    weather: list[WeatherCondition] = Field(..., description="Weather conditions")


class MinutelyForecast(BaseModel):
    """Minute-by-minute precipitation forecast."""
    dt: int = Field(..., description="Time of forecasted data, Unix, UTC")
    precipitation: float = Field(..., description="Precipitation volume in mm/h")


class HourlyForecast(BaseModel):
    """Hourly forecast data."""
    dt: int = Field(..., description="Time of forecasted data, Unix, UTC")
    temp: float = Field(..., description="Temperature in Celsius")
    feels_like: float = Field(..., description="Perceived temperature in Celsius")
    pressure: int = Field(..., description="Atmospheric pressure at sea level in hPa")
    humidity: int = Field(..., description="Humidity percentage")
    dew_point: float = Field(..., description="Dew point temperature in Celsius")
    uvi: float = Field(..., description="UV index")
    clouds: int = Field(..., description="Cloudiness percentage")
    visibility: int = Field(..., description="Average visibility in meters")
    wind_speed: float = Field(..., description="Wind speed in m/s")
    wind_deg: int = Field(..., description="Wind direction in degrees")
    wind_gust: Optional[float] = Field(None, description="Wind gust in m/s")
    pop: float = Field(..., description="Probability of precipitation (0-1)")
    rain: Optional[dict[str, float]] = Field(None, description="Rain volume")
    snow: Optional[dict[str, float]] = Field(None, description="Snow volume")
    weather: list[WeatherCondition] = Field(..., description="Weather conditions")


class DailyTemperature(BaseModel):
    """Daily temperature variations."""
    day: float = Field(..., description="Day temperature in Celsius")
    min: float = Field(..., description="Min daily temperature in Celsius")
    max: float = Field(..., description="Max daily temperature in Celsius")
    night: float = Field(..., description="Night temperature in Celsius")
    eve: float = Field(..., description="Evening temperature in Celsius")
    morn: float = Field(..., description="Morning temperature in Celsius")


class DailyFeelsLike(BaseModel):
    """Daily perceived temperature variations."""
    day: float = Field(..., description="Day perceived temperature in Celsius")
    night: float = Field(..., description="Night perceived temperature in Celsius")
    eve: float = Field(..., description="Evening perceived temperature in Celsius")
    morn: float = Field(..., description="Morning perceived temperature in Celsius")


class DailyForecast(BaseModel):
    """Daily forecast data."""
    dt: int = Field(..., description="Time of forecasted data, Unix, UTC")
    sunrise: Optional[int] = Field(None, description="Sunrise time, Unix, UTC")
    sunset: Optional[int] = Field(None, description="Sunset time, Unix, UTC")
    moonrise: int = Field(..., description="Moonrise time, Unix, UTC")
    moonset: int = Field(..., description="Moonset time, Unix, UTC")
    moon_phase: float = Field(..., description="Moon phase (0-1)")
    summary: Optional[str] = Field(None, description="Human-readable weather summary")
    temp: DailyTemperature = Field(..., description="Temperature variations")
    feels_like: DailyFeelsLike = Field(..., description="Perceived temperature variations")
    pressure: int = Field(..., description="Atmospheric pressure at sea level in hPa")
    humidity: int = Field(..., description="Humidity percentage")
    dew_point: float = Field(..., description="Dew point temperature in Celsius")
    wind_speed: float = Field(..., description="Wind speed in m/s")
    wind_deg: int = Field(..., description="Wind direction in degrees")
    wind_gust: Optional[float] = Field(None, description="Wind gust in m/s")
    weather: list[WeatherCondition] = Field(..., description="Weather conditions")
    clouds: int = Field(..., description="Cloudiness percentage")
    pop: float = Field(..., description="Probability of precipitation (0-1)")
    rain: Optional[float] = Field(None, description="Rain volume in mm")
    snow: Optional[float] = Field(None, description="Snow volume in mm")
    uvi: float = Field(..., description="Max UV index for the day")


class WeatherAlert(BaseModel):
    """Weather alert information."""
    sender_name: str = Field(..., description="Name of the alert source")
    event: str = Field(..., description="Alert event name")
    start: int = Field(..., description="Start time of the alert, Unix, UTC")
    end: int = Field(..., description="End time of the alert, Unix, UTC")
    description: str = Field(..., description="Alert description")
    tags: list[str] = Field(default_factory=list, description="Alert tags")


class OneCallResponse(BaseModel):
    """One Call API 3.0 response with current weather and forecasts."""
    lat: float = Field(..., description="Latitude")
    lon: float = Field(..., description="Longitude")
    timezone: str = Field(..., description="Timezone name")
    timezone_offset: int = Field(..., description="Shift in seconds from UTC")
    current: Optional[OneCallCurrentWeather] = Field(None, description="Current weather data")
    minutely: Optional[list[MinutelyForecast]] = Field(None, description="Minute forecast for next hour")
    hourly: Optional[list[HourlyForecast]] = Field(None, description="Hourly forecast for 48 hours")
    daily: Optional[list[DailyForecast]] = Field(None, description="Daily forecast for 16 days")
    alerts: Optional[list[WeatherAlert]] = Field(None, description="Weather alerts")


class TimeMachineData(BaseModel):
    """Historical or future weather data point."""
    dt: int = Field(..., description="Time of data, Unix, UTC")
    sunrise: Optional[int] = Field(None, description="Sunrise time, Unix, UTC")
    sunset: Optional[int] = Field(None, description="Sunset time, Unix, UTC")
    temp: float = Field(..., description="Temperature in Celsius")
    feels_like: float = Field(..., description="Perceived temperature in Celsius")
    pressure: int = Field(..., description="Atmospheric pressure at sea level in hPa")
    humidity: int = Field(..., description="Humidity percentage")
    dew_point: float = Field(..., description="Dew point temperature in Celsius")
    uvi: float = Field(..., description="UV index")
    clouds: int = Field(..., description="Cloudiness percentage")
    visibility: int = Field(..., description="Average visibility in meters")
    wind_speed: float = Field(..., description="Wind speed in m/s")
    wind_deg: int = Field(..., description="Wind direction in degrees")
    wind_gust: Optional[float] = Field(None, description="Wind gust in m/s")
    weather: list[WeatherCondition] = Field(..., description="Weather conditions")


class TimeMachineResponse(BaseModel):
    """Time Machine API response for historical/future weather data."""
    lat: float = Field(..., description="Latitude")
    lon: float = Field(..., description="Longitude")
    timezone: str = Field(..., description="Timezone name")
    timezone_offset: int = Field(..., description="Shift in seconds from UTC")
    data: list[TimeMachineData] = Field(..., description="Weather data points")
