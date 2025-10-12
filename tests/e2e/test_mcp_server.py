"""End-to-end tests for MCP server.

These tests verify the full integration of all layers.
Note: Some tests are marked as integration tests that require the real API.
"""

import json

import pytest
from pytest_httpx import HTTPXMock

from src.ree_mcp.interface.mcp_server import (
    compare_forecast_actual,
    get_carbon_intensity,
    get_demand_summary,
    get_generation_mix,
    get_generation_mix_timeline,
    get_grid_stability,
    get_indicator_data,
    get_international_exchanges,
    get_peak_analysis,
    get_price_analysis,
    get_renewable_summary,
    get_storage_operations,
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

    async def test_get_international_exchanges_tool(self, httpx_mock: HTTPXMock) -> None:
        """Test get_international_exchanges convenience tool."""
        # Mock responses for exports and imports (8 total: 4 countries × 2 directions)
        for _ in range(8):
            httpx_mock.add_response(
                json={
                    "indicator": {
                        "id": 2068,
                        "name": "Test",
                        "short_name": "Test",
                        "magnitud": [{"name": "Potencia"}],
                        "tiempo": [{"name": "Hora"}],
                        "geos": [{"geo_name": "Península"}],
                        "values": [
                            {
                                "value": 100.0,
                                "datetime": "2025-10-08T12:00:00.000+02:00",
                                "datetime_utc": "2025-10-08T10:00:00Z",
                                "geo_name": "Península",
                            }
                        ],
                    }
                }
            )

        result_str = await get_international_exchanges(date="2025-10-08", hour="12")

        result = json.loads(result_str)
        assert "datetime" in result
        assert "exchanges" in result
        assert "totals" in result
        assert "andorra" in result["exchanges"]
        assert "total_exports_mw" in result["totals"]

    async def test_get_renewable_summary_tool(self, httpx_mock: HTTPXMock) -> None:
        """Test get_renewable_summary convenience tool."""
        # Mock responses for renewable sources + demand (5 total)
        for _ in range(5):
            httpx_mock.add_response(
                json={
                    "indicator": {
                        "id": 2038,
                        "name": "Test",
                        "short_name": "Test",
                        "magnitud": [{"name": "Potencia"}],
                        "tiempo": [{"name": "Hora"}],
                        "geos": [{"geo_name": "Nacional"}],
                        "values": [
                            {
                                "value": 10000.0,
                                "datetime": "2025-10-08T12:00:00.000+02:00",
                                "datetime_utc": "2025-10-08T10:00:00Z",
                                "geo_name": "Nacional",
                            }
                        ],
                    }
                }
            )

        result_str = await get_renewable_summary(date="2025-10-08", hour="12")

        result = json.loads(result_str)
        assert "datetime" in result
        assert "renewable_sources" in result
        assert "summary" in result
        assert "total_renewable_mw" in result["summary"]

    async def test_get_carbon_intensity_tool(self, httpx_mock: HTTPXMock) -> None:
        """Test get_carbon_intensity tool."""
        # Mock CO2 response
        httpx_mock.add_response(
            json={
                "indicator": {
                    "id": 10355,
                    "name": "CO2",
                    "short_name": "CO2",
                    "magnitud": [{"name": "Emisiones"}],
                    "tiempo": [{"name": "Hora"}],
                    "geos": [{"geo_name": "Península"}],
                    "values": [
                        {
                            "value": 5000.0,  # tonnes
                            "datetime": "2025-10-08T12:00:00.000+02:00",
                            "datetime_utc": "2025-10-08T10:00:00Z",
                            "geo_name": "Península",
                        }
                    ],
                }
            }
        )
        # Mock demand response
        httpx_mock.add_response(
            json={
                "indicator": {
                    "id": 10004,
                    "name": "Demanda",
                    "short_name": "Demanda",
                    "magnitud": [{"name": "Potencia"}],
                    "tiempo": [{"name": "Hora"}],
                    "geos": [{"geo_name": "Península"}],
                    "values": [
                        {
                            "value": 30000.0,  # MW
                            "datetime": "2025-10-08T12:00:00.000+02:00",
                            "datetime_utc": "2025-10-08T10:00:00Z",
                            "geo_name": "Península",
                        }
                    ],
                }
            }
        )

        result_str = await get_carbon_intensity(
            start_date="2025-10-08T12:00", end_date="2025-10-08T13:00", time_granularity="hour"
        )

        result = json.loads(result_str)
        assert "period" in result
        assert "values" in result
        assert "statistics" in result
        assert len(result["values"]) > 0

    async def test_compare_forecast_actual_tool(self, httpx_mock: HTTPXMock) -> None:
        """Test compare_forecast_actual tool."""
        # Mock forecast response
        httpx_mock.add_response(
            json={
                "indicator": {
                    "id": 1292,
                    "name": "Forecast",
                    "short_name": "Forecast",
                    "magnitud": [{"name": "Potencia"}],
                    "tiempo": [{"name": "Hora"}],
                    "geos": [{"geo_name": "Península"}],
                    "values": [
                        {
                            "value": 31000.0,
                            "datetime": "2025-10-08T12:00:00.000+02:00",
                            "datetime_utc": "2025-10-08T10:00:00Z",
                            "geo_name": "Península",
                        }
                    ],
                }
            }
        )
        # Mock actual response
        httpx_mock.add_response(
            json={
                "indicator": {
                    "id": 1293,
                    "name": "Actual",
                    "short_name": "Actual",
                    "magnitud": [{"name": "Potencia"}],
                    "tiempo": [{"name": "Hora"}],
                    "geos": [{"geo_name": "Península"}],
                    "values": [
                        {
                            "value": 30000.0,
                            "datetime": "2025-10-08T12:00:00.000+02:00",
                            "datetime_utc": "2025-10-08T10:00:00Z",
                            "geo_name": "Península",
                        }
                    ],
                }
            }
        )

        result_str = await compare_forecast_actual(date="2025-10-08")

        result = json.loads(result_str)
        assert "date" in result
        assert "comparisons" in result
        assert "accuracy_metrics" in result
        assert "mean_absolute_error_mw" in result["accuracy_metrics"]

    async def test_get_grid_stability_tool(self, httpx_mock: HTTPXMock) -> None:
        """Test get_grid_stability tool."""
        # Mock responses for synchronous sources (5) + variable renewables (3) + demand (1) = 9
        for _ in range(9):
            httpx_mock.add_response(
                json={
                    "indicator": {
                        "id": 549,
                        "name": "Test",
                        "short_name": "Test",
                        "magnitud": [{"name": "Potencia"}],
                        "tiempo": [{"name": "Hora"}],
                        "geos": [{"geo_name": "Nacional"}],
                        "values": [
                            {
                                "value": 5000.0,
                                "datetime": "2025-10-08T12:00:00.000+02:00",
                                "datetime_utc": "2025-10-08T10:00:00Z",
                                "geo_name": "Nacional",
                            }
                        ],
                    }
                }
            )

        result_str = await get_grid_stability(date="2025-10-08", hour="12")

        result = json.loads(result_str)
        assert "datetime" in result
        assert "synchronous_generation" in result
        assert "variable_renewables" in result
        assert "analysis" in result

    async def test_get_generation_mix_timeline_tool(self, httpx_mock: HTTPXMock) -> None:
        """Test get_generation_mix_timeline tool."""
        # Mock responses for 6 generation sources
        for _ in range(6):
            httpx_mock.add_response(
                json={
                    "indicator": {
                        "id": 549,
                        "name": "Test",
                        "short_name": "Test",
                        "magnitud": [{"name": "Potencia"}],
                        "tiempo": [{"name": "Hora"}],
                        "geos": [{"geo_name": "Nacional"}],
                        "values": [
                            {
                                "value": 5000.0,
                                "datetime": "2025-10-08T00:00:00.000+02:00",
                                "datetime_utc": "2025-10-07T22:00:00Z",
                                "geo_name": "Nacional",
                            },
                            {
                                "value": 5100.0,
                                "datetime": "2025-10-08T01:00:00.000+02:00",
                                "datetime_utc": "2025-10-07T23:00:00Z",
                                "geo_name": "Nacional",
                            },
                        ],
                    }
                }
            )

        result_str = await get_generation_mix_timeline(date="2025-10-08", time_granularity="hour")

        result = json.loads(result_str)
        assert "period" in result
        assert "timeline" in result
        assert len(result["timeline"]) > 0

    async def test_get_price_analysis_tool(self, httpx_mock: HTTPXMock) -> None:
        """Test get_price_analysis tool."""
        httpx_mock.add_response(
            json={
                "indicator": {
                    "id": 600,
                    "name": "SPOT Price",
                    "short_name": "SPOT",
                    "magnitud": [{"name": "Precio"}],
                    "tiempo": [{"name": "Hora"}],
                    "geos": [{"geo_name": "España"}],
                    "values": [
                        {
                            "value": 112.50,
                            "datetime": "2025-10-08T12:00:00.000+02:00",
                            "datetime_utc": "2025-10-08T10:00:00Z",
                            "geo_name": "España",
                        },
                        {
                            "value": 115.00,
                            "datetime": "2025-10-08T13:00:00.000+02:00",
                            "datetime_utc": "2025-10-08T11:00:00Z",
                            "geo_name": "España",
                        },
                    ],
                }
            }
        )

        result_str = await get_price_analysis(
            start_date="2025-10-08T12:00", end_date="2025-10-08T13:00"
        )

        result = json.loads(result_str)
        assert "period" in result
        assert "countries" in result
        assert "statistics_by_country" in result

    async def test_get_storage_operations_tool(self, httpx_mock: HTTPXMock) -> None:
        """Test get_storage_operations tool."""
        # Mock pumping consumption
        httpx_mock.add_response(
            json={
                "indicator": {
                    "id": 2078,
                    "name": "Pumping",
                    "short_name": "Pumping",
                    "magnitud": [{"name": "Potencia"}],
                    "tiempo": [{"name": "Hora"}],
                    "geos": [{"geo_name": "Nacional"}],
                    "values": [
                        {
                            "value": 1000.0,
                            "datetime": "2025-10-08T12:00:00.000+02:00",
                            "datetime_utc": "2025-10-08T10:00:00Z",
                            "geo_name": "Nacional",
                        }
                    ],
                }
            }
        )
        # Mock turbining
        httpx_mock.add_response(
            json={
                "indicator": {
                    "id": 2079,
                    "name": "Turbining",
                    "short_name": "Turbining",
                    "magnitud": [{"name": "Potencia"}],
                    "tiempo": [{"name": "Hora"}],
                    "geos": [{"geo_name": "Nacional"}],
                    "values": [
                        {
                            "value": 800.0,
                            "datetime": "2025-10-08T12:00:00.000+02:00",
                            "datetime_utc": "2025-10-08T10:00:00Z",
                            "geo_name": "Nacional",
                        }
                    ],
                }
            }
        )

        result_str = await get_storage_operations(date="2025-10-08")

        result = json.loads(result_str)
        assert "date" in result
        assert "operations" in result
        assert "summary" in result
        assert "efficiency_percentage" in result["summary"]

    async def test_get_peak_analysis_tool(self, httpx_mock: HTTPXMock) -> None:
        """Test get_peak_analysis tool."""
        # Mock max demand
        httpx_mock.add_response(
            json={
                "indicator": {
                    "id": 624,
                    "name": "Max Demand",
                    "short_name": "Max",
                    "magnitud": [{"name": "Potencia"}],
                    "tiempo": [{"name": "Día"}],
                    "geos": [{"geo_name": "Península"}],
                    "values": [
                        {
                            "value": 35000.0,
                            "datetime": "2025-10-08T00:00:00.000+02:00",
                            "datetime_utc": "2025-10-07T22:00:00Z",
                            "geo_name": "Península",
                        }
                    ],
                }
            }
        )
        # Mock min demand
        httpx_mock.add_response(
            json={
                "indicator": {
                    "id": 625,
                    "name": "Min Demand",
                    "short_name": "Min",
                    "magnitud": [{"name": "Potencia"}],
                    "tiempo": [{"name": "Día"}],
                    "geos": [{"geo_name": "Península"}],
                    "values": [
                        {
                            "value": 25000.0,
                            "datetime": "2025-10-08T00:00:00.000+02:00",
                            "datetime_utc": "2025-10-07T22:00:00Z",
                            "geo_name": "Península",
                        }
                    ],
                }
            }
        )

        result_str = await get_peak_analysis(start_date="2025-10-08", end_date="2025-10-08")

        result = json.loads(result_str)
        assert "period" in result
        assert "daily_analysis" in result
        assert "period_statistics" in result


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
