from typing import Dict

import pandas as pd


def forecast_financials(
    historical_data: pd.DataFrame, forecast_assumptions: Dict[str, object]
) -> pd.DataFrame:
    last_year_data = historical_data.iloc[-1]
    forecast_years = int(forecast_assumptions["forecast_years"])
    forecast = forecast_assumptions["forecast"]
    last_historical_year = int(str(last_year_data["fiscalDateEnding"])[:4])

    forecasted_rows = []
    for year in range(1, forecast_years + 1):
        revenue_growth_rate = float(forecast["revenue_growth_rate"])
        operating_margin = float(forecast["operating_margin"])
        tax_rate = float(forecast["tax_rate"])
        da_percent = float(forecast["daPercentRevenue"])
        capex_percent = float(forecast["capexPercentRevenue"])
        nwc_percent = float(forecast["nwcPercentRevenue"])

        revenue = (
            last_year_data["totalRevenue"] * (1 + revenue_growth_rate)
            if year == 1
            else forecasted_rows[-1]["totalRevenue"] * (1 + revenue_growth_rate)
        )

        operating_income = revenue * operating_margin
        income_tax_expense = operating_income * tax_rate
        nopat = operating_income - income_tax_expense
        forecasted_rows.append(
            {
                "year": last_historical_year + year,
                "totalRevenue": revenue,
                "operatingIncome": operating_income,
                "incomeTaxExpense": income_tax_expense,
                "nopat": nopat,
                "depreciationAndAmortization": revenue * da_percent,
                "capitalExpenditures": revenue * capex_percent,
                "netWorkingCapital": revenue * nwc_percent,
            }
        )

    return pd.DataFrame(forecasted_rows)


def calculate_ufcf(forecasted_data: pd.DataFrame) -> pd.DataFrame:
    forecasted_data = forecasted_data.copy()
    forecasted_data["changeInOperatingNWC"] = (
        forecasted_data["netWorkingCapital"].diff().fillna(0)
    )
    forecasted_data["freeCashFlow"] = (
        forecasted_data["nopat"]
        + forecasted_data["depreciationAndAmortization"]
        - forecasted_data["capitalExpenditures"]
        - forecasted_data["changeInOperatingNWC"]
    )
    return forecasted_data
