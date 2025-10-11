"""Use case for getting indicator data."""

from ...domain.repositories import IndicatorRepository
from ...domain.value_objects import DateTimeRange, IndicatorId, TimeGranularity
from ..dtos import GetIndicatorDataRequest, IndicatorDataResponse


class GetIndicatorDataUseCase:
    """Use case for retrieving indicator time-series data.

    Attributes:
        repository: Indicator repository implementation
    """

    def __init__(self, repository: IndicatorRepository) -> None:
        """Initialize use case.

        Args:
            repository: Indicator repository
        """
        self.repository = repository

    async def execute(self, request: GetIndicatorDataRequest) -> IndicatorDataResponse:
        """Execute the use case.

        Args:
            request: Request with indicator ID and date range

        Returns:
            Response with indicator data and statistics.

        Raises:
            InvalidIndicatorIdError: If indicator ID is invalid
            InvalidDateRangeError: If date range is invalid
            IndicatorNotFoundError: If indicator doesn't exist
            NoDataAvailableError: If no data available
        """
        # Convert request to domain objects
        indicator_id = IndicatorId(request.indicator_id)
        date_range = DateTimeRange.from_iso_strings(request.start_date, request.end_date)
        time_granularity = TimeGranularity(request.time_granularity)

        # Get data from repository
        indicator_data = await self.repository.get_indicator_data(
            indicator_id=indicator_id,
            date_range=date_range,
            time_granularity=time_granularity,
        )

        # Convert to response DTO
        return IndicatorDataResponse.from_domain(indicator_data)
