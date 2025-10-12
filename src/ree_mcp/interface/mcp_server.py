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
        real_demand_result = await get_indicator_data(1293, start_date, end_date, "hour")  # type: ignore[operator]
        demand_data = json.loads(real_demand_result)

        if "error" in demand_data:
            return real_demand_result  # type: ignore[no-any-return]

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


@mcp.tool()
async def get_international_exchanges(date: str, hour: str = "12") -> str:
    """Get international electricity exchanges at a specific time.

    Returns import/export data by country (Andorra, Morocco, Portugal, France)
    with net balance calculations.

    Args:
        date: Date in YYYY-MM-DD format
        hour: Hour in HH format (00-23, default: 12)

    Returns:
        JSON string with imports, exports, and net balance by country.

    Examples:
        Get exchanges at noon on Oct 8:
        >>> await get_international_exchanges("2025-10-08", "12")

        Get overnight exchanges:
        >>> await get_international_exchanges("2025-10-08", "02")
    """
    try:
        start_datetime = f"{date}T{hour.zfill(2)}:00"
        end_datetime = f"{date}T{hour.zfill(2)}:59"

        # Exchange indicators (exports: 2068-2071, imports: 2073-2076)
        exchanges = {
            "andorra": {"export_id": 2068, "import_id": 2073},
            "morocco": {"export_id": 2069, "import_id": 2074},
            "portugal": {"export_id": 2070, "import_id": 2075},
            "france": {"export_id": 2071, "import_id": 2076},
        }

        result: dict[str, Any] = {
            "datetime": start_datetime,
            "exchanges": {},
            "totals": {"total_exports_mw": 0.0, "total_imports_mw": 0.0, "net_balance_mw": 0.0},
        }

        settings = get_settings()
        async with REEApiClient(settings) as client:
            repository = REEIndicatorRepository(client)
            use_case = GetIndicatorDataUseCase(repository)

            for country, ids in exchanges.items():
                country_data: dict[str, Any] = {}
                try:
                    # Get export data
                    export_request = GetIndicatorDataRequest(
                        indicator_id=ids["export_id"],
                        start_date=start_datetime,
                        end_date=end_datetime,
                        time_granularity="hour",
                    )
                    export_response = await use_case.execute(export_request)
                    export_values = export_response.model_dump().get("values", [])
                    export_mw = export_values[0]["value"] if export_values else 0.0

                    # Get import data
                    import_request = GetIndicatorDataRequest(
                        indicator_id=ids["import_id"],
                        start_date=start_datetime,
                        end_date=end_datetime,
                        time_granularity="hour",
                    )
                    import_response = await use_case.execute(import_request)
                    import_values = import_response.model_dump().get("values", [])
                    import_mw = import_values[0]["value"] if import_values else 0.0

                    # Calculate net balance (positive = net import)
                    net_mw = import_mw - export_mw

                    country_data = {
                        "export_mw": export_mw,
                        "import_mw": import_mw,
                        "net_balance_mw": net_mw,
                        "net_flow": "import"
                        if net_mw > 0
                        else "export"
                        if net_mw < 0
                        else "balanced",
                    }

                    result["totals"]["total_exports_mw"] += export_mw
                    result["totals"]["total_imports_mw"] += import_mw

                except Exception as e:
                    country_data = {"error": str(e)}

                result["exchanges"][country] = country_data

            result["totals"]["net_balance_mw"] = (
                result["totals"]["total_imports_mw"] - result["totals"]["total_exports_mw"]
            )

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Error getting exchanges: {str(e)}"}, indent=2)


