"""Geographic scope value object."""

from enum import Enum


class GeographicScope(str, Enum):
    """Geographic scope for indicators.

    Attributes:
        PENINSULAR: Peninsular Spain (mainland)
        NATIONAL: All Spain (including islands)
        CANARIAS: Canary Islands
        BALEARES: Balearic Islands
        CEUTA: Ceuta
        MELILLA: Melilla
    """

    PENINSULAR = "Península"
    NATIONAL = "Nacional"
    CANARIAS = "Canarias"
    BALEARES = "Baleares"
    CEUTA = "Ceuta"
    MELILLA = "Melilla"

    @classmethod
    def from_geo_name(cls, geo_name: str | None) -> "GeographicScope":
        """Create from API geo_name field.

        Args:
            geo_name: Geographic name from API

        Returns:
            Corresponding GeographicScope, defaults to PENINSULAR.
        """
        if not geo_name:
            return cls.PENINSULAR

        geo_lower = geo_name.lower()
        if "península" in geo_lower or "peninsular" in geo_lower:
            return cls.PENINSULAR
        elif "nacional" in geo_lower:
            return cls.NATIONAL
        elif "canarias" in geo_lower:
            return cls.CANARIAS
        elif "baleares" in geo_lower:
            return cls.BALEARES
        elif "ceuta" in geo_lower:
            return cls.CEUTA
        elif "melilla" in geo_lower:
            return cls.MELILLA
        else:
            return cls.PENINSULAR
