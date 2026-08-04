from typing import Dict, Tuple

import pandas as pd


def calculate_dcf_metrics(historical_data: pd.DataFrame) -> pd.DataFrame:
    historical_data = historical_data.sort_values("fiscalDateEnding").reset_index(drop=True).copy()
    historical_data["taxRate"] = (
        historical_data["incomeTaxExpense"]
        / historical_data["incomeBeforeTax"].replace(0, pd.NA)
    )
    historical_data["totalDebt"] = (
        historical_data["shortTermDebt"] + historical_data["longTermDebt"]
    )

    historical_data["operatingNetWorkingCapital"] = (
        historical_data["accountsReceivable"]
        + historical_data["inventory"]
        + historical_data["otherOperatingCurrentAssets"]
        - historical_data["accountsPayable"]
        - historical_data["otherOperatingCurrentLiabilities"]
    )
    historical_data["changeInOperatingNWC"] = historical_data["operatingNetWorkingCapital"].diff()
    historical_data["revenue_growth_rate"] = historical_data["totalRevenue"].pct_change()
    historical_data["operating_margin"] = historical_data["operatingIncome"] / historical_data["totalRevenue"]
    historical_data["daPercentRevenue"] = historical_data["depreciationAndAmortization"] / historical_data["totalRevenue"]
    historical_data["capexPercentRevenue"] = historical_data["capitalExpenditures"] / historical_data["totalRevenue"]
    historical_data["nwcPercentRevenue"] = (
        historical_data["operatingNetWorkingCapital"] / historical_data["totalRevenue"]
    )
    return historical_data


def calculate_enterprise_value(
    forecasted_data: pd.DataFrame, forecast_assumptions: Dict[str, object]
) -> Tuple[float, float]:
    WACC = float(forecast_assumptions["valuation"]["WACC"])
    terminal_growth_rate = float(
        forecast_assumptions["valuation"]["terminal_growth_rate"]
    )

    forecasted_data = forecasted_data.copy()
    forecasted_data["discount_factor"] = (1 + WACC) ** (forecasted_data.index + 1)
    forecasted_data["present_value"] = (
        forecasted_data["freeCashFlow"] / forecasted_data["discount_factor"]
    )

    terminal_value = (
        forecasted_data["freeCashFlow"].iloc[-1] * (1 + terminal_growth_rate)
        / (WACC - terminal_growth_rate)
    )
    present_value_terminal = terminal_value / ((1 + WACC) ** len(forecasted_data))
    total_present_value = forecasted_data["present_value"].sum() + present_value_terminal

    return float(total_present_value), float(present_value_terminal)


def calculate_equity_value(enterprise_value: float, historical_data: pd.DataFrame) -> float:
    return float(
        enterprise_value
        - historical_data["shortTermDebt"].iloc[-1]
        - historical_data["longTermDebt"].iloc[-1]
        + historical_data["cashAndCashEquivalents"].iloc[-1]
    )


def calculate_intrinsic_value_per_share(
    equity_value: float, historical_data: pd.DataFrame
) -> float:
    shares_outstanding = float(
        historical_data["commonStockSharesOutstanding"].iloc[-1]
    )
    return equity_value / shares_outstanding
