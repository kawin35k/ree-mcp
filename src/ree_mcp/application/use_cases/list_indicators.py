"""Use case for listing all indicators."""

from ...domain.repositories import IndicatorRepository
from ..dtos import IndicatorMetadataResponse


class ListIndicatorsUseCase:
    """Use case for listing all available indicators.

    Attributes:
        repository: Indicator repository implementation
    """

    def __init__(self, repository: IndicatorRepository) -> None:
        """Initialize use case.

        Args:
            repository: Indicator repository
        """
        self.repository = repository

    async def execute(
        self, limit: int | None = None, offset: int = 0
    ) -> list[IndicatorMetadataResponse]:
        """Execute the use case.

        Args:
            limit: Maximum number of indicators to return
            offset: Number of indicators to skip

        Returns:
            List of indicator metadata.
        """
        indicators = await self.repository.list_all_indicators(limit=limit, offset=offset)

        return [
            IndicatorMetadataResponse(
                id=int(ind.id),
                name=ind.name,
                short_name=ind.short_name,
                description=ind.description,
                unit=ind.unit.value,
                frequency=ind.frequency,
                geo_scope=ind.geo_scope.value,
            )
            for ind in indicators
        ]
