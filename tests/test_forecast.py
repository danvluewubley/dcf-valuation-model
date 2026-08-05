import pytest
import pandas as pd

from model.forecast import calculate_ufcf, forecast_financials


def test_forecast_financials_builds_expected_rows():
    historical_data = pd.DataFrame(
        [
            {
                "fiscalDateEnding": "2022-12-31",
                "totalRevenue": 100.0,
                "operatingIncome": 20.0,
                "incomeTaxExpense": 5.0,
                "nopat": 15.0,
                "depreciationAndAmortization": 10.0,
                "capitalExpenditures": 5.0,
                "accountsReceivable": 10.0,
                "inventory": 5.0,
                "otherOperatingCurrentAssets": 2.0,
                "accountsPayable": 3.0,
                "otherOperatingCurrentLiabilities": 1.0,
                "shortTermDebt": 0.0,
                "longTermDebt": 0.0,
                "cashAndCashEquivalents": 0.0,
                "commonStockSharesOutstanding": 1.0,
            }
        ]
    )
    forecast_assumptions = {
        "forecast_years": 2,
        "forecast": {
            "revenue_growth_rate": 0.1,
            "operating_margin": 0.2,
            "tax_rate": 0.25,
            "daPercentRevenue": 0.1,
            "capexPercentRevenue": 0.05,
            "nwcPercentRevenue": 0.1,
        },
        "valuation": {
            "WACC": 0.1,
            "terminal_growth_rate": 0.02,
        },
    }

    forecasted_data = forecast_financials(historical_data, forecast_assumptions)

    assert len(forecasted_data) == 2
    assert forecasted_data.iloc[0]["totalRevenue"] == pytest.approx(110.0)
    assert forecasted_data.iloc[0]["operatingIncome"] == pytest.approx(22.0)
    assert forecasted_data.iloc[0]["nopat"] == pytest.approx(16.5)
    assert forecasted_data.iloc[1]["totalRevenue"] == pytest.approx(121.0)


def test_calculate_ufcf():
    forecasted_data = pd.DataFrame(
        [
            {
                "year": 2023,
                "nopat": 16.5,
                "depreciationAndAmortization": 11.0,
                "capitalExpenditures": 5.5,
                "netWorkingCapital": 11.0,
            },
            {
                "year": 2024,
                "nopat": 18.15,
                "depreciationAndAmortization": 12.1,
                "capitalExpenditures": 6.05,
                "netWorkingCapital": 12.1,
            },
        ]
    )

    result = calculate_ufcf(forecasted_data, prior_net_working_capital=10.0)

    assert result.loc[0, "changeInOperatingNWC"] == pytest.approx(1.0)
    assert result.loc[1, "changeInOperatingNWC"] == pytest.approx(1.1)
    assert result.loc[0, "freeCashFlow"] == pytest.approx(16.5 + 11.0 - 5.5 - 1.0)
    assert result.loc[1, "freeCashFlow"] == pytest.approx(18.15 + 12.1 - 6.05 - 1.1)
