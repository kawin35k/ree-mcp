"""Centralized indicator configuration and constants.

This module provides a single source of truth for all REE indicator IDs
and their metadata, following the DRY principle.
"""

from dataclasses import dataclass
from enum import Enum


class IndicatorCategory(str, Enum):
    """Categories of electricity indicators."""

    DEMAND = "demand"
    GENERATION = "generation"
    PRICE = "price"
    EMISSION = "emission"
    EXCHANGE = "exchange"
    STORAGE = "storage"


@dataclass(frozen=True)
class IndicatorMetadata:
    """Metadata for an indicator."""

    id: int
    name: str
    category: IndicatorCategory
    description: str = ""


class IndicatorIDs:
    """Centralized repository of indicator IDs.

    This class eliminates magic numbers throughout the codebase and provides
    a single source of truth for indicator configuration.
    """

    # Demand Indicators
    REAL_DEMAND_PENINSULAR = IndicatorMetadata(
        id=1293,
        name="Real Demand (Peninsular)",
        category=IndicatorCategory.DEMAND,
        description="Real-time electricity demand in the Peninsular system (MW, 5 min)",
    )

    REAL_DEMAND_NATIONAL = IndicatorMetadata(
        id=2037,
        name="Real Demand (National)",
        category=IndicatorCategory.DEMAND,
        description="Real-time electricity demand for all of Spain (MW, 5 min)",
    )

    DEMAND_FORECAST = IndicatorMetadata(
        id=1292,
        name="Demand Forecast",
        category=IndicatorCategory.DEMAND,
        description="Forecasted electricity demand (MW, hourly)",
    )

    REAL_DEMAND_SUM_GENERATION = IndicatorMetadata(
        id=10004,
        name="Real Demand Sum of Generation",
        category=IndicatorCategory.DEMAND,
        description="Real demand calculated from generation sum",
    )

    MAX_DAILY_DEMAND = IndicatorMetadata(
        id=624,
        name="Maximum Daily Real Demand",
        category=IndicatorCategory.DEMAND,
        description="Maximum demand reached during the day (MW)",
    )

    MIN_DAILY_DEMAND = IndicatorMetadata(
        id=625,
        name="Minimum Daily Real Demand",
        category=IndicatorCategory.DEMAND,
        description="Minimum demand reached during the day (MW)",
    )

    # Generation Indicators - Synchronous Sources (provide inertia)
    NUCLEAR = IndicatorMetadata(
        id=549,
        name="Nuclear Generation",
        category=IndicatorCategory.GENERATION,
        description="Nuclear power generation (MW, 5 min)",
    )

    COMBINED_CYCLE_NATIONAL = IndicatorMetadata(
        id=2041,
        name="Combined Cycle (National)",
        category=IndicatorCategory.GENERATION,
        description="Combined cycle gas power generation (MW, 5 min)",
    )

    HYDRO_NATIONAL = IndicatorMetadata(
        id=2042,
        name="Hydroelectric (National)",
        category=IndicatorCategory.GENERATION,
        description="Hydroelectric power generation (MW, 5 min)",
    )

    COAL = IndicatorMetadata(
        id=547,
        name="Coal Generation",
        category=IndicatorCategory.GENERATION,
        description="Coal power generation (MW, 5 min)",
    )

    FUEL_GAS = IndicatorMetadata(
        id=548,
        name="Fuel/Gas Generation",
        category=IndicatorCategory.GENERATION,
        description="Fuel and gas power generation (MW, 5 min)",
    )

    # Generation Indicators - Variable Renewables (no inertia)
    WIND_NATIONAL = IndicatorMetadata(
        id=2038,
        name="Wind (National)",
        category=IndicatorCategory.GENERATION,
        description="Wind power generation for all of Spain (MW, 5 min)",
    )

    SOLAR_PV_PENINSULAR = IndicatorMetadata(
        id=1295,
        name="Solar PV (Peninsular)",
        category=IndicatorCategory.GENERATION,
        description="Solar photovoltaic generation in Peninsular system (MW, 5 min)",
    )

    SOLAR_PV_NATIONAL = IndicatorMetadata(
        id=2044,
        name="Solar PV (National)",
        category=IndicatorCategory.GENERATION,
        description="Solar photovoltaic generation for all of Spain (MW, 5 min)",
    )

    SOLAR_THERMAL_PENINSULAR = IndicatorMetadata(
        id=1294,
        name="Solar Thermal (Peninsular)",
        category=IndicatorCategory.GENERATION,
        description="Solar thermal generation in Peninsular system (MW, 5 min)",
    )

    SOLAR_THERMAL_NATIONAL = IndicatorMetadata(
        id=2045,
        name="Solar Thermal (National)",
        category=IndicatorCategory.GENERATION,
        description="Solar thermal generation for all of Spain (MW, 5 min)",
    )

    # Price Indicators
    SPOT_MARKET_PRICE = IndicatorMetadata(
        id=600,
        name="SPOT Market Price",
        category=IndicatorCategory.PRICE,
        description="Daily SPOT market electricity price (€/MWh). "
        "NOTE: Returns data for multiple European countries "
        "(Spain/Península, Portugal, France, Belgium, Netherlands, Germany). "
        "Filter by geo_scope='Península' for Spanish market only.",
    )

    PVPC_RATE = IndicatorMetadata(
        id=1013,
        name="PVPC Rate",
        category=IndicatorCategory.PRICE,
        description="Regulated electricity price for consumers (€/MWh, hourly)",
    )

    # Emissions Indicators
    CO2_EMISSIONS = IndicatorMetadata(
        id=10355,
        name="CO₂ Emissions",
        category=IndicatorCategory.EMISSION,
        description="CO₂ emissions associated with real-time generation (tCO₂eq)",
    )

    # International Exchange Indicators
    EXPORT_ANDORRA = IndicatorMetadata(
        id=2068,
        name="Export to Andorra",
        category=IndicatorCategory.EXCHANGE,
        description="Electricity exported to Andorra (MW)",
    )

    IMPORT_ANDORRA = IndicatorMetadata(
        id=2073,
        name="Import from Andorra",
        category=IndicatorCategory.EXCHANGE,
        description="Electricity imported from Andorra (MW)",
    )

    EXPORT_MOROCCO = IndicatorMetadata(
        id=2069,
        name="Export to Morocco",
        category=IndicatorCategory.EXCHANGE,
        description="Electricity exported to Morocco (MW)",
    )

    IMPORT_MOROCCO = IndicatorMetadata(
        id=2074,
        name="Import from Morocco",
        category=IndicatorCategory.EXCHANGE,
        description="Electricity imported from Morocco (MW)",
    )

    EXPORT_PORTUGAL = IndicatorMetadata(
        id=2070,
        name="Export to Portugal",
        category=IndicatorCategory.EXCHANGE,
        description="Electricity exported to Portugal (MW)",
    )

    IMPORT_PORTUGAL = IndicatorMetadata(
        id=2075,
        name="Import from Portugal",
        category=IndicatorCategory.EXCHANGE,
        description="Electricity imported from Portugal (MW)",
    )

    EXPORT_FRANCE = IndicatorMetadata(
        id=2071,
        name="Export to France",
        category=IndicatorCategory.EXCHANGE,
        description="Electricity exported to France (MW)",
    )

    IMPORT_FRANCE = IndicatorMetadata(
        id=2076,
        name="Import from France",
        category=IndicatorCategory.EXCHANGE,
        description="Electricity imported from France (MW)",
    )

    # Storage Indicators
    PUMPING_CONSUMPTION = IndicatorMetadata(
        id=2078,
        name="Pumped Storage Consumption",
        category=IndicatorCategory.STORAGE,
        description="Energy consumed for pumping water to storage (MW)",
    )

    PUMPED_TURBINING = IndicatorMetadata(
        id=2079,
        name="Pumped Storage Turbining",
        category=IndicatorCategory.STORAGE,
        description="Energy released from pumped storage (MW)",
    )

    @classmethod
    def get_generation_mix_sources(cls) -> dict[str, IndicatorMetadata]:
        """Get indicators for generation mix analysis.

        Returns:
            Dictionary mapping source names to indicator metadata.
        """
        return {
            "nuclear": cls.NUCLEAR,
            "wind_national": cls.WIND_NATIONAL,
            "solar_pv_peninsular": cls.SOLAR_PV_PENINSULAR,
            "solar_thermal_peninsular": cls.SOLAR_THERMAL_PENINSULAR,
            "hydro_national": cls.HYDRO_NATIONAL,
            "combined_cycle_national": cls.COMBINED_CYCLE_NATIONAL,
        }

    @classmethod
    def get_renewable_sources(cls) -> dict[str, IndicatorMetadata]:
        """Get renewable generation indicators.

        Returns:
            Dictionary mapping source names to indicator metadata.
        """
        return {
            "wind_national": cls.WIND_NATIONAL,
            "solar_pv_national": cls.SOLAR_PV_NATIONAL,
            "solar_thermal_national": cls.SOLAR_THERMAL_NATIONAL,
            "hydro_national": cls.HYDRO_NATIONAL,
        }

    @classmethod
    def get_synchronous_sources(cls) -> dict[str, IndicatorMetadata]:
        """Get synchronous generation indicators (provide inertia).

        Returns:
            Dictionary mapping source names to indicator metadata.
        """
        return {
            "nuclear": cls.NUCLEAR,
            "combined_cycle": cls.COMBINED_CYCLE_NATIONAL,
            "hydro": cls.HYDRO_NATIONAL,
            "coal": cls.COAL,
            "fuel_gas": cls.FUEL_GAS,
        }

    @classmethod
    def get_variable_renewable_sources(cls) -> dict[str, IndicatorMetadata]:
        """Get variable renewable indicators (no inertia).

        Returns:
            Dictionary mapping source names to indicator metadata.
        """
        return {
            "wind": cls.WIND_NATIONAL,
            "solar_pv": cls.SOLAR_PV_NATIONAL,
            "solar_thermal": cls.SOLAR_THERMAL_NATIONAL,
        }

    @classmethod
    def get_international_exchanges(cls) -> dict[str, dict[str, IndicatorMetadata]]:
        """Get international exchange indicators by country.

        Returns:
            Dictionary mapping country names to export/import indicators.
        """
        return {
            "andorra": {
                "export": cls.EXPORT_ANDORRA,
                "import": cls.IMPORT_ANDORRA,
            },
            "morocco": {
                "export": cls.EXPORT_MOROCCO,
                "import": cls.IMPORT_MOROCCO,
            },
            "portugal": {
                "export": cls.EXPORT_PORTUGAL,
                "import": cls.IMPORT_PORTUGAL,
            },
            "france": {
                "export": cls.EXPORT_FRANCE,
                "import": cls.IMPORT_FRANCE,
            },
        }
