"""MCP Server implementation using fastmcp.

This module provides MCP tools for accessing REE electricity data.
Refactored to follow DRY, KISS, and SOLID principles.
"""

import json
from typing import Any

from fastmcp import FastMCP

from ..application.dtos import GetIndicatorDataRequest
from ..domain.exceptions import DomainException
from ..domain.value_objects import IndicatorId
from ..infrastructure.config import get_settings
from ..infrastructure.http import REEApiClient
from ..infrastructure.repositories import REEIndicatorRepository
from .indicator_config import IndicatorIDs
from .tool_helpers import DateTimeHelper, ResponseFormatter, ToolExecutor
from .tool_services import (
    DataFetcher,
    GenerationMixService,
    GridStabilityService,
    InternationalExchangeService,
    RenewableAnalysisService,
)

# Initialize MCP server
mcp = FastMCP("REE MCP Server", dependencies=["httpx", "pydantic", "pydantic-settings"])


# Core MCP Tools - Low-level API access
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

        async with ToolExecutor() as executor:
            use_case = executor.create_get_indicator_data_use_case()
            response = await use_case.execute(request)

        return response.model_dump_json(indent=2)

    except DomainException as e:
        return ResponseFormatter.domain_exception(e)
    except Exception as e:
        return ResponseFormatter.unexpected_error(e)


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
        async with ToolExecutor() as executor:
            use_case = executor.create_list_indicators_use_case()
            indicators = await use_case.execute(limit=limit, offset=offset)

        result = {
            "count": len(indicators),
            "indicators": [ind.model_dump() for ind in indicators],
        }
        return ResponseFormatter.success(result, ensure_ascii=False)

    except Exception as e:
        return ResponseFormatter.unexpected_error(e, context="Error listing indicators")


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
        async with ToolExecutor() as executor:
            use_case = executor.create_search_indicators_use_case()
            indicators = await use_case.execute(keyword=keyword, limit=limit)

        result = {
            "keyword": keyword,
            "count": len(indicators),
            "indicators": [ind.model_dump() for ind in indicators],
        }
        return ResponseFormatter.success(result, ensure_ascii=False)

    except Exception as e:
        return ResponseFormatter.unexpected_error(e, context="Error searching indicators")


