"""MCP Server implementation using fastmcp."""

import json
from typing import Any

from fastmcp import FastMCP

from ..application.dtos import GetIndicatorDataRequest
from ..application.use_cases import (
    GetIndicatorDataUseCase,
    ListIndicatorsUseCase,
    SearchIndicatorsUseCase,
)
from ..domain.exceptions import DomainException
from ..domain.value_objects import IndicatorId
from ..infrastructure.config import get_settings
from ..infrastructure.http import REEApiClient
from ..infrastructure.repositories import REEIndicatorRepository

# Initialize MCP server
mcp = FastMCP("REE MCP Server", dependencies=["httpx", "pydantic", "pydantic-settings"])


# Dependency injection: Create shared instances
def _get_repository() -> REEIndicatorRepository:
    """Get repository instance with dependencies."""
    settings = get_settings()
    client = REEApiClient(settings)
    return REEIndicatorRepository(client)


# MCP Tools
@mcp.tool()
async def get_indicator_data(
    indicator_id: int,
    start_date: str,
    end_date: str,
    time_granularity: str = "raw",
) -> str:
    """Get time-series data for a specific electricity indicator.

    Retrieves historical data for any REE indicator (demand, generation, prices, etc.)
    for a specified date range. Returns the data with statistical summary.

    Args:
        indicator_id: The indicator ID (e.g., 1293 for real demand, 549 for nuclear)
        start_date: Start datetime in ISO format (YYYY-MM-DDTHH:MM)
        end_date: End datetime in ISO format (YYYY-MM-DDTHH:MM)
        time_granularity: Time aggregation level (raw, hour, day, fifteen_minutes)

    Returns:
        JSON string with indicator metadata, time-series values, and statistics.

    Examples:
        Get hourly real demand for Oct 8, 2025:
        >>> await get_indicator_data(1293, "2025-10-08T00:00", "2025-10-08T23:59", "hour")

        Get 5-minute wind generation data:
        >>> await get_indicator_data(2038, "2025-10-08T00:00", "2025-10-08T03:00", "raw")
    """
    try:
        request = GetIndicatorDataRequest(
            indicator_id=indicator_id,
            start_date=start_date,
            end_date=end_date,
            time_granularity=time_granularity,
        )

        settings = get_settings()
        async with REEApiClient(settings) as client:
            repository = REEIndicatorRepository(client)
            use_case = GetIndicatorDataUseCase(repository)
            response = await use_case.execute(request)

        return response.model_dump_json(indent=2)

    except DomainException as e:
        return json.dumps({"error": str(e), "type": type(e).__name__}, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)


@mcp.tool()
async def list_indicators(limit: int | None = None, offset: int = 0) -> str:
    """List all available electricity indicators from REE.

    Returns metadata for all 1,967+ available indicators including their IDs,
    names, units, frequencies, and geographic scopes.

    Args:
        limit: Maximum number of indicators to return (default: all)
        offset: Number of indicators to skip for pagination (default: 0)

    Returns:
        JSON string with list of indicator metadata.

    Examples:
        Get first 50 indicators:
        >>> await list_indicators(limit=50, offset=0)

        Get all indicators:
        >>> await list_indicators()
    """
    try:
        settings = get_settings()
        async with REEApiClient(settings) as client:
            repository = REEIndicatorRepository(client)
            use_case = ListIndicatorsUseCase(repository)
            indicators = await use_case.execute(limit=limit, offset=offset)

        result = {
            "count": len(indicators),
            "indicators": [ind.model_dump() for ind in indicators],
        }
        return json.dumps(result, indent=2, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"error": f"Error listing indicators: {str(e)}"}, indent=2)


@mcp.tool()
async def search_indicators(keyword: str, limit: int | None = 20) -> str:
    """Search for indicators by keyword in their names.

    Searches through all available indicators and returns those matching
    the keyword in their name or short name.

    Args:
        keyword: Keyword to search for (e.g., "demanda", "precio", "solar")
        limit: Maximum number of results (default: 20)

    Returns:
        JSON string with matching indicator metadata.

    Examples:
        Find all demand-related indicators:
        >>> await search_indicators("demanda", limit=10)

        Find price indicators:
        >>> await search_indicators("precio")

        Find solar generation indicators:
        >>> await search_indicators("solar")
    """
    try:
        settings = get_settings()
        async with REEApiClient(settings) as client:
            repository = REEIndicatorRepository(client)
            use_case = SearchIndicatorsUseCase(repository)
            indicators = await use_case.execute(keyword=keyword, limit=limit)

        result = {
            "keyword": keyword,
            "count": len(indicators),
            "indicators": [ind.model_dump() for ind in indicators],
        }
        return json.dumps(result, indent=2, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"error": f"Error searching indicators: {str(e)}"}, indent=2)


