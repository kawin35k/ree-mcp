"""Time granularity value object."""

from enum import Enum


class TimeGranularity(str, Enum):
    """Time granularity for data aggregation.

    Attributes:
        RAW: Raw data (5-minute intervals for most indicators)
        FIFTEEN_MINUTES: 15-minute aggregates
        HOUR: Hourly aggregates
        DAY: Daily aggregates
    """

    RAW = "raw"
    FIFTEEN_MINUTES = "fifteen_minutes"
    HOUR = "hour"
    DAY = "day"

    def to_api_param(self) -> str | None:
        """Convert to API parameter value.

        Returns:
            API parameter value or None for raw data.
        """
        if self == TimeGranularity.RAW:
            return None
        return self.value
