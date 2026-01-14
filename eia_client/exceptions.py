"""Custom exceptions for EIA API client."""


class EIAException(Exception):
    """Base exception for EIA API errors."""
    pass


class EIAAuthenticationError(EIAException):
    """Raised when API key is invalid or missing."""
    pass


class EIARateLimitError(EIAException):
    """Raised when API rate limit is exceeded."""
    pass


class EIARequestError(EIAException):
    """Raised when API request fails."""

    def __init__(self, message: str, status_code: int = None, response: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class EIAValidationError(EIAException):
    """Raised when request parameters are invalid."""
    pass


class EIADataNotFoundError(EIAException):
    """Raised when requested data is not found."""
    pass
