"""Helper classes for MCP tools.

This module provides reusable helper classes that eliminate code duplication
and follow DRY, KISS, and SOLID principles.
"""

import json
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

from ..application.use_cases import (
    GetIndicatorDataUseCase,
    ListIndicatorsUseCase,
    SearchIndicatorsUseCase,
)
from ..domain.exceptions import DomainException
from ..infrastructure.config import Settings, get_settings
from ..infrastructure.http import REEApiClient
from ..infrastructure.repositories import REEIndicatorRepository


class DateTimeHelper:
    """Helper class for date and time operations.

    Eliminates repeated datetime construction patterns throughout the codebase.
    """

    @staticmethod
    def build_datetime_range(date: str, hour: str) -> tuple[str, str]:
        """Build start and end datetime strings for a specific hour.

        Args:
            date: Date in YYYY-MM-DD format
            hour: Hour in HH format (00-23)

        Returns:
            Tuple of (start_datetime, end_datetime) in ISO format

        Examples:
            >>> DateTimeHelper.build_datetime_range("2025-10-08", "12")
            ('2025-10-08T12:00', '2025-10-08T12:59')
        """
        normalized_hour = hour.zfill(2)
        start_datetime = f"{date}T{normalized_hour}:00"
        end_datetime = f"{date}T{normalized_hour}:59"
        return start_datetime, end_datetime

    @staticmethod
    def build_day_range(date: str) -> tuple[str, str]:
        """Build start and end datetime strings for a full day.

        Args:
            date: Date in YYYY-MM-DD format

        Returns:
            Tuple of (start_datetime, end_datetime) in ISO format

        Examples:
            >>> DateTimeHelper.build_day_range("2025-10-08")
            ('2025-10-08T00:00', '2025-10-08T23:59')
        """
        return f"{date}T00:00", f"{date}T23:59"

    @staticmethod
    def validate_date_format(date: str) -> bool:
        """Validate date string format.

        Args:
            date: Date string to validate

        Returns:
            True if valid YYYY-MM-DD format

        Examples:
            >>> DateTimeHelper.validate_date_format("2025-10-08")
            True
            >>> DateTimeHelper.validate_date_format("10-08-2025")
            False
        """
        try:
            datetime.strptime(date, "%Y-%m-%d")
            return True
        except ValueError:
            return False


class ResponseFormatter:
    """Helper class for formatting tool responses.

    Provides consistent JSON formatting and error handling across all tools.
    Follows DRY principle by centralizing response formatting logic.
    """

    @staticmethod
    def success(data: dict[str, Any], indent: int = 2, ensure_ascii: bool = False) -> str:
        """Format a successful response.

        Args:
            data: Response data dictionary
            indent: JSON indentation level
            ensure_ascii: Whether to escape non-ASCII characters

        Returns:
            JSON string of the response data
        """
        return json.dumps(data, indent=indent, ensure_ascii=ensure_ascii)

    @staticmethod
    def error(message: str, error_type: str | None = None, indent: int = 2) -> str:
        """Format an error response.

        Args:
            message: Error message
            error_type: Optional error type/class name
            indent: JSON indentation level

        Returns:
            JSON string with error information
        """
        error_data: dict[str, Any] = {"error": message}
        if error_type:
            error_data["type"] = error_type
        return json.dumps(error_data, indent=indent)

    @staticmethod
    def domain_exception(exception: DomainException, indent: int = 2) -> str:
        """Format a domain exception response.

        Args:
            exception: Domain exception to format
            indent: JSON indentation level

        Returns:
            JSON string with exception details
        """
        return ResponseFormatter.error(
            message=str(exception), error_type=type(exception).__name__, indent=indent
        )

    @staticmethod
    def unexpected_error(exception: Exception, context: str = "", indent: int = 2) -> str:
        """Format an unexpected error response.

        Args:
            exception: Exception that occurred
            context: Optional context about what operation failed
            indent: JSON indentation level

        Returns:
            JSON string with error details
        """
        message = (
            f"{context}: {str(exception)}" if context else f"Unexpected error: {str(exception)}"
        )
        return ResponseFormatter.error(message=message, indent=indent)


class ToolExecutor:
    """Manages use case execution with proper dependency injection.

    This class eliminates the repeated pattern of creating settings, client,
    repository, and use case instances. It follows the Dependency Inversion
    Principle by managing dependencies centrally.

    Usage:
        async with ToolExecutor() as executor:
            result = await executor.get_indicator_data(...)
    """

    def __init__(self, settings: Settings | None = None):
        """Initialize the tool executor.

        Args:
            settings: Optional settings override (mainly for testing)
        """
        self._settings = settings or get_settings()
        self._client: REEApiClient | None = None
        self._repository: REEIndicatorRepository | None = None

    async def __aenter__(self) -> "ToolExecutor":
        """Async context manager entry."""
        self._client = REEApiClient(self._settings)
        await self._client.__aenter__()
        self._repository = REEIndicatorRepository(self._client)
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        if self._client:
            await self._client.__aexit__(exc_type, exc_val, exc_tb)

    @property
    def repository(self) -> REEIndicatorRepository:
        """Get the repository instance.

        Returns:
            Indicator repository

        Raises:
            RuntimeError: If called outside async context manager
        """
        if self._repository is None:
            raise RuntimeError("ToolExecutor must be used within async context manager")
        return self._repository

    def create_get_indicator_data_use_case(self) -> GetIndicatorDataUseCase:
        """Create a GetIndicatorDataUseCase instance.

        Returns:
            Configured use case instance
        """
        return GetIndicatorDataUseCase(self.repository)

    def create_list_indicators_use_case(self) -> ListIndicatorsUseCase:
        """Create a ListIndicatorsUseCase instance.

        Returns:
            Configured use case instance
        """
        return ListIndicatorsUseCase(self.repository)

    def create_search_indicators_use_case(self) -> SearchIndicatorsUseCase:
        """Create a SearchIndicatorsUseCase instance.

        Returns:
            Configured use case instance
        """
        return SearchIndicatorsUseCase(self.repository)


@asynccontextmanager
async def create_tool_executor(
    settings: Settings | None = None,
) -> AsyncIterator[ToolExecutor]:
    """Create a tool executor as an async context manager.

    This is a convenience function for creating a ToolExecutor with
    automatic cleanup.

    Args:
        settings: Optional settings override

    Yields:
        Configured ToolExecutor instance

    Example:
        async with create_tool_executor() as executor:
            use_case = executor.create_get_indicator_data_use_case()
            result = await use_case.execute(request)
    """
    executor = ToolExecutor(settings)
    async with executor:
        yield executor
