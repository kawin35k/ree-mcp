"""Indicator data aggregate."""

from dataclasses import dataclass

from .indicator import Indicator
from .indicator_value import IndicatorValue


@dataclass
class IndicatorData:
    """Aggregate root containing indicator metadata and values.

    Attributes:
        indicator: The indicator metadata
        values: List of time-series values
    """

    indicator: Indicator
    values: list[IndicatorValue]

    def __len__(self) -> int:
        """Return number of values."""
        return len(self.values)

    def is_empty(self) -> bool:
        """Check if there are no values."""
        return len(self.values) == 0

    def min_value(self) -> float | None:
        """Get minimum value."""
        if self.is_empty():
            return None
        return min(v.value for v in self.values)

    def max_value(self) -> float | None:
        """Get maximum value."""
        if self.is_empty():
            return None
        return max(v.value for v in self.values)

    def avg_value(self) -> float | None:
        """Get average value."""
        if self.is_empty():
            return None
        return sum(v.value for v in self.values) / len(self.values)

    def get_values_for_geo(self, geo_scope: str) -> list[IndicatorValue]:
        """Filter values by geographic scope.

        Args:
            geo_scope: Geographic scope to filter by

        Returns:
            List of values matching the geographic scope.
        """
        return [v for v in self.values if v.geo_scope.value == geo_scope]
