from typing import List
from numbers import Real
from collections.abc import Mapping

import pandas as pd


def validate_historical_data(historical_data: pd.DataFrame) -> pd.DataFrame:
    """Validate a historical dataset and return it if it passes checks."""
    required_columns = [
        "fiscalDateEnding",
        "totalRevenue",
        "operatingIncome",
        "incomeTaxExpense",
        "incomeBeforeTax",
        "nopat",
        "depreciationAndAmortization",
        "capitalExpenditures",
        "cashAndCashEquivalents",
        "shortTermDebt",
        "longTermDebt",
        "totalCurrentAssets",
        "totalCurrentLiabilities",
        "commonStockSharesOutstanding",
        "accountsReceivable",
        "inventory",
        "accountsPayable",
        "otherOperatingCurrentAssets",
        "otherOperatingCurrentLiabilities",
    ]

    errors: List[str] = []

    if historical_data.empty:
        errors.append("Historical dataset is empty.")

    missing_columns = [
        column
        for column in required_columns
        if column not in historical_data.columns
    ]
    if missing_columns:
        errors.append(f"Missing columns: {missing_columns}")

    historical_data = historical_data.copy()
    historical_data["fiscalDateEnding"] = pd.to_datetime(
        historical_data["fiscalDateEnding"], errors="coerce"
    )
    if historical_data["fiscalDateEnding"].isna().any():
        errors.append("One or more fiscal dates are invalid.")

    if historical_data["fiscalDateEnding"].duplicated().any():
        duplicate_dates = historical_data.loc[
            historical_data["fiscalDateEnding"].duplicated(), "fiscalDateEnding"
        ].tolist()
        errors.append(f"Duplicate fiscal dates: {duplicate_dates}")

    numeric_columns = [column for column in required_columns if column != "fiscalDateEnding"]
    for column in numeric_columns:
        if column in historical_data.columns:
            if not pd.api.types.is_numeric_dtype(historical_data[column]):
                errors.append(f"{column} is not numeric.")
            if historical_data[column].isna().any():
                missing_dates = historical_data.loc[
                    historical_data[column].isna(), "fiscalDateEnding"
                ].tolist()
                errors.append(
                    f"{column} contains missing values for {missing_dates}."
                )

    for column in [
        "totalRevenue",
        "commonStockSharesOutstanding",
        "totalCurrentAssets",
    ]:
        if column in historical_data.columns and (historical_data[column] <= 0).any():
            errors.append(f"{column} contains zero or negative values.")

    for column in [
        "cashAndCashEquivalents",
        "shortTermDebt",
        "longTermDebt",
        "totalCurrentLiabilities",
    ]:
        if column in historical_data.columns and (historical_data[column] < 0).any():
            errors.append(f"{column} contains negative values.")

    if errors:
        raise ValueError("Historical data validation failed:\n- " + "\n- ".join(errors))

    print("Historical data validation passed.")
    return historical_data

def validate_valuation_assumptions(
    valuation_assumptions: Mapping[str, Real],
) -> None:
    """Validate required valuation assumption fields and their numeric ranges."""
    required_fields = {"WACC", "terminal_growth_rate"}

    missing_fields = required_fields - valuation_assumptions.keys()
    if missing_fields:
        missing = ", ".join(sorted(missing_fields))
        raise ValueError(
            f"Missing valuation assumptions: {missing}"
        )

    wacc = float(valuation_assumptions["WACC"])
    terminal_growth_rate = float(
        valuation_assumptions["terminal_growth_rate"]
    )

    if not 0 < wacc < 1:
        raise ValueError(
            f"WACC must be between 0 and 1. Received: {wacc}"
        )

    if not -1 < terminal_growth_rate < 1:
        raise ValueError(
            "Terminal growth rate must be between -1 and 1. "
            f"Received: {terminal_growth_rate}"
        )

    if wacc <= terminal_growth_rate:
        raise ValueError(
            "WACC must be greater than the terminal growth rate. "
            f"Received WACC={wacc:.2%} and "
            f"terminal growth={terminal_growth_rate:.2%}."
        )
    
    print("Valuation assumptions validation passed.")

def validate_forecast_assumptions(
    forecast_assumptions: Mapping[str, object],
) -> None:
    """Validate forecast assumption structure and ensure values are sane."""
    required_fields = {
        "forecast_years",
        "forecast",
        "valuation",
    }

    missing_fields = required_fields - forecast_assumptions.keys()
    if missing_fields:
        missing = ", ".join(sorted(missing_fields))
        raise ValueError(
            f"Missing forecast assumptions: {missing}"
        )

    forecast_years = int(forecast_assumptions["forecast_years"])
    if forecast_years <= 0:
        raise ValueError(
            f"Forecast years must be a positive integer. Received: {forecast_years}"
        )
     
    capex_vals = forecast_assumptions["forecast"]["capexPercentRevenue"]
    # support either a scalar or an iterable of per-year values
    try:
        iterator = iter(capex_vals)
    except TypeError:
        iterator = [capex_vals]

    for capex_percent in iterator:
        if capex_percent < 0:
            raise ValueError(
                f"Capital expenditures as a percentage of revenue must be non-negative. Received: {capex_percent}"
            )    

    print("Forecast assumptions validation passed.")

def validate_equity_inputs(outstanding_shares: float, total_debt: float, cash_and_cash_equivalents: float) -> None:
    """Validate inputs used for equity value calculation."""
    if outstanding_shares <= 0:
        raise ValueError(
            f"Outstanding shares must be a positive number. Received: {outstanding_shares}"
        )
    if total_debt < 0:
        raise ValueError(
            f"Total debt must be a non-negative number. Received: {total_debt}"
        )
    if cash_and_cash_equivalents < 0:
        raise ValueError(
            f"Cash and cash equivalents must be a non-negative number. Received: {cash_and_cash_equivalents}"
        )
    print("Equity inputs validation passed.")