@mcp.tool()
async def get_renewable_summary(date: str, hour: str = "12") -> str:
    """Get renewable energy generation summary at a specific time.

    Aggregates wind, solar PV, solar thermal, and hydro generation with
    renewable percentage calculations.

    Args:
        date: Date in YYYY-MM-DD format
        hour: Hour in HH format (00-23, default: 12)

    Returns:
        JSON string with renewable generation breakdown and percentages.

    Examples:
        Get renewable summary at noon:
        >>> await get_renewable_summary("2025-10-08", "12")

        Get overnight renewable summary:
        >>> await get_renewable_summary("2025-10-08", "02")
    """
    try:
        start_datetime = f"{date}T{hour.zfill(2)}:00"
        end_datetime = f"{date}T{hour.zfill(2)}:59"

        # Renewable source indicators
        renewable_sources = {
            "wind_national": 2038,
            "solar_pv_national": 2044,
            "solar_thermal_national": 2045,
            "hydro_national": 2042,
        }

        # Total demand indicator
        DEMAND_ID = 2037  # Real National Demand

        result: dict[str, Any] = {
            "datetime": start_datetime,
            "renewable_sources": {},
            "summary": {},
        }

        settings = get_settings()
        async with REEApiClient(settings) as client:
            repository = REEIndicatorRepository(client)
            use_case = GetIndicatorDataUseCase(repository)

            total_renewable_mw = 0.0
            variable_renewable_mw = 0.0

            # Get renewable generation data
            for source_name, indicator_id in renewable_sources.items():
                try:
                    request = GetIndicatorDataRequest(
                        indicator_id=indicator_id,
                        start_date=start_datetime,
                        end_date=end_datetime,
                        time_granularity="hour",
                    )
                    response = await use_case.execute(request)
                    values = response.model_dump().get("values", [])

                    if values:
                        value_mw = values[0]["value"]
                        is_variable = source_name in [
                            "wind_national",
                            "solar_pv_national",
                            "solar_thermal_national",
                        ]

                        result["renewable_sources"][source_name] = {
                            "value_mw": value_mw,
                            "type": "variable" if is_variable else "synchronous",
                        }

                        total_renewable_mw += value_mw
                        if is_variable:
                            variable_renewable_mw += value_mw

                except Exception as e:
                    result["renewable_sources"][source_name] = {"error": str(e)}

            # Get total demand
            try:
                demand_request = GetIndicatorDataRequest(
                    indicator_id=DEMAND_ID,
                    start_date=start_datetime,
                    end_date=end_datetime,
                    time_granularity="hour",
                )
                demand_response = await use_case.execute(demand_request)
                demand_values = demand_response.model_dump().get("values", [])

                if demand_values:
                    total_demand_mw = demand_values[0]["value"]
                    renewable_pct = (
                        (total_renewable_mw / total_demand_mw * 100) if total_demand_mw > 0 else 0
                    )
                    variable_pct = (
                        (variable_renewable_mw / total_demand_mw * 100)
                        if total_demand_mw > 0
                        else 0
                    )

                    result["summary"] = {
                        "total_renewable_mw": total_renewable_mw,
                        "variable_renewable_mw": variable_renewable_mw,
                        "synchronous_renewable_mw": total_renewable_mw - variable_renewable_mw,
                        "total_demand_mw": total_demand_mw,
                        "renewable_percentage": round(renewable_pct, 2),
                        "variable_renewable_percentage": round(variable_pct, 2),
                    }
            except Exception as e:
                result["summary"] = {"error": f"Could not calculate percentages: {str(e)}"}

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Error getting renewable summary: {str(e)}"}, indent=2)


