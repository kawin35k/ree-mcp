"""Tests for domain value objects."""

from datetime import datetime, timedelta

import pytest

from src.ree_mcp.domain.exceptions import InvalidDateRangeError, InvalidIndicatorIdError
from src.ree_mcp.domain.value_objects import (
    DateTimeRange,
    GeographicScope,
    IndicatorId,
    MeasurementUnit,
    TimeGranularity,
)


class TestIndicatorId:
    """Tests for IndicatorId value object."""

    def test_valid_indicator_id(self) -> None:
        """Test creating valid indicator ID."""
        indicator_id = IndicatorId(1293)
        assert indicator_id.value == 1293
        assert int(indicator_id) == 1293
        assert str(indicator_id) == "1293"

    def test_invalid_indicator_id_zero(self) -> None:
        """Test that zero indicator ID raises error."""
        with pytest.raises(InvalidIndicatorIdError):
            IndicatorId(0)

    def test_invalid_indicator_id_negative(self) -> None:
        """Test that negative indicator ID raises error."""
        with pytest.raises(InvalidIndicatorIdError):
            IndicatorId(-1)

    def test_indicator_id_immutable(self) -> None:
        """Test that IndicatorId is immutable."""
        indicator_id = IndicatorId(100)
        with pytest.raises(AttributeError):
            indicator_id.value = 200  # type: ignore[misc]


class TestDateTimeRange:
    """Tests for DateTimeRange value object."""

    def test_valid_date_range(self) -> None:
        """Test creating valid date range."""
        start = datetime(2025, 10, 8, 0, 0)
        end = datetime(2025, 10, 8, 23, 59)
        date_range = DateTimeRange(start=start, end=end)

        assert date_range.start == start
        assert date_range.end == end

    def test_invalid_date_range_start_after_end(self) -> None:
        """Test that start after end raises error."""
        start = datetime(2025, 10, 9, 0, 0)
        end = datetime(2025, 10, 8, 0, 0)

        with pytest.raises(InvalidDateRangeError, match="must be before"):
            DateTimeRange(start=start, end=end)

    def test_invalid_date_range_equal(self) -> None:
        """Test that equal dates raise error."""
        dt = datetime(2025, 10, 8, 0, 0)

        with pytest.raises(InvalidDateRangeError):
            DateTimeRange(start=dt, end=dt)

    def test_invalid_date_range_too_long(self) -> None:
        """Test that range exceeding max days raises error."""
        start = datetime(2025, 1, 1, 0, 0)
        end = datetime(2026, 12, 31, 23, 59)  # More than 366 days

        with pytest.raises(InvalidDateRangeError, match="cannot exceed"):
            DateTimeRange(start=start, end=end)

    def test_to_api_params(self) -> None:
        """Test conversion to API parameters."""
        start = datetime(2025, 10, 8, 12, 30)
        end = datetime(2025, 10, 8, 18, 45)
        date_range = DateTimeRange(start=start, end=end)

        start_str, end_str = date_range.to_api_params()
        assert start_str == "2025-10-08T12:30"
        assert end_str == "2025-10-08T18:45"

    def test_duration_days(self) -> None:
        """Test duration calculation."""
        start = datetime(2025, 10, 8, 0, 0)
        end = datetime(2025, 10, 11, 0, 0)
        date_range = DateTimeRange(start=start, end=end)

        assert date_range.duration_days() == 3

    def test_from_iso_strings(self) -> None:
        """Test creating from ISO strings."""
        date_range = DateTimeRange.from_iso_strings("2025-10-08T00:00", "2025-10-08T23:59")

        assert date_range.start.year == 2025
        assert date_range.start.month == 10
        assert date_range.start.day == 8
        assert date_range.end.hour == 23

    def test_from_iso_strings_with_z(self) -> None:
        """Test creating from ISO strings with Z suffix."""
        date_range = DateTimeRange.from_iso_strings("2025-10-08T00:00Z", "2025-10-08T23:59Z")

        assert date_range.start.year == 2025

    def test_from_iso_strings_invalid(self) -> None:
        """Test that invalid ISO strings raise error."""
        with pytest.raises(InvalidDateRangeError, match="Invalid datetime format"):
            DateTimeRange.from_iso_strings("invalid", "2025-10-08T23:59")

    def test_last_n_days(self) -> None:
        """Test creating range for last N days."""
        end = datetime(2025, 10, 10, 12, 0)
        date_range = DateTimeRange.last_n_days(3, end=end)

        assert date_range.duration_days() == 3
        assert date_range.end == end
        assert date_range.start == end - timedelta(days=3)

    def test_last_n_hours(self) -> None:
        """Test creating range for last N hours."""
        end = datetime(2025, 10, 10, 12, 0)
        date_range = DateTimeRange.last_n_hours(6, end=end)

        assert date_range.end == end
        assert date_range.start == end - timedelta(hours=6)


