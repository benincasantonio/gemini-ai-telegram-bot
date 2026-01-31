"""Custom exceptions for OpenWeatherMap API errors."""


class OpenWeatherMapError(Exception):
    """Base exception for OpenWeatherMap API errors."""

    def __init__(self, message: str, status_code: int = None, parameters: list[str] = None):
        """Initialize the exception.

        Args:
            message: Error message
            status_code: HTTP status code
            parameters: List of parameters related to the error
        """
        self.message = message
        self.status_code = status_code
        self.parameters = parameters or []
        super().__init__(self.message)


class InvalidAPIKeyError(OpenWeatherMapError):
    """Raised when the API key is invalid or unauthorized (401)."""

    def __init__(self, message: str = "Invalid or unauthorized API key"):
        super().__init__(message, status_code=401)


class LocationNotFoundError(OpenWeatherMapError):
    """Raised when the requested location/city is not found (404)."""

    def __init__(self, message: str = "Location or city not found"):
        super().__init__(message, status_code=404)


class BadRequestError(OpenWeatherMapError):
    """Raised when the request has invalid parameters (400)."""

    def __init__(self, message: str, parameters: list[str] = None):
        super().__init__(message, status_code=400, parameters=parameters)


class RateLimitError(OpenWeatherMapError):
    """Raised when the API rate limit is exceeded (429)."""

    def __init__(self, message: str = "API rate limit exceeded. Please try again later."):
        super().__init__(message, status_code=429)


class ServerError(OpenWeatherMapError):
    """Raised when the OpenWeatherMap server encounters an error (5xx)."""

    def __init__(self, message: str = "OpenWeatherMap server error. Please try again later."):
        super().__init__(message, status_code=500)
