import pytest
import pandas as pd

from model.validation import (
    validate_historical_data,
    validate_valuation_assumptions,
    validate_forecast_assumptions,
    validate_equity_inputs,
)


def make_valid_historical_df():
    cols = {
        "fiscalDateEnding": ["2020-12-31"],
        "totalRevenue": [100.0],
        "operatingIncome": [20.0],
        "incomeTaxExpense": [3.5],
        "incomeBeforeTax": [23.5],
        "nopat": [17.0],
        "depreciationAndAmortization": [5.0],
        "capitalExpenditures": [5.0],
        "cashAndCashEquivalents": [10.0],
        "shortTermDebt": [0.0],
        "longTermDebt": [0.0],
        "totalCurrentAssets": [50.0],
        "totalCurrentLiabilities": [5.0],
        "commonStockSharesOutstanding": [1_000.0],
        "accountsReceivable": [5.0],
        "inventory": [2.0],
        "accountsPayable": [3.0],
        "otherOperatingCurrentAssets": [1.0],
        "otherOperatingCurrentLiabilities": [1.0],
    }
    return pd.DataFrame(cols)


def test_validate_historical_data_passes():
    df = make_valid_historical_df()
    validated = validate_historical_data(df)
    assert isinstance(validated, pd.DataFrame)


def test_validate_historical_data_missing_column_raises():
    df = make_valid_historical_df()
    df = df.drop(columns=["totalRevenue"])
    with pytest.raises(ValueError):
        validate_historical_data(df)


def test_validate_valuation_assumptions_passes():
    assumptions = {"WACC": 0.09, "terminal_growth_rate": 0.02}
    validate_valuation_assumptions(assumptions)


def test_validate_valuation_assumptions_missing_field_raises():
    with pytest.raises(ValueError):
        validate_valuation_assumptions({"WACC": 0.1})


def test_validate_valuation_assumptions_invalid_wacc_raises():
    with pytest.raises(ValueError):
        validate_valuation_assumptions({"WACC": 1.5, "terminal_growth_rate": 0.02})


def test_validate_valuation_assumptions_wacc_leq_terminal_raises():
    with pytest.raises(ValueError):
        validate_valuation_assumptions({"WACC": 0.02, "terminal_growth_rate": 0.03})


def test_validate_forecast_assumptions_passes():
    forecast = {"forecast_years": 1, "forecast": {"capexPercentRevenue": 0.05}, "valuation": {}}
    validate_forecast_assumptions(forecast)


def test_validate_forecast_assumptions_negative_capex_raises():
    forecast = {"forecast_years": 1, "forecast": {"capexPercentRevenue": -0.1}, "valuation": {}}
    with pytest.raises(ValueError):
        validate_forecast_assumptions(forecast)


def test_validate_equity_inputs_passes():
    validate_equity_inputs(1_000.0, 0.0, 0.0)


def test_validate_equity_inputs_invalid_shares_raises():
    with pytest.raises(ValueError):
        validate_equity_inputs(0.0, 0.0, 0.0)
