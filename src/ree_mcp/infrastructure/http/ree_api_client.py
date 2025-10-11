"""REE API HTTP client with retry logic."""

import asyncio
from typing import Any

import httpx

from ...domain.exceptions import IndicatorNotFoundError, NoDataAvailableError
from ..config import Settings


class REEApiClient:
    """HTTP client for REE API with automatic retry logic.

    Attributes:
        base_url: Base URL for the API
        api_key: Authentication token
        timeout: Request timeout in seconds
        max_retries: Maximum retry attempts
        backoff_factor: Exponential backoff factor
    """

    def __init__(self, settings: Settings) -> None:
        """Initialize the API client.

        Args:
            settings: Application settings
        """
        self.base_url = settings.ree_api_base_url
        self.api_key = settings.ree_api_token
        self.timeout = settings.request_timeout
        self.max_retries = settings.max_retries
        self.backoff_factor = settings.retry_backoff_factor
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "REEApiClient":
        """Async context manager entry."""
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(self.timeout),
            headers={
                "Accept": "application/json",
                "x-api-key": self.api_key,
            },
        )
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()

    async def get_indicator_data(
        self,
        indicator_id: int,
        start_date: str,
        end_date: str,
        time_trunc: str | None = None,
    ) -> dict[str, Any]:
        """Get indicator data from the API.

        Args:
            indicator_id: The indicator ID
            start_date: Start date in format YYYY-MM-DDTHH:MM
            end_date: End date in format YYYY-MM-DDTHH:MM
            time_trunc: Time granularity (hour, day, fifteen_minutes)

        Returns:
            API response as dictionary.

        Raises:
            IndicatorNotFoundError: If indicator doesn't exist
            NoDataAvailableError: If no data available
        """
        params: dict[str, str] = {
            "start_date": start_date,
            "end_date": end_date,
        }
        if time_trunc:
            params["time_trunc"] = time_trunc

        url = f"/indicators/{indicator_id}"
        return await self._request_with_retry("GET", url, params=params)

    async def list_indicators(
        self,
        limit: int | None = None,
        offset: int = 0,
    ) -> dict[str, Any]:
        """List all indicators.

        Args:
            limit: Maximum number of indicators to return
            offset: Number of indicators to skip

        Returns:
            API response as dictionary.
        """
        params: dict[str, str | int] = {}
        if limit:
            params["limit"] = limit
        if offset:
            params["offset"] = offset

        return await self._request_with_retry("GET", "/indicators", params=params)

    async def _request_with_retry(
        self,
        method: str,
        url: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute HTTP request with exponential backoff retry.

        Args:
            method: HTTP method
            url: Request URL
            params: Query parameters

        Returns:
            Response JSON.

        Raises:
            IndicatorNotFoundError: If 404 error
            NoDataAvailableError: If response has empty values
            httpx.HTTPError: For other HTTP errors
        """
        if not self._client:
            raise RuntimeError("Client not initialized. Use async context manager.")

        last_exception: Exception | None = None

        for attempt in range(self.max_retries + 1):
            try:
                response = await self._client.request(
                    method=method,
                    url=url,
                    params=params,
                )

                # Handle HTTP errors
                if response.status_code == 404:
                    raise IndicatorNotFoundError(
                        int(url.split("/")[-1]) if url.split("/")[-1].isdigit() else 0
                    )
                elif response.status_code == 500:
                    # Server error - retry
                    if attempt < self.max_retries:
                        await self._backoff(attempt)
                        continue
                    raise NoDataAvailableError(
                        "API server error (HTTP 500). Service may be temporarily unavailable."
                    )

                response.raise_for_status()
                data: dict[str, Any] = response.json()

                # Check if response has empty values
                if "indicator" in data:
                    values = data["indicator"].get("values", [])
                    if not values:
                        raise NoDataAvailableError(
                            "No data available for the requested period"
                        )

                return data

            except httpx.TimeoutException as e:
                last_exception = e
                if attempt < self.max_retries:
                    await self._backoff(attempt)
                    continue
                raise

            except httpx.HTTPError as e:
                last_exception = e
                # Don't retry client errors (4xx) except 404 which is handled above
                if isinstance(e, httpx.HTTPStatusError) and 400 <= e.response.status_code < 500:
                    raise
                # Retry on network errors and 5xx
                if attempt < self.max_retries:
                    await self._backoff(attempt)
                    continue
                raise

        # If we've exhausted retries
        if last_exception:
            raise last_exception
        raise RuntimeError("Request failed without exception")

    async def _backoff(self, attempt: int) -> None:
        """Wait before retrying with exponential backoff.

        Args:
            attempt: Current attempt number (0-indexed)
        """
        wait_time = self.backoff_factor * (2**attempt)
        await asyncio.sleep(wait_time)
