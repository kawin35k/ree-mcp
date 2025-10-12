"""Unit tests for indicator configuration."""

from src.ree_mcp.interface.indicator_config import (
    IndicatorCategory,
    IndicatorIDs,
    IndicatorMetadata,
)


class TestIndicatorMetadata:
    """Tests for IndicatorMetadata class."""

    def test_indicator_metadata_creation(self) -> None:
        """Test creating indicator metadata."""
        metadata = IndicatorMetadata(
            id=123, name="Test Indicator", category=IndicatorCategory.DEMAND, description="Test"
        )

        assert metadata.id == 123
        assert metadata.name == "Test Indicator"
        assert metadata.category == IndicatorCategory.DEMAND
        assert metadata.description == "Test"

    def test_indicator_metadata_immutable(self) -> None:
        """Test that indicator metadata is frozen (immutable)."""
        metadata = IndicatorMetadata(
            id=123, name="Test", category=IndicatorCategory.GENERATION
        )

        # Should not be able to modify attributes
        try:
            metadata.id = 456  # type: ignore[misc]
            raise AssertionError("Should not be able to modify frozen dataclass")
        except (AttributeError, Exception):
            pass  # Expected - frozen dataclass


class TestIndicatorIDs:
    """Tests for IndicatorIDs class."""

    def test_demand_indicators_exist(self) -> None:
        """Test that demand indicators are defined."""
        assert IndicatorIDs.REAL_DEMAND_PENINSULAR.id == 1293
        assert IndicatorIDs.REAL_DEMAND_NATIONAL.id == 2037
        assert IndicatorIDs.DEMAND_FORECAST.id == 1292
        assert IndicatorIDs.MAX_DAILY_DEMAND.id == 624
        assert IndicatorIDs.MIN_DAILY_DEMAND.id == 625

    def test_generation_indicators_exist(self) -> None:
        """Test that generation indicators are defined."""
        assert IndicatorIDs.NUCLEAR.id == 549
        assert IndicatorIDs.WIND_NATIONAL.id == 2038
        assert IndicatorIDs.SOLAR_PV_PENINSULAR.id == 1295
        assert IndicatorIDs.COMBINED_CYCLE_NATIONAL.id == 2041
        assert IndicatorIDs.HYDRO_NATIONAL.id == 2042

    def test_price_indicators_exist(self) -> None:
        """Test that price indicators are defined."""
        assert IndicatorIDs.SPOT_MARKET_PRICE.id == 600
        assert IndicatorIDs.PVPC_RATE.id == 1013

    def test_emission_indicators_exist(self) -> None:
        """Test that emission indicators are defined."""
        assert IndicatorIDs.CO2_EMISSIONS.id == 10355

    def test_exchange_indicators_exist(self) -> None:
        """Test that exchange indicators are defined."""
        assert IndicatorIDs.EXPORT_ANDORRA.id == 2068
        assert IndicatorIDs.IMPORT_ANDORRA.id == 2073
        assert IndicatorIDs.EXPORT_MOROCCO.id == 2069
        assert IndicatorIDs.IMPORT_MOROCCO.id == 2074

    def test_storage_indicators_exist(self) -> None:
        """Test that storage indicators are defined."""
        assert IndicatorIDs.PUMPING_CONSUMPTION.id == 2078
        assert IndicatorIDs.PUMPED_TURBINING.id == 2079

    def test_get_generation_mix_sources(self) -> None:
        """Test retrieving generation mix sources."""
        sources = IndicatorIDs.get_generation_mix_sources()

        assert isinstance(sources, dict)
        assert "nuclear" in sources
        assert "wind_national" in sources
        assert "solar_pv_peninsular" in sources
        assert sources["nuclear"].id == 549
        assert sources["wind_national"].id == 2038

    def test_get_renewable_sources(self) -> None:
        """Test retrieving renewable sources."""
        sources = IndicatorIDs.get_renewable_sources()

        assert isinstance(sources, dict)
        assert "wind_national" in sources
        assert "solar_pv_national" in sources
        assert "solar_thermal_national" in sources
        assert "hydro_national" in sources
        assert len(sources) == 4

    def test_get_synchronous_sources(self) -> None:
        """Test retrieving synchronous sources."""
        sources = IndicatorIDs.get_synchronous_sources()

        assert isinstance(sources, dict)
        assert "nuclear" in sources
        assert "combined_cycle" in sources
        assert "hydro" in sources
        assert "coal" in sources
        assert "fuel_gas" in sources
        assert len(sources) == 5

    def test_get_variable_renewable_sources(self) -> None:
        """Test retrieving variable renewable sources."""
        sources = IndicatorIDs.get_variable_renewable_sources()

        assert isinstance(sources, dict)
        assert "wind" in sources
        assert "solar_pv" in sources
        assert "solar_thermal" in sources
        assert len(sources) == 3

    def test_get_international_exchanges(self) -> None:
        """Test retrieving international exchange indicators."""
        exchanges = IndicatorIDs.get_international_exchanges()

        assert isinstance(exchanges, dict)
        assert "andorra" in exchanges
        assert "morocco" in exchanges
        assert "portugal" in exchanges
        assert "france" in exchanges

        # Check structure
        assert "export" in exchanges["andorra"]
        assert "import" in exchanges["andorra"]
        assert exchanges["andorra"]["export"].id == 2068
        assert exchanges["andorra"]["import"].id == 2073

    def test_indicator_categories_are_correct(self) -> None:
        """Test that indicators have correct categories."""
        assert IndicatorIDs.REAL_DEMAND_PENINSULAR.category == IndicatorCategory.DEMAND
        assert IndicatorIDs.NUCLEAR.category == IndicatorCategory.GENERATION
        assert IndicatorIDs.SPOT_MARKET_PRICE.category == IndicatorCategory.PRICE
        assert IndicatorIDs.CO2_EMISSIONS.category == IndicatorCategory.EMISSION
        assert IndicatorIDs.EXPORT_ANDORRA.category == IndicatorCategory.EXCHANGE
        assert IndicatorIDs.PUMPING_CONSUMPTION.category == IndicatorCategory.STORAGE

    def test_indicator_metadata_has_names(self) -> None:
        """Test that all indicators have meaningful names."""
        assert IndicatorIDs.REAL_DEMAND_PENINSULAR.name != ""
        assert IndicatorIDs.NUCLEAR.name != ""
        assert "Demand" in IndicatorIDs.REAL_DEMAND_PENINSULAR.name
        assert "Nuclear" in IndicatorIDs.NUCLEAR.name