# Convenience Tools - High-level analysis
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
        start_date, end_date = DateTimeHelper.build_day_range(date)

        # Fetch demand data directly
        async with ToolExecutor() as executor:
            use_case = executor.create_get_indicator_data_use_case()
            request = GetIndicatorDataRequest(
                indicator_id=IndicatorIDs.REAL_DEMAND_PENINSULAR.id,
                start_date=start_date,
                end_date=end_date,
                time_granularity="hour",
            )
            response = await use_case.execute(request)
            demand_data = response.model_dump()

        result = {
            "date": date,
            "real_demand": {
                "statistics": demand_data.get("statistics"),
                "unit": demand_data["indicator"]["unit"],
                "values_count": len(demand_data.get("values", [])),
            },
        }
        return ResponseFormatter.success(result)

    except Exception as e:
        return ResponseFormatter.unexpected_error(e, context="Error getting demand summary")


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
        start_datetime, end_datetime = DateTimeHelper.build_datetime_range(date, hour)

        async with ToolExecutor() as executor:
            use_case = executor.create_get_indicator_data_use_case()
            data_fetcher = DataFetcher(use_case)
            service = GenerationMixService(data_fetcher)

            result = await service.get_generation_mix(start_datetime, end_datetime)

        return ResponseFormatter.success(result)

    except Exception as e:
        return ResponseFormatter.unexpected_error(e, context="Error getting generation mix")


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
        start_datetime, end_datetime = DateTimeHelper.build_datetime_range(date, hour)

        async with ToolExecutor() as executor:
            use_case = executor.create_get_indicator_data_use_case()
            data_fetcher = DataFetcher(use_case)
            service = InternationalExchangeService(data_fetcher)

            result = await service.get_international_exchanges(start_datetime, end_datetime)

        return ResponseFormatter.success(result)

    except Exception as e:
        return ResponseFormatter.unexpected_error(e, context="Error getting exchanges")


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
        start_datetime, end_datetime = DateTimeHelper.build_datetime_range(date, hour)

        async with ToolExecutor() as executor:
            use_case = executor.create_get_indicator_data_use_case()
            data_fetcher = DataFetcher(use_case)
            service = RenewableAnalysisService(data_fetcher)

            result = await service.get_renewable_summary(start_datetime, end_datetime)

        return ResponseFormatter.success(result)

    except Exception as e:
        return ResponseFormatter.unexpected_error(e, context="Error getting renewable summary")


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
        async with ToolExecutor() as executor:
            use_case = executor.create_get_indicator_data_use_case()

            # Get CO2 emissions
            co2_request = GetIndicatorDataRequest(
                indicator_id=IndicatorIDs.CO2_EMISSIONS.id,
                start_date=start_date,
                end_date=end_date,
                time_granularity=time_granularity,
            )
            co2_response = await use_case.execute(co2_request)
            co2_data = co2_response.model_dump()

            # Get generation/demand
            demand_request = GetIndicatorDataRequest(
                indicator_id=IndicatorIDs.REAL_DEMAND_SUM_GENERATION.id,
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
        stats = {}
        if intensity_values:
            intensities = [v["carbon_intensity_g_per_kwh"] for v in intensity_values]
            stats = {
                "min_g_per_kwh": min(intensities),
                "max_g_per_kwh": max(intensities),
                "avg_g_per_kwh": round(sum(intensities) / len(intensities), 2),
                "count": len(intensities),
            }

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

        return ResponseFormatter.success(result)

    except Exception as e:
        return ResponseFormatter.unexpected_error(e, context="Error calculating carbon intensity")


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
        start_date, end_date = DateTimeHelper.build_day_range(date)

        async with ToolExecutor() as executor:
            use_case = executor.create_get_indicator_data_use_case()

            # Get forecast data
            forecast_request = GetIndicatorDataRequest(
                indicator_id=IndicatorIDs.DEMAND_FORECAST.id,
                start_date=start_date,
                end_date=end_date,
                time_granularity="hour",
            )
            forecast_response = await use_case.execute(forecast_request)
            forecast_data = forecast_response.model_dump()

            # Get actual data
            actual_request = GetIndicatorDataRequest(
                indicator_id=IndicatorIDs.REAL_DEMAND_PENINSULAR.id,
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
        accuracy_metrics = {}
        if errors:
            mae = sum(absolute_errors) / len(absolute_errors)
            rmse = (sum(squared_errors) / len(squared_errors)) ** 0.5
            mean_error = sum(errors) / len(errors)
            mape = (
                sum(
                    abs(e / a["value"]) * 100 for e, a in zip(errors, actual_values, strict=False)
                )
                / len(errors)
            )

            accuracy_metrics = {
                "mean_absolute_error_mw": round(mae, 2),
                "root_mean_squared_error_mw": round(rmse, 2),
                "mean_error_mw": round(mean_error, 2),
                "mean_absolute_percentage_error": round(mape, 2),
                "bias": (
                    "overforecast"
                    if mean_error > 0
                    else "underforecast" if mean_error < 0 else "unbiased"
                ),
            }

        result = {
            "date": date,
            "comparisons": comparisons,
            "accuracy_metrics": accuracy_metrics,
        }

        return ResponseFormatter.success(result)

    except Exception as e:
        return ResponseFormatter.unexpected_error(e, context="Error comparing forecast")


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
        start_datetime, end_datetime = DateTimeHelper.build_datetime_range(date, hour)

        async with ToolExecutor() as executor:
            use_case = executor.create_get_indicator_data_use_case()
            data_fetcher = DataFetcher(use_case)
            service = GridStabilityService(data_fetcher)

            result = await service.get_grid_stability(start_datetime, end_datetime)

        return ResponseFormatter.success(result)

    except Exception as e:
        return ResponseFormatter.unexpected_error(e, context="Error getting grid stability")


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
        start_date, end_date = DateTimeHelper.build_day_range(date)

        async with ToolExecutor() as executor:
            use_case = executor.create_get_indicator_data_use_case()
            data_fetcher = DataFetcher(use_case)
            service = GenerationMixService(data_fetcher)

            result = await service.get_generation_mix_timeline(
                start_date, end_date, time_granularity
            )

        return ResponseFormatter.success(result)

    except Exception as e:
        return ResponseFormatter.unexpected_error(e, context="Error getting generation timeline")


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
        async with ToolExecutor() as executor:
            use_case = executor.create_get_indicator_data_use_case()

            # Get SPOT price data
            request = GetIndicatorDataRequest(
                indicator_id=IndicatorIDs.SPOT_MARKET_PRICE.id,
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

        return ResponseFormatter.success(result)

    except Exception as e:
        return ResponseFormatter.unexpected_error(e, context="Error analyzing prices")


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
        start_date, end_date = DateTimeHelper.build_day_range(date)

        async with ToolExecutor() as executor:
            use_case = executor.create_get_indicator_data_use_case()

            # Get pumping consumption
            pumping_request = GetIndicatorDataRequest(
                indicator_id=IndicatorIDs.PUMPING_CONSUMPTION.id,
                start_date=start_date,
                end_date=end_date,
                time_granularity="hour",
            )
            pumping_response = await use_case.execute(pumping_request)
            pumping_data = pumping_response.model_dump()

            # Get turbining
            turbining_request = GetIndicatorDataRequest(
                indicator_id=IndicatorIDs.PUMPED_TURBINING.id,
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
                    "operation": (
                        "storing" if pump_mw > turb_mw else "releasing" if turb_mw > pump_mw else "idle"
                    ),
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
                "efficiency_assessment": (
                    "normal" if 70 <= efficiency_pct <= 85 else "check_data"
                ),
            },
        }

        return ResponseFormatter.success(result)

    except Exception as e:
        return ResponseFormatter.unexpected_error(e, context="Error getting storage operations")


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
        async with ToolExecutor() as executor:
            use_case = executor.create_get_indicator_data_use_case()

            # Get max demand
            max_request = GetIndicatorDataRequest(
                indicator_id=IndicatorIDs.MAX_DAILY_DEMAND.id,
                start_date=start_date,
                end_date=end_date,
                time_granularity="day",
            )
            max_response = await use_case.execute(max_request)
            max_data = max_response.model_dump()

            # Get min demand
            min_request = GetIndicatorDataRequest(
                indicator_id=IndicatorIDs.MIN_DAILY_DEMAND.id,
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
        period_stats = {}
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

        result = {
            "period": {"start": start_date, "end": end_date},
            "daily_analysis": daily_analysis,
            "period_statistics": period_stats,
        }

        return ResponseFormatter.success(result)

    except Exception as e:
        return ResponseFormatter.unexpected_error(e, context="Error analyzing peaks")


# MCP Resources
@mcp.resource("ree://indicators")
async def list_all_indicators() -> str:
    """Resource providing the complete list of all REE indicators.

    Returns:
        JSON string with all indicator metadata.
    """
    try:
        async with ToolExecutor() as executor:
            use_case = executor.create_list_indicators_use_case()
            indicators = await use_case.execute(limit=None, offset=0)

        result = {
            "count": len(indicators),
            "indicators": [ind.model_dump() for ind in indicators],
        }
        return ResponseFormatter.success(result, ensure_ascii=False)

    except Exception as e:
        return ResponseFormatter.unexpected_error(e, context="Error listing indicators")


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
        return ResponseFormatter.success(result, ensure_ascii=False)

    except Exception as e:
        return ResponseFormatter.unexpected_error(e, context="Error getting indicator info")


def create_server() -> FastMCP:
    """Create and return the MCP server instance.

    Returns:
        Configured FastMCP server.
    """
    return mcp


# Entry point for running the server
if __name__ == "__main__":
    mcp.run()
