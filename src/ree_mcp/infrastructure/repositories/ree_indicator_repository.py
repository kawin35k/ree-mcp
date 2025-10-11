"""REE API implementation of IndicatorRepository."""

from datetime import datetime
from typing import Any

from ...domain.entities import Indicator, IndicatorData, IndicatorValue
from ...domain.repositories import IndicatorRepository
from ...domain.value_objects import (
    DateTimeRange,
    GeographicScope,
    IndicatorId,
    MeasurementUnit,
    TimeGranularity,
)
from ..http import REEApiClient


class REEIndicatorRepository(IndicatorRepository):
    """REE API implementation of the indicator repository.

    Attributes:
        client: REE API HTTP client
    """

    def __init__(self, client: REEApiClient) -> None:
        """Initialize the repository.

        Args:
            client: Initialized REE API client
        """
        self.client = client

    async def get_indicator_data(
        self,
        indicator_id: IndicatorId,
        date_range: DateTimeRange,
        time_granularity: TimeGranularity = TimeGranularity.RAW,
    ) -> IndicatorData:
        """Retrieve indicator data for a date range.

        Args:
            indicator_id: The indicator to retrieve
            date_range: Time range for the data
            time_granularity: Time aggregation level

        Returns:
            IndicatorData with metadata and values.
        """
        start_date, end_date = date_range.to_api_params()
        time_trunc = time_granularity.to_api_param()

        response = await self.client.get_indicator_data(
            indicator_id=int(indicator_id),
            start_date=start_date,
            end_date=end_date,
            time_trunc=time_trunc,
        )

        return self._parse_indicator_data_response(response)

    async def list_all_indicators(
        self,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[Indicator]:
        """List all available indicators.

        Args:
            limit: Maximum number of indicators to return
            offset: Number of indicators to skip

        Returns:
            List of available indicators.
        """
        response = await self.client.list_indicators(limit=limit, offset=offset)
        indicators_data = response.get("indicators", [])
        return [self._parse_indicator_metadata(ind) for ind in indicators_data]

    async def search_indicators(
        self,
        keyword: str,
        limit: int | None = None,
    ) -> list[Indicator]:
        """Search indicators by keyword.

        Args:
            keyword: Keyword to search for in indicator names
            limit: Maximum number of results

        Returns:
            List of matching indicators.
        """
        # Get all indicators and filter by keyword
        all_indicators = await self.list_all_indicators()
        keyword_lower = keyword.lower()

        matches = [
            ind
            for ind in all_indicators
            if keyword_lower in ind.name.lower() or keyword_lower in ind.short_name.lower()
        ]

        if limit:
            return matches[:limit]
        return matches

    async def get_indicator_metadata(self, indicator_id: IndicatorId) -> Indicator:
        """Get metadata for a specific indicator.

        Args:
            indicator_id: The indicator ID

        Returns:
            Indicator metadata.
        """
        # Fetch a minimal data range to get metadata
        date_range = DateTimeRange.last_n_hours(1)
        try:
            indicator_data = await self.get_indicator_data(
                indicator_id=indicator_id,
                date_range=date_range,
            )
            return indicator_data.indicator
        except Exception:
            # If that fails, try getting from the full list
            all_indicators = await self.list_all_indicators()
            for ind in all_indicators:
                if ind.id == indicator_id:
                    return ind
            # Re-raise the original exception if not found in list
            raise

    def _parse_indicator_data_response(self, response: dict[str, Any]) -> IndicatorData:
        """Parse API response into IndicatorData.

        Args:
            response: API response dictionary

        Returns:
            IndicatorData instance.
        """
        indicator_json = response["indicator"]
        indicator = self._parse_indicator_metadata(indicator_json)

        values = [
            self._parse_indicator_value(val_json) for val_json in indicator_json.get("values", [])
        ]

        return IndicatorData(indicator=indicator, values=values)

    def _parse_indicator_metadata(self, data: dict[str, Any]) -> Indicator:
        """Parse indicator metadata from API response.

        Args:
            data: Indicator metadata dictionary

        Returns:
            Indicator instance.
        """
        # Extract unit from magnitud field
        magnitud_list = data.get("magnitud", [])
        magnitud_name = magnitud_list[0].get("name", "") if magnitud_list else ""
        unit = MeasurementUnit.from_api_response(magnitud_name)

        # Extract frequency from tiempo field
        tiempo_list = data.get("tiempo", [])
        frequency = tiempo_list[0].get("name", "Unknown") if tiempo_list else "Unknown"

        # Extract geographic scope from geos field
        geos_list = data.get("geos", [])
        geo_name = geos_list[0].get("geo_name", "") if geos_list else ""
        geo_scope = GeographicScope.from_geo_name(geo_name)

        return Indicator(
            id=IndicatorId(data["id"]),
            name=data.get("name", ""),
            short_name=data.get("short_name", data.get("name", "")),
            description=data.get("description"),
            unit=unit,
            frequency=frequency,
            geo_scope=geo_scope,
        )

    def _parse_indicator_value(self, data: dict[str, Any]) -> IndicatorValue:
        """Parse indicator value from API response.

        Args:
            data: Value dictionary

        Returns:
            IndicatorValue instance.
        """
        # Parse datetime strings
        datetime_str = data.get("datetime", "")
        datetime_utc_str = data.get("datetime_utc", datetime_str)

        dt = datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))
        dt_utc = datetime.fromisoformat(datetime_utc_str.replace("Z", "+00:00"))

        # Get geographic scope
        geo_name = data.get("geo_name", "")
        geo_scope = GeographicScope.from_geo_name(geo_name)

        return IndicatorValue(
            value=float(data.get("value", 0.0)),
            datetime=dt,
            datetime_utc=dt_utc,
            geo_scope=geo_scope,
        )
