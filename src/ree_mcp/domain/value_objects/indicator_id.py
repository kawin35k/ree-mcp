"""Indicator ID value object."""

from dataclasses import dataclass

from ..exceptions import InvalidIndicatorIdError


@dataclass(frozen=True)
class IndicatorId:
    """Strongly typed indicator identifier.

    Attributes:
        value: The indicator ID (must be positive)
    """

    value: int

    def __post_init__(self) -> None:
        """Validate indicator ID."""
        if self.value <= 0:
            raise InvalidIndicatorIdError(self.value)

    def __int__(self) -> int:
        """Convert to int."""
        return self.value

    def __str__(self) -> str:
        """Convert to string."""
        return str(self.value)
