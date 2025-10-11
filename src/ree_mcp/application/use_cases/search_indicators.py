"""Use case for searching indicators by keyword."""

from ...domain.repositories import IndicatorRepository
from ..dtos import IndicatorMetadataResponse


class SearchIndicatorsUseCase:
    """Use case for searching indicators by keyword.

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
        self, keyword: str, limit: int | None = None
    ) -> list[IndicatorMetadataResponse]:
        """Execute the use case.

        Args:
            keyword: Keyword to search for
            limit: Maximum number of results

        Returns:
            List of matching indicator metadata.
        """
        indicators = await self.repository.search_indicators(keyword=keyword, limit=limit)

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
