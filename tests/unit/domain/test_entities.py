"""Tests for domain entities."""

from datetime import datetime

from src.ree_mcp.domain.entities import Indicator, IndicatorData, IndicatorValue
from src.ree_mcp.domain.value_objects import (
    GeographicScope,
    IndicatorId,
    MeasurementUnit,
)


class TestIndicator:
    """Tests for Indicator entity."""

    def test_create_indicator(self) -> None:
        """Test creating an indicator."""
        indicator = Indicator(
            id=IndicatorId(1293),
            name="Demanda real",
            short_name="Demanda real",
            description="Real electricity demand",
            unit=MeasurementUnit.MW,
            frequency="5 minutes",
            geo_scope=GeographicScope.PENINSULAR,
        )

        assert int(indicator.id) == 1293
        assert indicator.name == "Demanda real"
        assert indicator.unit == MeasurementUnit.MW

    def test_indicator_equality_by_id(self) -> None:
        """Test that indicators are equal if they have the same ID."""
        ind1 = Indicator(
            id=IndicatorId(100),
            name="Test 1",
            short_name="T1",
            description=None,
            unit=MeasurementUnit.MW,
            frequency="Hour",
            geo_scope=GeographicScope.PENINSULAR,
        )
        ind2 = Indicator(
            id=IndicatorId(100),
            name="Test 2",
            short_name="T2",
            description=None,
            unit=MeasurementUnit.EUR_MWH,
            frequency="Day",
            geo_scope=GeographicScope.NATIONAL,
        )

        assert ind1 == ind2
        assert hash(ind1) == hash(ind2)

    def test_indicator_inequality(self) -> None:
        """Test that indicators with different IDs are not equal."""
        ind1 = Indicator(
            id=IndicatorId(100),
            name="Test 1",
            short_name="T1",
            description=None,
            unit=MeasurementUnit.MW,
            frequency="Hour",
            geo_scope=GeographicScope.PENINSULAR,
        )
        ind2 = Indicator(
            id=IndicatorId(200),
            name="Test 1",
            short_name="T1",
            description=None,
            unit=MeasurementUnit.MW,
            frequency="Hour",
            geo_scope=GeographicScope.PENINSULAR,
        )

        assert ind1 != ind2

    def test_is_demand_indicator(self) -> None:
        """Test demand indicator detection."""
        indicator = Indicator(
            id=IndicatorId(1293),
            name="Demanda real",
            short_name="Demanda",
            description=None,
            unit=MeasurementUnit.MW,
            frequency="5 minutes",
            geo_scope=GeographicScope.PENINSULAR,
        )

        assert indicator.is_demand_indicator() is True
        assert indicator.is_generation_indicator() is False
        assert indicator.is_price_indicator() is False

    def test_is_generation_indicator(self) -> None:
        """Test generation indicator detection."""
        indicator = Indicator(
            id=IndicatorId(549),
            name="Generación nuclear",
            short_name="Nuclear",
            description=None,
            unit=MeasurementUnit.MW,
            frequency="5 minutes",
            geo_scope=GeographicScope.PENINSULAR,
        )

        assert indicator.is_generation_indicator() is True
        assert indicator.is_demand_indicator() is False

    def test_is_price_indicator(self) -> None:
        """Test price indicator detection."""
        indicator = Indicator(
            id=IndicatorId(600),
            name="Precio mercado SPOT",
            short_name="Precio SPOT",
            description=None,
            unit=MeasurementUnit.EUR_MWH,
            frequency="Hour",
            geo_scope=GeographicScope.PENINSULAR,
        )

        assert indicator.is_price_indicator() is True
        assert indicator.is_generation_indicator() is False

    def test_is_emissions_indicator(self) -> None:
        """Test emissions indicator detection."""
        indicator = Indicator(
            id=IndicatorId(10355),
            name="CO2 Asociado Generación",
            short_name="CO2",
            description=None,
            unit=MeasurementUnit.TCO2EQ,
            frequency="5 minutes",
            geo_scope=GeographicScope.PENINSULAR,
        )

        assert indicator.is_emissions_indicator() is True