@mcp.tool()
async def get_carbon_intensity(
    start_date: str, end_date: str, time_granularity: str = "hour"
) -> str:
    """Get carbon intensity over time (gCO2/kWh).

    Calculates CO2 emissions per unit of electricity generated. Lower values
    indicate cleaner energy mix.

    Args:
        start_date: Start datetime in ISO format (YYYY-MM-DDTHH:MM)
        end_date: End datetime in ISO format (YYYY-MM-DDTHH:MM)
        time_granularity: Time aggregation (raw, hour, day, fifteen_minutes)

    Returns:
        JSON string with carbon intensity time series and statistics.

    Examples:
        Get hourly carbon intensity for a day:
        >>> await get_carbon_intensity("2025-10-08T00:00", "2025-10-08T23:59", "hour")

        Get daily carbon intensity for a week:
        >>> await get_carbon_intensity("2025-10-01T00:00", "2025-10-07T23:59", "day")
    """
    try:
        CO2_INDICATOR = 10355  # CO₂ Associated with Real-Time Generation
        DEMAND_INDICATOR = 10004  # Real Demand Sum of Generation

        settings = get_settings()
        async with REEApiClient(settings) as client:
            repository = REEIndicatorRepository(client)
            use_case = GetIndicatorDataUseCase(repository)

            # Get CO2 emissions
            co2_request = GetIndicatorDataRequest(
                indicator_id=CO2_INDICATOR,
                start_date=start_date,
                end_date=end_date,
                time_granularity=time_granularity,
            )
            co2_response = await use_case.execute(co2_request)
            co2_data = co2_response.model_dump()

            # Get generation/demand
            demand_request = GetIndicatorDataRequest(
                indicator_id=DEMAND_INDICATOR,
                start_date=start_date,
                end_date=end_date,
                time_granularity=time_granularity,
            )
            demand_response = await use_case.execute(demand_request)
            demand_data = demand_response.model_dump()

            # Calculate carbon intensity (gCO2/kWh)
            co2_values = co2_data.get("values", [])
            demand_values = demand_data.get("values", [])

            intensity_values = []
            for co2_val, demand_val in zip(co2_values, demand_values, strict=False):
                if demand_val["value"] > 0:
                    # Convert tCO2 to gCO2, MW to MWh (for hourly data they're equivalent)
                    intensity_g_per_kwh = (co2_val["value"] * 1_000_000) / (
                        demand_val["value"] * 1_000
                    )
                    intensity_values.append(
                        {
                            "datetime": co2_val["datetime"],
                            "carbon_intensity_g_per_kwh": round(intensity_g_per_kwh, 2),
                            "co2_tonnes": co2_val["value"],
                            "generation_mw": demand_val["value"],
                        }
                    )

            # Calculate statistics
            if intensity_values:
                intensities = [v["carbon_intensity_g_per_kwh"] for v in intensity_values]
                stats = {
                    "min_g_per_kwh": min(intensities),
                    "max_g_per_kwh": max(intensities),
                    "avg_g_per_kwh": round(sum(intensities) / len(intensities), 2),
                    "count": len(intensities),
                }
            else:
                stats = {}

            result = {
                "period": {"start": start_date, "end": end_date, "granularity": time_granularity},
                "values": intensity_values,
                "statistics": stats,
                "interpretation": {
                    "excellent": "< 50 g/kWh",
                    "good": "50-150 g/kWh",
                    "moderate": "150-300 g/kWh",
                    "poor": "> 300 g/kWh",
                },
            }

            return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Error calculating carbon intensity: {str(e)}"}, indent=2)


