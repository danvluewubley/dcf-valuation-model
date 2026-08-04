from typing import Dict

import pandas as pd


def get_forecast_assumptions(historical_data: pd.DataFrame) -> Dict[str, object]:
    return {
        "forecast_years": 5,
        "forecast": {
            "revenue_growth_rate": historical_data["revenue_growth_rate"].mean(),
            "operating_margin": historical_data["operating_margin"].mean(),
            "tax_rate": historical_data["taxRate"].mean(),
            "daPercentRevenue": historical_data["daPercentRevenue"].mean(),
            "capexPercentRevenue": historical_data["capexPercentRevenue"].mean(),
            "nwcPercentRevenue": historical_data["nwcPercentRevenue"].mean(),
        },
        "valuation": {
            "WACC": 0.1091,
            "terminal_growth_rate": 0.025,
        },
    }