@mcp.tool()
async def get_demand_summary(date: str = "2025-10-08") -> str:
    """Get a summary of electricity demand for a specific date.

    Convenience tool that fetches key demand indicators (real demand, forecast,
    max/min) for a given date.

    Args:
        date: Date in YYYY-MM-DD format (default: 2025-10-08)

    Returns:
        JSON string with demand summary.

    Examples:
        Get today's demand summary:
        >>> await get_demand_summary("2025-10-11")
    """
    try:
        start_date = f"{date}T00:00"
        end_date = f"{date}T23:59"

        # Get real demand (indicator 1293)
        real_demand_result = await get_indicator_data(1293, start_date, end_date, "hour")
        demand_data = json.loads(real_demand_result)

        if "error" in demand_data:
            return real_demand_result

        result = {
            "date": date,
            "real_demand": {
                "statistics": demand_data.get("statistics"),
                "unit": demand_data["indicator"]["unit"],
                "values_count": len(demand_data.get("values", [])),
            },
        }
        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Error getting demand summary: {str(e)}"}, indent=2)


@mcp.tool()
async def get_generation_mix(date: str, hour: str = "12") -> str:
    """Get the electricity generation mix at a specific time.

    Returns the power generation breakdown by source (nuclear, wind, solar, etc.)
    for a specific hour.

    Args:
        date: Date in YYYY-MM-DD format
        hour: Hour in HH format (00-23, default: 12)

    Returns:
        JSON string with generation mix by source.

    Examples:
        Get generation mix at noon on Oct 8:
        >>> await get_generation_mix("2025-10-08", "12")

        Get overnight generation mix:
        >>> await get_generation_mix("2025-10-08", "02")
    """
    try:
        start_datetime = f"{date}T{hour.zfill(2)}:00"
        end_datetime = f"{date}T{hour.zfill(2)}:59"

        # Key generation indicators
        sources = {
            "nuclear": 549,
            "wind_national": 2038,
            "solar_pv_peninsular": 1295,
            "solar_thermal_peninsular": 1294,
            "hydro_national": 2042,
            "combined_cycle_national": 2041,
        }

        generation_mix: dict[str, Any] = {
            "datetime": start_datetime,
            "sources": {},
        }

        settings = get_settings()
        async with REEApiClient(settings) as client:
            repository = REEIndicatorRepository(client)
            use_case = GetIndicatorDataUseCase(repository)

            for source_name, indicator_id in sources.items():
                try:
                    request = GetIndicatorDataRequest(
                        indicator_id=indicator_id,
                        start_date=start_datetime,
                        end_date=end_datetime,
                        time_granularity="hour",
                    )
                    response = await use_case.execute(request)
                    response_dict = response.model_dump()

                    values = response_dict.get("values", [])
                    if values:
                        generation_mix["sources"][source_name] = {
                            "value_mw": values[0]["value"],
                            "unit": response_dict["indicator"]["unit"],
                        }
                except Exception as e:
                    generation_mix["sources"][source_name] = {"error": str(e)}

        return json.dumps(generation_mix, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Error getting generation mix: {str(e)}"}, indent=2)


# MCP Resources
@mcp.resource("ree://indicators")
async def list_all_indicators() -> str:
    """Resource providing the complete list of all REE indicators.

    Returns:
        JSON string with all indicator metadata.
    """
    result: str = await list_indicators()
    return result


@mcp.resource("ree://indicators/{indicator_id}")
async def get_indicator_info(indicator_id: int) -> str:
    """Resource providing metadata for a specific indicator.

    Args:
        indicator_id: The indicator ID

    Returns:
        JSON string with indicator metadata.
    """
    try:
        settings = get_settings()
        async with REEApiClient(settings) as client:
            repository = REEIndicatorRepository(client)
            indicator = await repository.get_indicator_metadata(
                indicator_id=IndicatorId(indicator_id)
            )

        result = {
            "id": int(indicator.id),
            "name": indicator.name,
            "short_name": indicator.short_name,
            "description": indicator.description,
            "unit": indicator.unit.value,
            "frequency": indicator.frequency,
            "geo_scope": indicator.geo_scope.value,
        }
        return json.dumps(result, indent=2, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"error": f"Error getting indicator info: {str(e)}"}, indent=2)


def create_server() -> FastMCP:
    """Create and return the MCP server instance.

    Returns:
        Configured FastMCP server.
    """
    return mcp


# Entry point for running the server
if __name__ == "__main__":
    mcp.run()
