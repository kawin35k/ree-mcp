"""Measurement unit value object."""

from enum import Enum


class MeasurementUnit(str, Enum):
    """Measurement units for indicator values.

    Attributes:
        MW: Megawatts (power)
        MWH: Megawatt-hours (energy)
        EUR_MWH: Euros per megawatt-hour (price)
        TCO2EQ: Tonnes of CO2 equivalent (emissions)
        PERCENT: Percentage
        NONE: Dimensionless
    """

    MW = "MW"
    MWH = "MWh"
    EUR_MWH = "€/MWh"
    TCO2EQ = "tCO₂eq"
    PERCENT = "%"
    NONE = ""

    @classmethod
    def from_api_response(cls, magnitud: str | None) -> "MeasurementUnit":
        """Create from API response magnitude field.

        Args:
            magnitud: Magnitude from API (e.g., "Potencia", "Precio")

        Returns:
            Corresponding MeasurementUnit.
        """
        if not magnitud:
            return cls.NONE

        magnitud_lower = magnitud.lower()
        if "potencia" in magnitud_lower or "power" in magnitud_lower:
            return cls.MW
        elif "energía" in magnitud_lower or "energy" in magnitud_lower:
            return cls.MWH
        elif "precio" in magnitud_lower or "price" in magnitud_lower:
            return cls.EUR_MWH
        elif "co2" in magnitud_lower or "emisiones" in magnitud_lower:
            return cls.TCO2EQ
        elif "porcentaje" in magnitud_lower or "percent" in magnitud_lower:
            return cls.PERCENT
        else:
            return cls.NONE
