"""Integration tests for REE API client.

These tests use pytest-httpx to mock HTTP responses without hitting the real API.
"""

import pytest
from pytest_httpx import HTTPXMock

from src.ree_mcp.domain.exceptions import IndicatorNotFoundError, NoDataAvailableError
from src.ree_mcp.infrastructure.config import Settings
from src.ree_mcp.infrastructure.http import REEApiClient


@pytest.fixture
def settings() -> Settings:
    """Create test settings."""
    return Settings(
        ree_api_token="test_token",
        ree_api_base_url="https://api.esios.ree.es",
        request_timeout=10,
        max_retries=2,
        retry_backoff_factor=0.1,
    )


@pytest.fixture
def client(settings: Settings) -> REEApiClient:
    """Create test client."""
    return REEApiClient(settings)


class TestREEApiClient:
    """Tests for REE API client."""

    async def test_get_indicator_data_success(
        self, client: REEApiClient, httpx_mock: HTTPXMock
    ) -> None:
        """Test successful indicator data retrieval."""
        mock_response = {
            "indicator": {
                "id": 1293,
                "name": "Demanda real",
                "values": [
                    {
                        "value": 30000.0,
                        "datetime": "2025-10-08T00:00:00.000+02:00",
                        "datetime_utc": "2025-10-07T22:00:00Z",
                    }
                ],
            }
        }

        httpx_mock.add_response(
            url="https://api.esios.ree.es/indicators/1293?start_date=2025-10-08T00%3A00&end_date=2025-10-08T23%3A59",
            json=mock_response,
        )

        async with client:
            result = await client.get_indicator_data(
                indicator_id=1293,
                start_date="2025-10-08T00:00",
                end_date="2025-10-08T23:59",
            )

        assert result == mock_response
        assert result["indicator"]["id"] == 1293
        assert len(result["indicator"]["values"]) == 1

    async def test_get_indicator_data_with_time_trunc(
        self, client: REEApiClient, httpx_mock: HTTPXMock
    ) -> None:
        """Test indicator data retrieval with time granularity."""
        mock_response = {
            "indicator": {
                "id": 549,
                "name": "Nuclear",
                "values": [{"value": 59000.0}],
            }
        }

        httpx_mock.add_response(json=mock_response)

        async with client:
            result = await client.get_indicator_data(
                indicator_id=549,
                start_date="2025-10-08T00:00",
                end_date="2025-10-08T23:59",
                time_trunc="hour",
            )

        assert "indicator" in result

    async def test_get_indicator_data_not_found(
        self, client: REEApiClient, httpx_mock: HTTPXMock
    ) -> None:
        """Test 404 error handling."""
        httpx_mock.add_response(status_code=404)

        async with client:
            with pytest.raises(IndicatorNotFoundError):
                await client.get_indicator_data(
                    indicator_id=999999,
                    start_date="2025-10-08T00:00",
                    end_date="2025-10-08T23:59",
                )

    async def test_get_indicator_data_empty_values(
        self, client: REEApiClient, httpx_mock: HTTPXMock
    ) -> None:
        """Test handling of empty values."""
        mock_response = {"indicator": {"id": 1293, "name": "Test", "values": []}}

        httpx_mock.add_response(json=mock_response)

        async with client:
            with pytest.raises(NoDataAvailableError, match="No data available"):
                await client.get_indicator_data(
                    indicator_id=1293,
                    start_date="2025-10-08T00:00",
                    end_date="2025-10-08T23:59",
                )

    async def test_get_indicator_data_server_error_retry(
        self, client: REEApiClient, httpx_mock: HTTPXMock
    ) -> None:
        """Test retry on server error."""
        # First two attempts: 500 error
        httpx_mock.add_response(status_code=500)
        httpx_mock.add_response(status_code=500)
        # Third attempt: success
        httpx_mock.add_response(
            json={"indicator": {"id": 1293, "values": [{"value": 100.0}]}}
        )

        async with client:
            result = await client.get_indicator_data(
                indicator_id=1293,
                start_date="2025-10-08T00:00",
                end_date="2025-10-08T23:59",
            )

        assert "indicator" in result

    async def test_get_indicator_data_server_error_exhausted(
        self, client: REEApiClient, httpx_mock: HTTPXMock
    ) -> None:
        """Test that server errors eventually raise."""
        # All attempts fail
        httpx_mock.add_response(status_code=500)
        httpx_mock.add_response(status_code=500)
        httpx_mock.add_response(status_code=500)

        async with client:
            with pytest.raises(NoDataAvailableError, match="HTTP 500"):
                await client.get_indicator_data(
                    indicator_id=1293,
                    start_date="2025-10-08T00:00",
                    end_date="2025-10-08T23:59",
                )

    async def test_list_indicators(
        self, client: REEApiClient, httpx_mock: HTTPXMock
    ) -> None:
        """Test listing indicators."""
        mock_response = {
            "indicators": [
                {"id": 1, "name": "Indicator 1"},
                {"id": 2, "name": "Indicator 2"},
            ]
        }

        httpx_mock.add_response(json=mock_response)

        async with client:
            result = await client.list_indicators()

        assert "indicators" in result
        assert len(result["indicators"]) == 2

    async def test_list_indicators_with_pagination(
        self, client: REEApiClient, httpx_mock: HTTPXMock
    ) -> None:
        """Test listing indicators with pagination."""
        mock_response = {"indicators": [{"id": 1, "name": "Indicator 1"}]}

        httpx_mock.add_response(json=mock_response)

        async with client:
            result = await client.list_indicators(limit=50, offset=100)

        assert "indicators" in result

    async def test_context_manager_without_enter_raises(
        self, client: REEApiClient, httpx_mock: HTTPXMock
    ) -> None:
        """Test that using client without context manager raises error."""
        httpx_mock.add_response(json={"indicator": {"values": [{"value": 100.0}]}})

        with pytest.raises(RuntimeError, match="not initialized"):
            await client.get_indicator_data(
                indicator_id=1293,
                start_date="2025-10-08T00:00",
                end_date="2025-10-08T23:59",
            )
