"""Response DTOs for indicator operations."""

from pydantic import BaseModel, Field

from ...domain.entities import IndicatorData


class IndicatorValueResponse(BaseModel):
    """Single indicator value response.

    Attributes:
        value: The numeric value
        datetime: Timestamp (ISO format)
        datetime_utc: UTC timestamp (ISO format)
        geo_scope: Geographic scope
    """

    value: float
    datetime: str
    datetime_utc: str
    geo_scope: str


class IndicatorMetadataResponse(BaseModel):
    """Indicator metadata response.

    Attributes:
        id: Indicator ID
        name: Full name
        short_name: Abbreviated name
        description: Optional description
        unit: Measurement unit
        frequency: Update frequency
        geo_scope: Geographic scope
    """

    id: int
    name: str
    short_name: str
    description: str | None
    unit: str
    frequency: str
    geo_scope: str


class IndicatorDataResponse(BaseModel):
    """Complete indicator data response.

    Attributes:
        indicator: Indicator metadata
        values: List of time-series values
        statistics: Optional statistics about the data
    """

    indicator: IndicatorMetadataResponse
    values: list[IndicatorValueResponse]
    statistics: dict[str, float | None] = Field(
        default_factory=dict, description="Statistical summary of values"
    )

    @classmethod
    def from_domain(cls, data: IndicatorData) -> "IndicatorDataResponse":
        """Create response from domain entity.

        Args:
            data: Domain IndicatorData entity

        Returns:
            IndicatorDataResponse instance.
        """
        indicator_response = IndicatorMetadataResponse(
            id=int(data.indicator.id),
            name=data.indicator.name,
            short_name=data.indicator.short_name,
            description=data.indicator.description,
            unit=data.indicator.unit.value,
            frequency=data.indicator.frequency,
            geo_scope=data.indicator.geo_scope.value,
        )

        values_response = [
            IndicatorValueResponse(
                value=val.value,
                datetime=val.datetime.isoformat(),
                datetime_utc=val.datetime_utc.isoformat(),
                geo_scope=val.geo_scope.value,
            )
            for val in data.values
        ]

        statistics = {
            "count": len(data.values),
            "min": data.min_value(),
            "max": data.max_value(),
            "avg": data.avg_value(),
        }

        return cls(
            indicator=indicator_response,
            values=values_response,
            statistics=statistics,
        )
