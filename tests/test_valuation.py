import pytest
import pandas as pd

from model.valuation import (
    calculate_dcf_metrics,
    calculate_enterprise_value,
    calculate_equity_value,
    calculate_intrinsic_value_per_share,
)


@pytest.fixture
def historical_data():
    return pd.DataFrame(
        [
            {
                "fiscalDateEnding": "2021-12-31",
                "totalRevenue": 80.0,
                "operatingIncome": 16.0,
                "incomeTaxExpense": 4.0,
                "incomeBeforeTax": 16.0,
                "nopat": 12.0,
                "depreciationAndAmortization": 8.0,
                "capitalExpenditures": 4.0,
                "accountsReceivable": 8.0,
                "inventory": 4.0,
                "otherOperatingCurrentAssets": 2.0,
                "accountsPayable": 3.0,
                "otherOperatingCurrentLiabilities": 1.0,
                "shortTermDebt": 5.0,
                "longTermDebt": 10.0,
                "cashAndCashEquivalents": 2.0,
                "commonStockSharesOutstanding": 2.0,
            },
            {
                "fiscalDateEnding": "2022-12-31",
                "totalRevenue": 100.0,
                "operatingIncome": 20.0,
                "incomeTaxExpense": 5.0,
                "incomeBeforeTax": 20.0,
                "nopat": 15.0,
                "depreciationAndAmortization": 10.0,
                "capitalExpenditures": 5.0,
                "accountsReceivable": 10.0,
                "inventory": 5.0,
                "otherOperatingCurrentAssets": 2.0,
                "accountsPayable": 3.0,
                "otherOperatingCurrentLiabilities": 1.0,
                "shortTermDebt": 5.0,
                "longTermDebt": 10.0,
                "cashAndCashEquivalents": 2.0,
                "commonStockSharesOutstanding": 2.0,
            },
        ]
    )


def test_calculate_dcf_metrics_adds_expected_columns(historical_data):
    result = calculate_dcf_metrics(historical_data)

    assert "taxRate" in result.columns
    assert "totalDebt" in result.columns
    assert "operatingNetWorkingCapital" in result.columns
    assert "revenue_growth_rate" in result.columns
    assert result.loc[1, "taxRate"] == pytest.approx(0.25)
    assert result.loc[1, "revenue_growth_rate"] == pytest.approx(0.25)


def test_calculate_enterprise_value_and_equity_value(historical_data):
    result = calculate_dcf_metrics(historical_data)
    forecasted_data = pd.DataFrame(
        [
            {"freeCashFlow": 10.0},
            {"freeCashFlow": 11.0},
            {"freeCashFlow": 12.0},
        ]
    )
    forecast_assumptions = {
        "valuation": {
            "WACC": 0.1,
            "terminal_growth_rate": 0.02,
        }
    }

    enterprise_value, terminal_value = calculate_enterprise_value(
        forecasted_data, forecast_assumptions
    )
    equity_value = calculate_equity_value(enterprise_value, result)
    intrinsic_value = calculate_intrinsic_value_per_share(
        equity_value, result
    )

    assert enterprise_value > 0
    assert terminal_value > 0
    assert intrinsic_value == pytest.approx(
        equity_value / float(historical_data["commonStockSharesOutstanding"].iloc[-1])
    )