@mcp.tool()
async def compare_forecast_actual(date: str) -> str:
    """Compare forecasted vs actual electricity demand.

    Calculates forecast accuracy metrics (error, MAE, RMSE) for demand predictions.

    Args:
        date: Date in YYYY-MM-DD format

    Returns:
        JSON string with forecast comparison and accuracy metrics.

    Examples:
        Compare forecast accuracy for Oct 8:
        >>> await compare_forecast_actual("2025-10-08")
    """
    try:
        start_date = f"{date}T00:00"
        end_date = f"{date}T23:59"

        FORECAST_INDICATOR = 1292  # Demand Forecast
        ACTUAL_INDICATOR = 1293  # Real Demand

        settings = get_settings()
        async with REEApiClient(settings) as client:
            repository = REEIndicatorRepository(client)
            use_case = GetIndicatorDataUseCase(repository)

            # Get forecast data
            forecast_request = GetIndicatorDataRequest(
                indicator_id=FORECAST_INDICATOR,
                start_date=start_date,
                end_date=end_date,
                time_granularity="hour",
            )
            forecast_response = await use_case.execute(forecast_request)
            forecast_data = forecast_response.model_dump()

            # Get actual data
            actual_request = GetIndicatorDataRequest(
                indicator_id=ACTUAL_INDICATOR,
                start_date=start_date,
                end_date=end_date,
                time_granularity="hour",
            )
            actual_response = await use_case.execute(actual_request)
            actual_data = actual_response.model_dump()

            # Compare values
            forecast_values = forecast_data.get("values", [])
            actual_values = actual_data.get("values", [])

            comparisons = []
            errors = []
            absolute_errors = []
            squared_errors = []

            for forecast, actual in zip(forecast_values, actual_values, strict=False):
                forecast_mw = forecast["value"]
                actual_mw = actual["value"]
                error_mw = forecast_mw - actual_mw
                error_pct = (error_mw / actual_mw * 100) if actual_mw > 0 else 0

                comparisons.append(
                    {
                        "datetime": forecast["datetime"],
                        "forecast_mw": forecast_mw,
                        "actual_mw": actual_mw,
                        "error_mw": round(error_mw, 2),
                        "error_percentage": round(error_pct, 2),
                    }
                )

                errors.append(error_mw)
                absolute_errors.append(abs(error_mw))
                squared_errors.append(error_mw**2)

            # Calculate accuracy metrics
            if errors:
                mae = sum(absolute_errors) / len(absolute_errors)
                rmse = (sum(squared_errors) / len(squared_errors)) ** 0.5
                mean_error = sum(errors) / len(errors)
                mape = sum(abs(e / a["value"]) * 100 for e, a in zip(errors, actual_values, strict=False)) / len(
                    errors
                )

                accuracy_metrics = {
                    "mean_absolute_error_mw": round(mae, 2),
                    "root_mean_squared_error_mw": round(rmse, 2),
                    "mean_error_mw": round(mean_error, 2),
                    "mean_absolute_percentage_error": round(mape, 2),
                    "bias": "overforecast"
                    if mean_error > 0
                    else "underforecast"
                    if mean_error < 0
                    else "unbiased",
                }
            else:
                accuracy_metrics = {}

            result = {
                "date": date,
                "comparisons": comparisons,
                "accuracy_metrics": accuracy_metrics,
            }

            return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Error comparing forecast: {str(e)}"}, indent=2)


