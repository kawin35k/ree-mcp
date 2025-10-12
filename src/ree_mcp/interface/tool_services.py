"""Service classes for complex tool operations.

This module contains business logic services that handle multi-indicator
data fetching and complex calculations, following SRP and DRY principles.
"""

from typing import Any

from ..application.dtos import GetIndicatorDataRequest
from ..application.use_cases import GetIndicatorDataUseCase
from .indicator_config import IndicatorIDs, IndicatorMetadata


class DataFetcher:
    """Service for fetching data from multiple indicators.

    This class eliminates the repeated pattern of fetching data from multiple
    indicators in parallel and handling errors individually.
    """

    def __init__(self, use_case: GetIndicatorDataUseCase):
        """Initialize the data fetcher.

        Args:
            use_case: Use case for getting indicator data
        """
        self.use_case = use_case

    async def fetch_single_indicator(
        self,
        indicator: IndicatorMetadata,
        start_date: str,
        end_date: str,
        time_granularity: str = "hour",
    ) -> dict[str, Any] | None:
        """Fetch data for a single indicator.

        Args:
            indicator: Indicator metadata
            start_date: Start datetime in ISO format
            end_date: End datetime in ISO format
            time_granularity: Time aggregation level

        Returns:
            Response dictionary or None if error occurred
        """
        try:
            request = GetIndicatorDataRequest(
                indicator_id=indicator.id,
                start_date=start_date,
                end_date=end_date,
                time_granularity=time_granularity,
            )
            response = await self.use_case.execute(request)
            return response.model_dump()
        except Exception:
            return None

    async def fetch_multiple_indicators(
        self,
        indicators: dict[str, IndicatorMetadata],
        start_date: str,
        end_date: str,
        time_granularity: str = "hour",
    ) -> dict[str, dict[str, Any]]:
        """Fetch data for multiple indicators.

        Args:
            indicators: Dictionary mapping names to indicator metadata
            start_date: Start datetime in ISO format
            end_date: End datetime in ISO format
            time_granularity: Time aggregation level

        Returns:
            Dictionary mapping names to response data (or error info)
        """
        results: dict[str, dict[str, Any]] = {}

        for name, indicator in indicators.items():
            response = await self.fetch_single_indicator(
                indicator, start_date, end_date, time_granularity
            )

            if response is None:
                results[name] = {"error": f"Failed to fetch data for {indicator.name}"}
            else:
                results[name] = response

        return results

    async def fetch_value_at_time(
        self,
        indicator: IndicatorMetadata,
        start_date: str,
        end_date: str,
        time_granularity: str = "hour",
    ) -> float | None:
        """Fetch single value for an indicator at a specific time.

        Args:
            indicator: Indicator metadata
            start_date: Start datetime in ISO format
            end_date: End datetime in ISO format
            time_granularity: Time aggregation level

        Returns:
            First value from response or None if not available
        """
        response = await self.fetch_single_indicator(
            indicator, start_date, end_date, time_granularity
        )

        if response and "values" in response and response["values"]:
            return response["values"][0]["value"]  # type: ignore[no-any-return]

        return None


class GenerationMixService:
    """Service for generation mix analysis.

    Handles fetching and aggregating generation data from multiple sources.
    """

    def __init__(self, data_fetcher: DataFetcher):
        """Initialize the generation mix service.

        Args:
            data_fetcher: Data fetcher instance
        """
        self.data_fetcher = data_fetcher

    async def get_generation_mix(
        self, start_date: str, end_date: str
    ) -> dict[str, Any]:
        """Get generation mix for a specific time.

        Args:
            start_date: Start datetime in ISO format
            end_date: End datetime in ISO format

        Returns:
            Generation mix data with sources and values
        """
        sources = IndicatorIDs.get_generation_mix_sources()
        raw_data = await self.data_fetcher.fetch_multiple_indicators(
            sources, start_date, end_date, "hour"
        )

        generation_mix: dict[str, Any] = {
            "datetime": start_date,
            "sources": {},
        }

        for source_name, response_data in raw_data.items():
            if "error" in response_data:
                generation_mix["sources"][source_name] = response_data
            else:
                values = response_data.get("values", [])
                if values:
                    generation_mix["sources"][source_name] = {
                        "value_mw": values[0]["value"],
                        "unit": response_data["indicator"]["unit"],
                    }
                else:
                    generation_mix["sources"][source_name] = {"error": "No data available"}

        return generation_mix

    async def get_generation_mix_timeline(
        self, start_date: str, end_date: str, time_granularity: str = "hour"
    ) -> dict[str, Any]:
        """Get generation mix over a period.

        Args:
            start_date: Start datetime in ISO format
            end_date: End datetime in ISO format
            time_granularity: Time aggregation level

        Returns:
            Timeline data with generation mix at each point
        """
        sources = IndicatorIDs.get_generation_mix_sources()
        raw_data = await self.data_fetcher.fetch_multiple_indicators(
            sources, start_date, end_date, time_granularity
        )

        result: dict[str, Any] = {
            "period": {
                "start": start_date,
                "end": end_date,
                "granularity": time_granularity,
            },
            "timeline": [],
        }

        # Build timeline by combining data points
        source_data: dict[str, list[dict[str, Any]]] = {}
        for source_name, response_data in raw_data.items():
            if "error" not in response_data:
                source_data[source_name] = response_data.get("values", [])
            else:
                source_data[source_name] = []

        if source_data:
            # Use first source to get timestamps
            first_source_values = next(iter(source_data.values()))
            for i, value_point in enumerate(first_source_values):
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

        return result


