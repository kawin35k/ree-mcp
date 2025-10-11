"""Domain exceptions."""


class DomainException(Exception):
    """Base exception for domain errors."""

    pass


class InvalidIndicatorIdError(DomainException):
    """Raised when an indicator ID is invalid."""

    def __init__(self, indicator_id: int) -> None:
        super().__init__(f"Invalid indicator ID: {indicator_id}")
        self.indicator_id = indicator_id


class InvalidDateRangeError(DomainException):
    """Raised when a date range is invalid."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class IndicatorNotFoundError(DomainException):
    """Raised when an indicator is not found."""

    def __init__(self, indicator_id: int) -> None:
        super().__init__(f"Indicator not found: {indicator_id}")
        self.indicator_id = indicator_id


class NoDataAvailableError(DomainException):
    """Raised when no data is available for the requested period."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
