"""Financial model package."""

from .assumptions import get_custom_forecast_assumptions, get_historical_average_forecast_assumptions
from .data import (
    build_historical_dataset,
    download_financial_statements,
    load_financial_statements,
)
from .forecast import calculate_ufcf, forecast_financials
from .validation import validate_historical_data
from .valuation import (
    calculate_dcf_metrics,
    calculate_enterprise_value,
    calculate_equity_value,
    calculate_intrinsic_value_per_share,
)

__all__ = [
    "get_historical_average_forecast_assumptions",
    "get_custom_forecast_assumptions",
    "download_financial_statements",
    "load_financial_statements",
    "build_historical_dataset",
    "validate_historical_data",
    "forecast_financials",
    "calculate_ufcf",
    "calculate_dcf_metrics",
    "calculate_enterprise_value",
    "calculate_equity_value",
    "calculate_intrinsic_value_per_share",
]
