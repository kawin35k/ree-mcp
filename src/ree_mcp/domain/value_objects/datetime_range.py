"""Date-time range value object."""

from dataclasses import dataclass
from datetime import datetime, timedelta

from ..exceptions import InvalidDateRangeError


@dataclass(frozen=True)
class DateTimeRange:
    """Represents a date-time range with validation.

    Attributes:
        start: Start datetime (inclusive)
        end: End datetime (inclusive)
    """

    start: datetime
    end: datetime

    MAX_RANGE_DAYS = 366  # Maximum 1 year + 1 day

    def __post_init__(self) -> None:
        """Validate date range."""
        if self.start >= self.end:
            raise InvalidDateRangeError(
                f"Start date ({self.start}) must be before end date ({self.end})"
            )

        if (self.end - self.start).days > self.MAX_RANGE_DAYS:
            raise InvalidDateRangeError(
                f"Date range cannot exceed {self.MAX_RANGE_DAYS} days. "
                f"Requested: {(self.end - self.start).days} days"
            )

    def to_api_params(self) -> tuple[str, str]:
        """Convert to API parameters.

        Returns:
            Tuple of (start_date, end_date) in API format (YYYY-MM-DDTHH:MM).
        """
        start_str = self.start.strftime("%Y-%m-%dT%H:%M")
        end_str = self.end.strftime("%Y-%m-%dT%H:%M")
        return start_str, end_str

    def duration_days(self) -> int:
        """Get duration in days."""
        return (self.end - self.start).days

    @classmethod
    def from_iso_strings(cls, start: str, end: str) -> "DateTimeRange":
        """Create from ISO format strings.

        Args:
            start: Start datetime in ISO format
            end: End datetime in ISO format

        Returns:
            DateTimeRange instance.

        Raises:
            InvalidDateRangeError: If datetime strings are invalid.
        """
        try:
            start_dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
            end_dt = datetime.fromisoformat(end.replace("Z", "+00:00"))
            return cls(start=start_dt, end=end_dt)
        except (ValueError, AttributeError) as e:
            raise InvalidDateRangeError(f"Invalid datetime format: {e}") from e

    @classmethod
    def last_n_days(cls, days: int, end: datetime | None = None) -> "DateTimeRange":
        """Create a range for the last N days.

        Args:
            days: Number of days
            end: End datetime (defaults to now)

        Returns:
            DateTimeRange instance.
        """
        if end is None:
            end = datetime.now()
        start = end - timedelta(days=days)
        return cls(start=start, end=end)

    @classmethod
    def last_n_hours(cls, hours: int, end: datetime | None = None) -> "DateTimeRange":
        """Create a range for the last N hours.

        Args:
            hours: Number of hours
            end: End datetime (defaults to now)

        Returns:
            DateTimeRange instance.
        """
        if end is None:
            end = datetime.now()
        start = end - timedelta(hours=hours)
        return cls(start=start, end=end)