@mcp.tool()
async def get_grid_stability(date: str, hour: str = "12") -> str:
    """Get grid stability metrics at a specific time.

    Analyzes synchronous generation (provides inertia) vs variable renewables
    (no inertia) to assess grid stability risk.

    Args:
        date: Date in YYYY-MM-DD format
        hour: Hour in HH format (00-23, default: 12)

    Returns:
        JSON string with grid stability analysis.

    Examples:
        Get grid stability at noon:
        >>> await get_grid_stability("2025-10-08", "12")

        Check overnight stability:
        >>> await get_grid_stability("2025-10-08", "02")
    """
    try:
        start_datetime = f"{date}T{hour.zfill(2)}:00"
        end_datetime = f"{date}T{hour.zfill(2)}:59"

        # Synchronous sources (provide inertia)
        synchronous = {
            "nuclear": 549,
            "combined_cycle": 2041,
            "hydro": 2042,
            "coal": 547,
            "fuel_gas": 548,
        }

        # Variable renewables (no inertia)
        variable_renewables = {
            "wind": 2038,
            "solar_pv": 2044,
            "solar_thermal": 2045,
        }

        DEMAND_ID = 2037  # Real National Demand

        result: dict[str, Any] = {
            "datetime": start_datetime,
            "synchronous_generation": {},
            "variable_renewables": {},
            "analysis": {},
        }

        settings = get_settings()
        async with REEApiClient(settings) as client:
            repository = REEIndicatorRepository(client)
            use_case = GetIndicatorDataUseCase(repository)

            total_synchronous_mw = 0.0
            total_variable_mw = 0.0

            # Get synchronous generation
            for source_name, indicator_id in synchronous.items():
                try:
                    request = GetIndicatorDataRequest(
                        indicator_id=indicator_id,
                        start_date=start_datetime,
                        end_date=end_datetime,
                        time_granularity="hour",
                    )
                    response = await use_case.execute(request)
                    values = response.model_dump().get("values", [])

                    if values:
                        value_mw = values[0]["value"]
                        result["synchronous_generation"][source_name] = {"value_mw": value_mw}
                        total_synchronous_mw += value_mw
                except Exception as e:
                    result["synchronous_generation"][source_name] = {"error": str(e)}

            # Get variable renewables
            for source_name, indicator_id in variable_renewables.items():
                try:
                    request = GetIndicatorDataRequest(
                        indicator_id=indicator_id,
                        start_date=start_datetime,
                        end_date=end_datetime,
                        time_granularity="hour",
                    )
                    response = await use_case.execute(request)
                    values = response.model_dump().get("values", [])

                    if values:
                        value_mw = values[0]["value"]
                        result["variable_renewables"][source_name] = {"value_mw": value_mw}
                        total_variable_mw += value_mw
                except Exception as e:
                    result["variable_renewables"][source_name] = {"error": str(e)}

            # Get total demand
            try:
                demand_request = GetIndicatorDataRequest(
                    indicator_id=DEMAND_ID,
                    start_date=start_datetime,
                    end_date=end_datetime,
                    time_granularity="hour",
                )
                demand_response = await use_case.execute(demand_request)
                demand_values = demand_response.model_dump().get("values", [])

                if demand_values:
                    total_demand_mw = demand_values[0]["value"]
                    synchronous_pct = (
                        (total_synchronous_mw / total_demand_mw * 100) if total_demand_mw > 0 else 0
                    )
                    variable_pct = (
                        (total_variable_mw / total_demand_mw * 100) if total_demand_mw > 0 else 0
                    )
                    inertia_ratio = (
                        (total_synchronous_mw / total_variable_mw)
                        if total_variable_mw > 0
                        else float("inf")
                    )

                    # Stability assessment
                    if synchronous_pct >= 70:
                        stability_level = "excellent"
                    elif synchronous_pct >= 50:
                        stability_level = "good"
                    elif synchronous_pct >= 30:
                        stability_level = "moderate"
                    else:
                        stability_level = "concerning"

                    result["analysis"] = {
                        "total_synchronous_mw": round(total_synchronous_mw, 2),
                        "total_variable_renewable_mw": round(total_variable_mw, 2),
                        "total_demand_mw": round(total_demand_mw, 2),
                        "synchronous_percentage": round(synchronous_pct, 2),
                        "variable_renewable_percentage": round(variable_pct, 2),
                        "inertia_ratio": round(inertia_ratio, 2)
                        if inertia_ratio != float("inf")
                        else "infinite",
                        "stability_level": stability_level,
                        "interpretation": {
                            "excellent": ">=70% synchronous (high inertia)",
                            "good": "50-70% synchronous (adequate inertia)",
                            "moderate": "30-50% synchronous (requires monitoring)",
                            "concerning": "<30% synchronous (stability risk)",
                        },
                    }
            except Exception as e:
                result["analysis"] = {"error": f"Could not calculate analysis: {str(e)}"}

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Error getting grid stability: {str(e)}"}, indent=2)