class TestIndicatorValue:
    """Tests for IndicatorValue entity."""

    def test_create_indicator_value(self) -> None:
        """Test creating an indicator value."""
        dt = datetime(2025, 10, 8, 12, 0)
        dt_utc = datetime(2025, 10, 8, 10, 0)

        value = IndicatorValue(
            value=35000.5,
            datetime=dt,
            datetime_utc=dt_utc,
            geo_scope=GeographicScope.PENINSULAR,
        )

        assert value.value == 35000.5
        assert value.datetime == dt
        assert value.datetime_utc == dt_utc
        assert value.geo_scope == GeographicScope.PENINSULAR

    def test_indicator_value_str(self) -> None:
        """Test string representation."""
        dt = datetime(2025, 10, 8, 12, 0)
        value = IndicatorValue(
            value=100.0,
            datetime=dt,
            datetime_utc=dt,
            geo_scope=GeographicScope.PENINSULAR,
        )

        str_repr = str(value)
        assert "100.0" in str_repr
        assert "2025-10-08" in str_repr
        assert "Península" in str_repr


class TestIndicatorData:
    """Tests for IndicatorData aggregate."""

    def test_create_indicator_data(self) -> None:
        """Test creating indicator data."""
        indicator = Indicator(
            id=IndicatorId(1293),
            name="Demanda real",
            short_name="Demanda",
            description=None,
            unit=MeasurementUnit.MW,
            frequency="5 minutes",
            geo_scope=GeographicScope.PENINSULAR,
        )

        dt = datetime(2025, 10, 8, 12, 0)
        values = [
            IndicatorValue(
                value=30000.0,
                datetime=dt,
                datetime_utc=dt,
                geo_scope=GeographicScope.PENINSULAR,
            ),
            IndicatorValue(
                value=31000.0,
                datetime=dt,
                datetime_utc=dt,
                geo_scope=GeographicScope.PENINSULAR,
            ),
        ]

        data = IndicatorData(indicator=indicator, values=values)

        assert data.indicator == indicator
        assert len(data) == 2
        assert data.is_empty() is False

    def test_indicator_data_empty(self) -> None:
        """Test empty indicator data."""
        indicator = Indicator(
            id=IndicatorId(1293),
            name="Test",
            short_name="T",
            description=None,
            unit=MeasurementUnit.MW,
            frequency="Hour",
            geo_scope=GeographicScope.PENINSULAR,
        )

        data = IndicatorData(indicator=indicator, values=[])

        assert len(data) == 0
        assert data.is_empty() is True
        assert data.min_value() is None
        assert data.max_value() is None
        assert data.avg_value() is None

    def test_indicator_data_statistics(self) -> None:
        """Test statistical calculations."""
        indicator = Indicator(
            id=IndicatorId(1293),
            name="Test",
            short_name="T",
            description=None,
            unit=MeasurementUnit.MW,
            frequency="Hour",
            geo_scope=GeographicScope.PENINSULAR,
        )

        dt = datetime(2025, 10, 8, 12, 0)
        values = [
            IndicatorValue(
                value=100.0,
                datetime=dt,
                datetime_utc=dt,
                geo_scope=GeographicScope.PENINSULAR,
            ),
            IndicatorValue(
                value=200.0,
                datetime=dt,
                datetime_utc=dt,
                geo_scope=GeographicScope.PENINSULAR,
            ),
            IndicatorValue(
                value=300.0,
                datetime=dt,
                datetime_utc=dt,
                geo_scope=GeographicScope.PENINSULAR,
            ),
        ]

        data = IndicatorData(indicator=indicator, values=values)

        assert data.min_value() == 100.0
        assert data.max_value() == 300.0
        assert data.avg_value() == 200.0

    def test_get_values_for_geo(self) -> None:
        """Test filtering values by geographic scope."""
        indicator = Indicator(
            id=IndicatorId(1293),
            name="Test",
            short_name="T",
            description=None,
            unit=MeasurementUnit.MW,
            frequency="Hour",
            geo_scope=GeographicScope.PENINSULAR,
        )

        dt = datetime(2025, 10, 8, 12, 0)
        values = [
            IndicatorValue(
                value=100.0,
                datetime=dt,
                datetime_utc=dt,
                geo_scope=GeographicScope.PENINSULAR,
            ),
            IndicatorValue(
                value=200.0,
                datetime=dt,
                datetime_utc=dt,
                geo_scope=GeographicScope.CANARIAS,
            ),
            IndicatorValue(
                value=300.0,
                datetime=dt,
                datetime_utc=dt,
                geo_scope=GeographicScope.PENINSULAR,
            ),
        ]

        data = IndicatorData(indicator=indicator, values=values)

        peninsular_values = data.get_values_for_geo("Península")
        assert len(peninsular_values) == 2
        assert all(v.geo_scope == GeographicScope.PENINSULAR for v in peninsular_values)

        canarias_values = data.get_values_for_geo("Canarias")
        assert len(canarias_values) == 1