class RenewableAnalysisService:
    """Service for renewable energy analysis.

    Handles renewable generation aggregation and percentage calculations.
    """

    def __init__(self, data_fetcher: DataFetcher):
        """Initialize the renewable analysis service.

        Args:
            data_fetcher: Data fetcher instance
        """
        self.data_fetcher = data_fetcher

    async def get_renewable_summary(
        self, start_date: str, end_date: str
    ) -> dict[str, Any]:
        """Get renewable generation summary.

        Args:
            start_date: Start datetime in ISO format
            end_date: End datetime in ISO format

        Returns:
            Renewable summary with breakdowns and percentages
        """
        renewable_sources = IndicatorIDs.get_renewable_sources()
        raw_data = await self.data_fetcher.fetch_multiple_indicators(
            renewable_sources, start_date, end_date, "hour"
        )

        result: dict[str, Any] = {
            "datetime": start_date,
            "renewable_sources": {},
            "summary": {},
        }

        total_renewable_mw = 0.0
        variable_renewable_mw = 0.0

        # Process renewable sources
        for source_name, response_data in raw_data.items():
            if "error" in response_data:
                result["renewable_sources"][source_name] = response_data
            else:
                values = response_data.get("values", [])
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
                else:
                    result["renewable_sources"][source_name] = {"error": "No data available"}

        # Get total demand for percentage calculation
        demand_mw = await self.data_fetcher.fetch_value_at_time(
            IndicatorIDs.REAL_DEMAND_NATIONAL, start_date, end_date, "hour"
        )

        if demand_mw and demand_mw > 0:
            renewable_pct = (total_renewable_mw / demand_mw) * 100
            variable_pct = (variable_renewable_mw / demand_mw) * 100

            result["summary"] = {
                "total_renewable_mw": round(total_renewable_mw, 2),
                "variable_renewable_mw": round(variable_renewable_mw, 2),
                "synchronous_renewable_mw": round(
                    total_renewable_mw - variable_renewable_mw, 2
                ),
                "total_demand_mw": round(demand_mw, 2),
                "renewable_percentage": round(renewable_pct, 2),
                "variable_renewable_percentage": round(variable_pct, 2),
            }
        else:
            result["summary"] = {"error": "Could not calculate percentages: No demand data"}

        return result


