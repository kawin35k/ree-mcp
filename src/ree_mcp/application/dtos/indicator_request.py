"""Request DTOs for indicator operations."""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class GetIndicatorDataRequest(BaseModel):
    """Request to get indicator data.

    Attributes:
        indicator_id: The indicator ID
        start_date: Start datetime (ISO format)
        end_date: End datetime (ISO format)
        time_granularity: Time aggregation (raw, hour, day, fifteen_minutes)
    """

    indicator_id: int = Field(..., gt=0, description="Indicator ID (must be positive)")
    start_date: str = Field(..., description="Start datetime in ISO format")
    end_date: str = Field(..., description="End datetime in ISO format")
    time_granularity: str = Field(
        default="raw",
        description="Time granularity (raw, hour, day, fifteen_minutes)",
    )

    @field_validator("time_granularity")
    @classmethod
    def validate_time_granularity(cls, v: str) -> str:
        """Validate time granularity."""
        allowed = {"raw", "hour", "day", "fifteen_minutes"}
        if v not in allowed:
            raise ValueError(f"time_granularity must be one of {allowed}")
        return v

    @field_validator("start_date", "end_date")
    @classmethod
    def validate_datetime(cls, v: str) -> str:
        """Validate datetime format."""
        try:
            datetime.fromisoformat(v.replace("Z", "+00:00"))
        except (ValueError, AttributeError) as e:
            raise ValueError(f"Invalid datetime format: {e}") from e
        return v
