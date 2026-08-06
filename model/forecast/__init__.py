from typing import Dict, Optional

import pandas as pd


def forecast_financials(
    historical_data: pd.DataFrame, forecast_assumptions: Dict[str, object]
) -> pd.DataFrame:
    """Project future financials using historical results and forecast assumptions."""
    last_year_data = historical_data.iloc[-1]
    forecast_years = int(forecast_assumptions["forecast_years"])
    forecast = forecast_assumptions["forecast"]
    last_historical_year = int(str(last_year_data["fiscalDateEnding"])[:4])

    forecasted_rows = []
    for year in range(1, forecast_years + 1):
        revenue_growth_rate = forecast["revenue_growth_rate"]
        operating_margin = forecast["operating_margin"]
        tax_rate = forecast["tax_rate"]
        da_percent = forecast["daPercentRevenue"]
        capex_percent = forecast["capexPercentRevenue"]
        nwc_percent = forecast["nwcPercentRevenue"]

        # helper to support either scalar or per-year iterable inputs
        def val_for(param, idx):
            try:
                return param[idx]
            except Exception:
                return param

        revenue = (
            last_year_data["totalRevenue"] * (1 + val_for(revenue_growth_rate, year - 1))
            if year == 1
            else forecasted_rows[-1]["totalRevenue"] * (1 + val_for(revenue_growth_rate, year - 1))
        )

        operating_income = revenue * val_for(operating_margin, year - 1)

        income_tax_expense = operating_income * val_for(tax_rate, year - 1)
        nopat = operating_income - income_tax_expense
        forecasted_rows.append(
            {
                "year": last_historical_year + year,
                "totalRevenue": revenue,
                "operatingIncome": operating_income,
                "incomeTaxExpense": income_tax_expense,
                "nopat": nopat,
                "depreciationAndAmortization": revenue * val_for(da_percent, year - 1),
                "capitalExpenditures": revenue * val_for(capex_percent, year - 1),
                "netWorkingCapital": revenue * val_for(nwc_percent, year - 1),
            }
        )

    return pd.DataFrame(forecasted_rows)

def calculate_ufcf(
    forecasted_data: pd.DataFrame,
    prior_net_working_capital: Optional[float] = None,
) -> pd.DataFrame:
    """Calculate unlevered free cash flow from forecasted financials."""
    forecasted_data = forecasted_data.copy()
    forecasted_data["changeInOperatingNWC"] = forecasted_data["netWorkingCapital"].diff()
    if prior_net_working_capital is not None and len(forecasted_data) > 0:
        forecasted_data.iat[
            0,
            forecasted_data.columns.get_loc("changeInOperatingNWC"),
        ] = forecasted_data.iloc[0]["netWorkingCapital"] - prior_net_working_capital
    forecasted_data["changeInOperatingNWC"] = forecasted_data["changeInOperatingNWC"].fillna(0)
    
    forecasted_data["freeCashFlow"] = (
        forecasted_data["nopat"]
        + forecasted_data["depreciationAndAmortization"]
        - forecasted_data["capitalExpenditures"]
        - forecasted_data["changeInOperatingNWC"]
    )
    return forecasted_data
