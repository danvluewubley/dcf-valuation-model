from typing import Dict

import pandas as pd


def get_forecast_assumptions(historical_data: pd.DataFrame) -> Dict[str, object]:
    return {
        "forecast_years": 5,
        "forecast": {
            "revenue_growth_rate": [0.06, 0.055, 0.05, 0.04, 0.03],
            "operating_margin": [0.31, 0.312, 0.315, 0.317, 0.32],
            "tax_rate": [0.16, 0.16, 0.16, 0.16, 0.16],
            "daPercentRevenue": [0.029, 0.029, 0.0285, 0.028, 0.028],
            "capexPercentRevenue": [0.031, 0.03, 0.03, 0.029, 0.029],
            "nwcPercentRevenue": [-0.14, -0.14, -0.139, -0.138, -0.138],
        },
        "valuation": {
            "WACC": 0.1091,
            "terminal_growth_rate": 0.025,
        },
    }