class GridStabilityService:
    """Service for grid stability analysis.

    Analyzes balance between synchronous generation (provides inertia)
    and variable renewables (no inertia).
    """

    def __init__(self, data_fetcher: DataFetcher):
        """Initialize the grid stability service.

        Args:
            data_fetcher: Data fetcher instance
        """
        self.data_fetcher = data_fetcher

    async def get_grid_stability(
        self, start_date: str, end_date: str
    ) -> dict[str, Any]:
        """Get grid stability metrics.

        Args:
            start_date: Start datetime in ISO format
            end_date: End datetime in ISO format

        Returns:
            Grid stability analysis with synchronous/variable breakdown
        """
        synchronous = IndicatorIDs.get_synchronous_sources()
        variable_renewables = IndicatorIDs.get_variable_renewable_sources()

        # Fetch all data
        sync_data = await self.data_fetcher.fetch_multiple_indicators(
            synchronous, start_date, end_date, "hour"
        )
        var_data = await self.data_fetcher.fetch_multiple_indicators(
            variable_renewables, start_date, end_date, "hour"
        )

        result: dict[str, Any] = {
            "datetime": start_date,
            "synchronous_generation": {},
            "variable_renewables": {},
            "analysis": {},
        }

        # Process synchronous generation
        total_synchronous_mw = 0.0
        for source_name, response_data in sync_data.items():
            if "error" not in response_data:
                values = response_data.get("values", [])
                if values:
                    value_mw = values[0]["value"]
                    result["synchronous_generation"][source_name] = {"value_mw": value_mw}
                    total_synchronous_mw += value_mw
                else:
                    result["synchronous_generation"][source_name] = {"error": "No data"}
            else:
                result["synchronous_generation"][source_name] = response_data

        # Process variable renewables
        total_variable_mw = 0.0
        for source_name, response_data in var_data.items():
            if "error" not in response_data:
                values = response_data.get("values", [])
                if values:
                    value_mw = values[0]["value"]
                    result["variable_renewables"][source_name] = {"value_mw": value_mw}
                    total_variable_mw += value_mw
                else:
                    result["variable_renewables"][source_name] = {"error": "No data"}
            else:
                result["variable_renewables"][source_name] = response_data

        # Calculate analysis metrics
        demand_mw = await self.data_fetcher.fetch_value_at_time(
            IndicatorIDs.REAL_DEMAND_NATIONAL, start_date, end_date, "hour"
        )

        if demand_mw and demand_mw > 0:
            synchronous_pct = (total_synchronous_mw / demand_mw) * 100
            variable_pct = (total_variable_mw / demand_mw) * 100
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
                "total_demand_mw": round(demand_mw, 2),
                "synchronous_percentage": round(synchronous_pct, 2),
                "variable_renewable_percentage": round(variable_pct, 2),
                "inertia_ratio": (
                    round(inertia_ratio, 2) if inertia_ratio != float("inf") else "infinite"
                ),
                "stability_level": stability_level,
                "interpretation": {
                    "excellent": ">=70% synchronous (high inertia)",
                    "good": "50-70% synchronous (adequate inertia)",
                    "moderate": "30-50% synchronous (requires monitoring)",
                    "concerning": "<30% synchronous (stability risk)",
                },
            }
        else:
            result["analysis"] = {"error": "Could not calculate analysis: No demand data"}

        return result


class InternationalExchangeService:
    """Service for international electricity exchange analysis."""

    def __init__(self, data_fetcher: DataFetcher):
        """Initialize the international exchange service.

        Args:
            data_fetcher: Data fetcher instance
        """
        self.data_fetcher = data_fetcher

    async def get_international_exchanges(
        self, start_date: str, end_date: str
    ) -> dict[str, Any]:
        """Get international electricity exchanges.

        Args:
            start_date: Start datetime in ISO format
            end_date: End datetime in ISO format

        Returns:
            Exchange data by country with net balance
        """
        exchanges = IndicatorIDs.get_international_exchanges()

        result: dict[str, Any] = {
            "datetime": start_date,
            "exchanges": {},
            "totals": {"total_exports_mw": 0.0, "total_imports_mw": 0.0, "net_balance_mw": 0.0},
        }

        for country, indicators in exchanges.items():
            # Fetch export and import data
            export_mw = await self.data_fetcher.fetch_value_at_time(
                indicators["export"], start_date, end_date, "hour"
            )
            import_mw = await self.data_fetcher.fetch_value_at_time(
                indicators["import"], start_date, end_date, "hour"
            )

            if export_mw is not None and import_mw is not None:
                net_mw = import_mw - export_mw

                result["exchanges"][country] = {
                    "export_mw": export_mw,
                    "import_mw": import_mw,
                    "net_balance_mw": net_mw,
                    "net_flow": (
                        "import" if net_mw > 0 else "export" if net_mw < 0 else "balanced"
                    ),
                }

                result["totals"]["total_exports_mw"] += export_mw
                result["totals"]["total_imports_mw"] += import_mw
            else:
                result["exchanges"][country] = {"error": "Could not fetch exchange data"}

        result["totals"]["net_balance_mw"] = (
            result["totals"]["total_imports_mw"] - result["totals"]["total_exports_mw"]
        )

        return result