@mcp.tool()
async def get_generation_mix_timeline(date: str, time_granularity: str = "hour") -> str:
    """Get generation mix over time for a full day or period.

    Returns generation breakdown by source across multiple time points,
    useful for visualizing energy transition patterns.

    Args:
        date: Date in YYYY-MM-DD format
        time_granularity: Time aggregation (hour or day, default: hour)

    Returns:
        JSON string with generation mix timeline.

    Examples:
        Get hourly generation mix for a day:
        >>> await get_generation_mix_timeline("2025-10-08", "hour")

        Get daily generation mix for a month:
        >>> await get_generation_mix_timeline("2025-10-01", "day")
    """
    try:
        # Determine date range based on granularity
        if time_granularity == "hour":
            start_date = f"{date}T00:00"
            end_date = f"{date}T23:59"
        else:  # day
            start_date = f"{date}T00:00"
            end_date = f"{date}T23:59"

        # Key generation indicators
        sources = {
            "nuclear": 549,
            "wind_national": 2038,
            "solar_pv_national": 2044,
            "solar_thermal_national": 2045,
            "hydro_national": 2042,
            "combined_cycle_national": 2041,
        }

        result: dict[str, Any] = {
            "period": {"start": start_date, "end": end_date, "granularity": time_granularity},
            "timeline": [],
        }

        settings = get_settings()
        async with REEApiClient(settings) as client:
            repository = REEIndicatorRepository(client)
            use_case = GetIndicatorDataUseCase(repository)

            # Fetch all source data
            source_data = {}
            for source_name, indicator_id in sources.items():
                try:
                    request = GetIndicatorDataRequest(
                        indicator_id=indicator_id,
                        start_date=start_date,
                        end_date=end_date,
                        time_granularity=time_granularity,
                    )
                    response = await use_case.execute(request)
                    response_dict = response.model_dump()
                    source_data[source_name] = response_dict.get("values", [])
                except Exception:
                    source_data[source_name] = []

            # Build timeline by combining data points
            if source_data:
                # Use first source to get timestamps
                first_source = next(iter(source_data.values()))
                for i, value_point in enumerate(first_source):
                    timestamp = value_point["datetime"]

                    generation_point: dict[str, Any] = {
                        "datetime": timestamp,
                        "sources": {},
                        "total_mw": 0.0,
                    }

                    for source_name, values in source_data.items():
                        if i < len(values):
                            mw_value = values[i]["value"]
                            generation_point["sources"][source_name] = mw_value
                            generation_point["total_mw"] += mw_value
                        else:
                            generation_point["sources"][source_name] = 0.0

                    generation_point["total_mw"] = round(generation_point["total_mw"], 2)
                    result["timeline"].append(generation_point)

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Error getting generation timeline: {str(e)}"}, indent=2)


@mcp.tool()
async def get_price_analysis(start_date: str, end_date: str) -> str:
    """Get electricity price analysis over time.

    Analyzes SPOT market prices with statistics and multi-country comparison.

    Args:
        start_date: Start datetime in ISO format (YYYY-MM-DDTHH:MM)
        end_date: End datetime in ISO format (YYYY-MM-DDTHH:MM)

    Returns:
        JSON string with price data and analysis.

    Examples:
        Get hourly prices for a day:
        >>> await get_price_analysis("2025-10-08T00:00", "2025-10-08T23:59")

        Get prices for a week:
        >>> await get_price_analysis("2025-10-01T00:00", "2025-10-07T23:59")
    """
    try:
        SPOT_PRICE_INDICATOR = 600  # Daily SPOT Market Price

        settings = get_settings()
        async with REEApiClient(settings) as client:
            repository = REEIndicatorRepository(client)
            use_case = GetIndicatorDataUseCase(repository)

            # Get SPOT price data
            request = GetIndicatorDataRequest(
                indicator_id=SPOT_PRICE_INDICATOR,
                start_date=start_date,
                end_date=end_date,
                time_granularity="hour",
            )
            response = await use_case.execute(request)
            price_data = response.model_dump()

            values = price_data.get("values", [])

            # Group by country
            countries: dict[str, list[dict[str, Any]]] = {}
            for value_point in values:
                geo = value_point["geo_scope"]
                if geo not in countries:
                    countries[geo] = []
                countries[geo].append(
                    {
                        "datetime": value_point["datetime"],
                        "price_eur_per_mwh": value_point["value"],
                    }
                )

            # Calculate statistics per country
            country_stats = {}
            for country, prices in countries.items():
                price_values = [p["price_eur_per_mwh"] for p in prices]
                if price_values:
                    country_stats[country] = {
                        "min_eur_per_mwh": round(min(price_values), 2),
                        "max_eur_per_mwh": round(max(price_values), 2),
                        "avg_eur_per_mwh": round(sum(price_values) / len(price_values), 2),
                        "count": len(price_values),
                    }

            result = {
                "period": {"start": start_date, "end": end_date},
                "countries": countries,
                "statistics_by_country": country_stats,
                "unit": price_data["indicator"]["unit"],
            }

            return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Error analyzing prices: {str(e)}"}, indent=2)


