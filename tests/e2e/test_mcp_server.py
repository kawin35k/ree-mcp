"""End-to-end tests for MCP server.

These tests verify the full integration of all layers.
Note: Some tests are marked as integration tests that require the real API.
"""

import json

import pytest
from pytest_httpx import HTTPXMock

from src.ree_mcp.interface.mcp_server import (
    get_demand_summary,
    get_generation_mix,
    get_indicator_data,
    list_indicators,
    search_indicators,
)


class TestMCPServerTools:
    """Tests for MCP server tools."""

    async def test_get_indicator_data_tool(self, httpx_mock: HTTPXMock) -> None:
        """Test get_indicator_data tool."""
        mock_response = {
            "indicator": {
                "id": 1293,
                "name": "Demanda real",
                "short_name": "Demanda real",
                "magnitud": [{"name": "Potencia"}],
                "tiempo": [{"name": "Cinco minutos"}],
                "geos": [{"geo_name": "Península"}],
                "values": [
                    {
                        "value": 30000.0,
                        "datetime": "2025-10-08T00:00:00.000+02:00",
                        "datetime_utc": "2025-10-07T22:00:00Z",
                        "geo_name": "Península",
                    }
                ],
            }
        }

        httpx_mock.add_response(json=mock_response)

        result_str = await get_indicator_data(
            indicator_id=1293,
            start_date="2025-10-08T00:00",
            end_date="2025-10-08T23:59",
            time_granularity="hour",
        )

        result = json.loads(result_str)
        assert "indicator" in result
        assert "values" in result
        assert "statistics" in result
        assert result["indicator"]["id"] == 1293

    async def test_get_indicator_data_tool_invalid_id(self) -> None:
        """Test get_indicator_data tool with invalid ID."""
        result_str = await get_indicator_data(
            indicator_id=-1,
            start_date="2025-10-08T00:00",
            end_date="2025-10-08T23:59",
        )

        result = json.loads(result_str)
        assert "error" in result
        assert "InvalidIndicatorIdError" in result["type"]

    async def test_get_indicator_data_tool_invalid_date_range(self) -> None:
        """Test get_indicator_data tool with invalid date range."""
        result_str = await get_indicator_data(
            indicator_id=1293,
            start_date="2025-10-10T00:00",
            end_date="2025-10-08T23:59",  # End before start
        )

        result = json.loads(result_str)
        assert "error" in result

    async def test_list_indicators_tool(self, httpx_mock: HTTPXMock) -> None:
        """Test list_indicators tool."""
        mock_response = {
            "indicators": [
                {
                    "id": 1293,
                    "name": "Demanda real",
                    "short_name": "Demanda real",
                    "magnitud": [{"name": "Potencia"}],
                    "tiempo": [{"name": "Cinco minutos"}],
                    "geos": [{"geo_name": "Península"}],
                },
                {
                    "id": 549,
                    "name": "Nuclear",
                    "short_name": "Nuclear",
                    "magnitud": [{"name": "Potencia"}],
                    "tiempo": [{"name": "Cinco minutos"}],
                    "geos": [{"geo_name": "Península"}],
                },
            ]
        }

        httpx_mock.add_response(json=mock_response)

        result_str = await list_indicators(limit=50, offset=0)

        result = json.loads(result_str)
        assert "count" in result
        assert "indicators" in result
        assert result["count"] == 2
        assert len(result["indicators"]) == 2

    async def test_search_indicators_tool(self, httpx_mock: HTTPXMock) -> None:
        """Test search_indicators tool."""
        mock_response = {
            "indicators": [
                {
                    "id": 1293,
                    "name": "Demanda real",
                    "short_name": "Demanda real",
                    "magnitud": [{"name": "Potencia"}],
                    "tiempo": [{"name": "Cinco minutos"}],
                    "geos": [{"geo_name": "Península"}],
                },
                {
                    "id": 1292,
                    "name": "Demanda prevista",
                    "short_name": "Demanda prevista",
                    "magnitud": [{"name": "Potencia"}],
                    "tiempo": [{"name": "Hora"}],
                    "geos": [{"geo_name": "Península"}],
                },
            ]
        }

        httpx_mock.add_response(json=mock_response)

        result_str = await search_indicators(keyword="demanda", limit=10)

        result = json.loads(result_str)
        assert "keyword" in result
        assert "count" in result
        assert "indicators" in result
        assert result["keyword"] == "demanda"
        assert result["count"] == 2

    async def test_get_demand_summary_tool(self, httpx_mock: HTTPXMock) -> None:
        """Test get_demand_summary convenience tool."""
        mock_response = {
            "indicator": {
                "id": 1293,
                "name": "Demanda real",
                "short_name": "Demanda real",
                "magnitud": [{"name": "Potencia"}],
                "tiempo": [{"name": "Cinco minutos"}],
                "geos": [{"geo_name": "Península"}],
                "values": [
                    {
                        "value": 30000.0,
                        "datetime": "2025-10-08T00:00:00.000+02:00",
                        "datetime_utc": "2025-10-07T22:00:00Z",
                        "geo_name": "Península",
                    },
                    {
                        "value": 31000.0,
                        "datetime": "2025-10-08T01:00:00.000+02:00",
                        "datetime_utc": "2025-10-07T23:00:00Z",
                        "geo_name": "Península",
                    },
                ],
            }
        }

        httpx_mock.add_response(json=mock_response)

        result_str = await get_demand_summary(date="2025-10-08")

        result = json.loads(result_str)
        assert "date" in result
        assert "real_demand" in result
        assert result["date"] == "2025-10-08"

    async def test_get_generation_mix_tool(self, httpx_mock: HTTPXMock) -> None:
        """Test get_generation_mix convenience tool."""
        # Mock responses for all generation sources
        for _ in range(6):  # 6 sources
            httpx_mock.add_response(
                json={
                    "indicator": {
                        "id": 549,
                        "name": "Test",
                        "short_name": "Test",
                        "magnitud": [{"name": "Potencia"}],
                        "tiempo": [{"name": "Hora"}],
                        "geos": [{"geo_name": "Península"}],
                        "values": [
                            {
                                "value": 5000.0,
                                "datetime": "2025-10-08T12:00:00.000+02:00",
                                "datetime_utc": "2025-10-08T10:00:00Z",
                                "geo_name": "Península",
                            }
                        ],
                    }
                }
            )

        result_str = await get_generation_mix(date="2025-10-08", hour="12")

        result = json.loads(result_str)
        assert "datetime" in result
        assert "sources" in result
        assert result["datetime"] == "2025-10-08T12:00"


@pytest.mark.integration
class TestMCPServerRealAPI:
    """Integration tests using real REE API.

    These tests are marked with @pytest.mark.integration and are skipped by default.
    Run with: pytest -m integration
    """

    @pytest.mark.skip(reason="Requires real API - run manually for verification")
    async def test_get_real_demand_data(self) -> None:
        """Test getting real demand data from API."""
        result_str = await get_indicator_data(
            indicator_id=1293,
            start_date="2025-10-08T00:00",
            end_date="2025-10-08T03:00",
            time_granularity="hour",
        )

        result = json.loads(result_str)
        assert "indicator" in result
        assert "values" in result
        assert result["indicator"]["id"] == 1293
        assert len(result["values"]) > 0

    @pytest.mark.skip(reason="Requires real API - run manually for verification")
    async def test_search_real_indicators(self) -> None:
        """Test searching real indicators."""
        result_str = await search_indicators(keyword="precio", limit=5)

        result = json.loads(result_str)
        assert "indicators" in result
        assert result["count"] > 0
        # All results should contain "precio" in name
        for ind in result["indicators"]:
            assert "precio" in ind["name"].lower()
