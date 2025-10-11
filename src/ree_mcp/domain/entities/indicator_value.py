"""Indicator value entity."""

from dataclasses import dataclass
from datetime import datetime as dt

from ..value_objects import GeographicScope


@dataclass
class IndicatorValue:
    """Represents a single value of an indicator at a point in time.

    Attributes:
        value: The numeric value
        datetime: Timestamp of the value
        datetime_utc: UTC timestamp
        geo_scope: Geographic scope of this value
    """

    value: float
    datetime: dt
    datetime_utc: dt
    geo_scope: GeographicScope

    def __str__(self) -> str:
        """String representation."""
        return (
            f"IndicatorValue(value={self.value}, "
            f"datetime={self.datetime.isoformat()}, "
            f"geo={self.geo_scope.value})"
        )