class TestTimeGranularity:
    """Tests for TimeGranularity enum."""

    def test_time_granularity_values(self) -> None:
        """Test all time granularity values."""
        assert TimeGranularity.RAW.value == "raw"
        assert TimeGranularity.HOUR.value == "hour"
        assert TimeGranularity.DAY.value == "day"
        assert TimeGranularity.FIFTEEN_MINUTES.value == "fifteen_minutes"

    def test_to_api_param_raw(self) -> None:
        """Test converting RAW to API param returns None."""
        assert TimeGranularity.RAW.to_api_param() is None

    def test_to_api_param_hour(self) -> None:
        """Test converting other granularities to API param."""
        assert TimeGranularity.HOUR.to_api_param() == "hour"
        assert TimeGranularity.DAY.to_api_param() == "day"
        assert TimeGranularity.FIFTEEN_MINUTES.to_api_param() == "fifteen_minutes"


class TestMeasurementUnit:
    """Tests for MeasurementUnit enum."""

    def test_measurement_unit_values(self) -> None:
        """Test all measurement unit values."""
        assert MeasurementUnit.MW.value == "MW"
        assert MeasurementUnit.EUR_MWH.value == "€/MWh"
        assert MeasurementUnit.TCO2EQ.value == "tCO₂eq"

    def test_from_api_response_power(self) -> None:
        """Test parsing power unit from API."""
        assert MeasurementUnit.from_api_response("Potencia") == MeasurementUnit.MW

    def test_from_api_response_price(self) -> None:
        """Test parsing price unit from API."""
        assert MeasurementUnit.from_api_response("Precio") == MeasurementUnit.EUR_MWH

    def test_from_api_response_emissions(self) -> None:
        """Test parsing emissions unit from API."""
        assert MeasurementUnit.from_api_response("CO2 emisiones") == MeasurementUnit.TCO2EQ

    def test_from_api_response_none(self) -> None:
        """Test parsing None returns NONE unit."""
        assert MeasurementUnit.from_api_response(None) == MeasurementUnit.NONE

    def test_from_api_response_unknown(self) -> None:
        """Test parsing unknown unit returns NONE."""
        assert MeasurementUnit.from_api_response("Unknown") == MeasurementUnit.NONE


class TestGeographicScope:
    """Tests for GeographicScope enum."""

    def test_geographic_scope_values(self) -> None:
        """Test all geographic scope values."""
        assert GeographicScope.PENINSULAR.value == "Península"
        assert GeographicScope.NATIONAL.value == "Nacional"
        assert GeographicScope.CANARIAS.value == "Canarias"

    def test_from_geo_name_peninsular(self) -> None:
        """Test parsing peninsular from API."""
        assert GeographicScope.from_geo_name("Península") == GeographicScope.PENINSULAR

    def test_from_geo_name_national(self) -> None:
        """Test parsing national from API."""
        assert GeographicScope.from_geo_name("Nacional") == GeographicScope.NATIONAL

    def test_from_geo_name_none(self) -> None:
        """Test parsing None defaults to peninsular."""
        assert GeographicScope.from_geo_name(None) == GeographicScope.PENINSULAR

    def test_from_geo_name_unknown(self) -> None:
        """Test parsing unknown defaults to peninsular."""
        assert GeographicScope.from_geo_name("Unknown") == GeographicScope.PENINSULAR
