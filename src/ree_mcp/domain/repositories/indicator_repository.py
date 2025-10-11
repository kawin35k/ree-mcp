"""Indicator repository interface."""

from abc import ABC, abstractmethod

from ..entities import Indicator, IndicatorData
from ..value_objects import DateTimeRange, IndicatorId, TimeGranularity


class IndicatorRepository(ABC):
    """Repository interface for indicator data access.

    This interface is defined in the domain layer but implemented
    in the infrastructure layer, following the Dependency Inversion Principle.
    """

    @abstractmethod
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

        Raises:
            IndicatorNotFoundError: If indicator doesn't exist
            NoDataAvailableError: If no data available for the period
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    async def get_indicator_metadata(self, indicator_id: IndicatorId) -> Indicator:
        """Get metadata for a specific indicator.

        Args:
            indicator_id: The indicator ID

        Returns:
            Indicator metadata.

        Raises:
            IndicatorNotFoundError: If indicator doesn't exist
        """
        pass