@mcp.tool()
async def get_storage_operations(date: str) -> str:
    """Get pumped storage operations for a day.

    Shows pumping consumption (storing energy) and turbining (releasing energy)
    to identify arbitrage opportunities and storage efficiency.

    Args:
        date: Date in YYYY-MM-DD format

    Returns:
        JSON string with storage operations and efficiency metrics.

    Examples:
        Get storage operations for Oct 8:
        >>> await get_storage_operations("2025-10-08")
    """
    try:
        start_date = f"{date}T00:00"
        end_date = f"{date}T23:59"

        PUMPING_CONSUMPTION = 2078  # Energy consumed for pumping
        PUMPED_TURBINING = 2079  # Energy released from storage

        settings = get_settings()
        async with REEApiClient(settings) as client:
            repository = REEIndicatorRepository(client)
            use_case = GetIndicatorDataUseCase(repository)

            # Get pumping consumption
            pumping_request = GetIndicatorDataRequest(
                indicator_id=PUMPING_CONSUMPTION,
                start_date=start_date,
                end_date=end_date,
                time_granularity="hour",
            )
            pumping_response = await use_case.execute(pumping_request)
            pumping_data = pumping_response.model_dump()

            # Get turbining
            turbining_request = GetIndicatorDataRequest(
                indicator_id=PUMPED_TURBINING,
                start_date=start_date,
                end_date=end_date,
                time_granularity="hour",
            )
            turbining_response = await use_case.execute(turbining_request)
            turbining_data = turbining_response.model_dump()

            # Combine data
            pumping_values = pumping_data.get("values", [])
            turbining_values = turbining_data.get("values", [])

            operations = []
            total_pumping_mwh = 0.0
            total_turbining_mwh = 0.0

            for pumping, turbining in zip(pumping_values, turbining_values, strict=False):
                pump_mw = pumping["value"]
                turb_mw = turbining["value"]
                net_mw = turb_mw - pump_mw

                operations.append(
                    {
                        "datetime": pumping["datetime"],
                        "pumping_mw": pump_mw,
                        "turbining_mw": turb_mw,
                        "net_storage_mw": round(net_mw, 2),
                        "operation": "storing"
                        if pump_mw > turb_mw
                        else "releasing"
                        if turb_mw > pump_mw
                        else "idle",
                    }
                )

                total_pumping_mwh += pump_mw
                total_turbining_mwh += turb_mw

            # Calculate efficiency (typical pumped storage is 70-85%)
            efficiency_pct = (
                (total_turbining_mwh / total_pumping_mwh * 100) if total_pumping_mwh > 0 else 0
            )

            result = {
                "date": date,
                "operations": operations,
                "summary": {
                    "total_energy_stored_mwh": round(total_pumping_mwh, 2),
                    "total_energy_released_mwh": round(total_turbining_mwh, 2),
                    "net_energy_balance_mwh": round(total_turbining_mwh - total_pumping_mwh, 2),
                    "efficiency_percentage": round(efficiency_pct, 2),
                    "efficiency_assessment": "normal"
                    if 70 <= efficiency_pct <= 85
                    else "check_data",
                },
            }

            return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Error getting storage operations: {str(e)}"}, indent=2)


