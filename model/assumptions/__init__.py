from typing import Dict

import pandas as pd


def get_custom_forecast_assumptions() -> Dict[str, object]:
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

def get_historical_average_forecast_assumptions(historical_data: pd.DataFrame) -> Dict[str, object]:
    revenue_growth_rate = historical_data["totalRevenue"].pct_change().mean()
    operating_margin = (historical_data["operatingIncome"] / historical_data["totalRevenue"]).mean()
    tax_rate = (historical_data["incomeTaxExpense"] / historical_data["incomeBeforeTax"]).mean()
    da_percent = (historical_data["depreciationAndAmortization"] / historical_data["totalRevenue"]).mean()
    capex_percent = (historical_data["capitalExpenditures"] / historical_data["totalRevenue"]).mean()
    nwc_percent = (
        (historical_data["accountsReceivable"]
         + historical_data["inventory"]
         + historical_data["otherOperatingCurrentAssets"]
         - historical_data["accountsPayable"]
         - historical_data["otherOperatingCurrentLiabilities"])
        / historical_data["totalRevenue"]
    ).mean()

    return {
        "forecast_years": 5,
        "forecast": {
            "revenue_growth_rate": [revenue_growth_rate] * 5,
            "operating_margin": [operating_margin] * 5,
            "tax_rate": [tax_rate] * 5,
            "daPercentRevenue": [da_percent] * 5,
            "capexPercentRevenue": [capex_percent] * 5,
            "nwcPercentRevenue": [nwc_percent] * 5,
        },
        "valuation": {
            "WACC": 0.1,
            "terminal_growth_rate": 0.02,
        },
    }
    
def get_bear_forecast_assumptions() -> Dict[str, object]:
    return {
        "forecast_years": 5,
        "forecast": {
            "revenue_growth_rate": [0.03, 0.025, 0.02, 0.02, 0.02],
            "operating_margin": [0.300, 0.298, 0.297, 0.296, 0.295],
            "tax_rate": [0.17, 0.17, 0.17, 0.17, 0.17],
            "daPercentRevenue": [0.029, 0.029, 0.029, 0.029, 0.029],
            "capexPercentRevenue": [0.032, 0.032, 0.031, 0.031, 0.031],
            "nwcPercentRevenue": [-0.138, -0.138, -0.137, -0.137, -0.137],
        },
        "valuation": {
            "WACC": 0.120,
            "terminal_growth_rate": 0.020,
        },
    }
    
def get_bull_forecast_assumptions() -> Dict[str, object]:
    return {
        "forecast_years": 5,
        "forecast": {
            "revenue_growth_rate": [0.08, 0.075, 0.07, 0.06, 0.05],
            "operating_margin": [0.320, 0.323, 0.326, 0.328, 0.330],
            "tax_rate": [0.155, 0.155, 0.155, 0.155, 0.155],
            "daPercentRevenue": [0.0285, 0.028, 0.028, 0.0275, 0.0275],
            "capexPercentRevenue": [0.030, 0.0295, 0.029, 0.0285, 0.028],
            "nwcPercentRevenue": [-0.142, -0.142, -0.141, -0.141, -0.140],
        },
        "valuation": {
            "WACC": 0.100,
            "terminal_growth_rate": 0.030,
        },
    }
    
def get_base_forecast_assumptions() -> Dict[str, object]:
    return {
        "forecast_years": 5,
        "forecast": {
            "revenue_growth_rate": [0.06, 0.055, 0.05, 0.04, 0.03],
            "operating_margin": [0.310, 0.312, 0.315, 0.317, 0.320],
            "tax_rate": [0.16, 0.16, 0.16, 0.16, 0.16],
            "daPercentRevenue": [0.029, 0.029, 0.0285, 0.028, 0.028],
            "capexPercentRevenue": [0.031, 0.030, 0.030, 0.029, 0.029],
            "nwcPercentRevenue": [-0.140, -0.140, -0.139, -0.138, -0.138],
        },
        "valuation": {
            "WACC": 0.1091,
            "terminal_growth_rate": 0.025,
        },
    }