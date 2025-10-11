"""Indicator entity."""

from dataclasses import dataclass

from ..value_objects import GeographicScope, IndicatorId, MeasurementUnit


@dataclass
class Indicator:
    """Represents an electricity indicator.

    Attributes:
        id: Unique identifier
        name: Full name of the indicator
        short_name: Abbreviated name
        description: Optional detailed description
        unit: Measurement unit
        frequency: Update frequency description
        geo_scope: Geographic scope
    """

    id: IndicatorId
    name: str
    short_name: str
    description: str | None
    unit: MeasurementUnit
    frequency: str
    geo_scope: GeographicScope

    def __eq__(self, other: object) -> bool:
        """Compare by ID."""
        if not isinstance(other, Indicator):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash by ID."""
        return hash(self.id)

    def is_demand_indicator(self) -> bool:
        """Check if this is a demand indicator."""
        name_lower = self.name.lower()
        return "demanda" in name_lower or "demand" in name_lower

    def is_generation_indicator(self) -> bool:
        """Check if this is a generation indicator."""
        name_lower = self.name.lower()
        return "generación" in name_lower or "generation" in name_lower

    def is_price_indicator(self) -> bool:
        """Check if this is a price indicator."""
        name_lower = self.name.lower()
        return "precio" in name_lower or "price" in name_lower

    def is_emissions_indicator(self) -> bool:
        """Check if this is an emissions indicator."""
        name_lower = self.name.lower()
        return "co2" in name_lower or "emisiones" in name_lower