@mcp.tool()
async def get_peak_analysis(start_date: str, end_date: str) -> str:
    """Get peak demand analysis over a period.

    Analyzes daily maximum and minimum demand to identify patterns and
    calculate load factors.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format

    Returns:
        JSON string with peak demand analysis.

    Examples:
        Get peak analysis for a week:
        >>> await get_peak_analysis("2025-10-01", "2025-10-07")

        Get peak analysis for a month:
        >>> await get_peak_analysis("2025-10-01", "2025-10-31")
    """
    try:
        MAX_DEMAND_INDICATOR = 624  # Maximum Daily Real Demand
        MIN_DEMAND_INDICATOR = 625  # Minimum Daily Real Demand

        settings = get_settings()
        async with REEApiClient(settings) as client:
            repository = REEIndicatorRepository(client)
            use_case = GetIndicatorDataUseCase(repository)

            # Get max demand
            max_request = GetIndicatorDataRequest(
                indicator_id=MAX_DEMAND_INDICATOR,
                start_date=start_date,
                end_date=end_date,
                time_granularity="day",
            )
            max_response = await use_case.execute(max_request)
            max_data = max_response.model_dump()

            # Get min demand
            min_request = GetIndicatorDataRequest(
                indicator_id=MIN_DEMAND_INDICATOR,
                start_date=start_date,
                end_date=end_date,
                time_granularity="day",
            )
            min_response = await use_case.execute(min_request)
            min_data = min_response.model_dump()

            # Combine data
            max_values = max_data.get("values", [])
            min_values = min_data.get("values", [])

            daily_analysis = []
            peak_demands = []
            load_factors = []

            for max_val, min_val in zip(max_values, min_values, strict=False):
                max_mw = max_val["value"]
                min_mw = min_val["value"]
                avg_mw = (max_mw + min_mw) / 2
                peak_to_valley = max_mw - min_mw
                load_factor = (avg_mw / max_mw * 100) if max_mw > 0 else 0

                daily_analysis.append(
                    {
                        "date": max_val["datetime"][:10],
                        "peak_demand_mw": max_mw,
                        "minimum_demand_mw": min_mw,
                        "average_demand_mw": round(avg_mw, 2),
                        "peak_to_valley_mw": round(peak_to_valley, 2),
                        "load_factor_percentage": round(load_factor, 2),
                    }
                )

                peak_demands.append(max_mw)
                load_factors.append(load_factor)

            # Calculate period statistics
            if peak_demands:
                period_stats = {
                    "highest_peak_mw": max(peak_demands),
                    "lowest_peak_mw": min(peak_demands),
                    "average_peak_mw": round(sum(peak_demands) / len(peak_demands), 2),
                    "average_load_factor_percentage": round(
                        sum(load_factors) / len(load_factors), 2
                    ),
                    "interpretation": {
                        "high_load_factor": "> 70% (efficient, stable demand)",
                        "medium_load_factor": "50-70% (moderate variability)",
                        "low_load_factor": "< 50% (high variability, inefficient)",
                    },
                }
            else:
                period_stats = {}

            result = {
                "period": {"start": start_date, "end": end_date},
                "daily_analysis": daily_analysis,
                "period_statistics": period_stats,
            }

            return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Error analyzing peaks: {str(e)}"}, indent=2)


# MCP Resources
@mcp.resource("ree://indicators")
async def list_all_indicators() -> str:
    """Resource providing the complete list of all REE indicators.

    Returns:
        JSON string with all indicator metadata.
    """
    result: str = await list_indicators()  # type: ignore[operator]
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
