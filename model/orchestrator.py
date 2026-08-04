from pathlib import Path

import pandas as pd

from model.assumptions import get_forecast_assumptions
from model.data import (
    build_historical_dataset,
    download_financial_statements,
    load_financial_statements,
)
from model.forecast import calculate_ufcf, forecast_financials
from model.validation import validate_equity_inputs, validate_forecast_assumptions, validate_historical_data, validate_valuation_assumptions
from model.valuation import (
    calculate_dcf_metrics,
    calculate_equity_value,
    calculate_enterprise_value,
    calculate_intrinsic_value_per_share,
)


def run_model(ticker: str) -> None:
    output_dir = Path(__file__).parent.parent / "data" / ticker
    outputs_dir = Path(__file__).parent.parent / "outputs" / ticker
    outputs_dir.mkdir(parents=True, exist_ok=True)

    download_financial_statements(ticker, output_dir)

    income_statement, balance_sheet, cash_flow = load_financial_statements(
        ticker, output_dir
    )

    historical_path = output_dir / f"{ticker}_historical_data.csv"
    if historical_path.exists():
        print("Using cached historical data.")
        historical_data = pd.read_csv(historical_path)
    else:
        historical_data = build_historical_dataset(
            income_statement, balance_sheet, cash_flow
        )
        historical_data.to_csv(historical_path, index=False)
        print("Built and saved historical data.")

    historical_data = validate_historical_data(historical_data)
    historical_data = (
        historical_data.sort_values("fiscalDateEnding").tail(5).reset_index(drop=True)
    )

    historical_data = calculate_dcf_metrics(historical_data)
    historical_data.to_csv(historical_path, index=False)
    outputs_historical_path = outputs_dir / f"{ticker}_historical_data.csv"
    historical_data.to_csv(outputs_historical_path, index=False)

    forecast_assumptions = get_forecast_assumptions(historical_data)
    validate_forecast_assumptions(forecast_assumptions)
    validate_valuation_assumptions(forecast_assumptions["valuation"])

    forecasted_data = forecast_financials(historical_data, forecast_assumptions)
    forecasted_data = calculate_ufcf(forecasted_data)
    forecasted_path = output_dir / f"{ticker}_forecasted_data.csv"
    forecasted_data.to_csv(forecasted_path, index=False)
    outputs_forecasted_path = outputs_dir / f"{ticker}_forecasted_data.csv"
    forecasted_data.to_csv(outputs_forecasted_path, index=False)

    enterprise_value, terminal_value = calculate_enterprise_value(
        forecasted_data, forecast_assumptions
    )
    
    total_debt = historical_data["shortTermDebt"].iloc[-1] + historical_data["longTermDebt"].iloc[-1]
    validate_equity_inputs(historical_data["commonStockSharesOutstanding"].iloc[-1], total_debt, historical_data["cashAndCashEquivalents"].iloc[-1])
    equity_value = calculate_equity_value(enterprise_value, historical_data)
    intrinsic_value_per_share = calculate_intrinsic_value_per_share(
        equity_value, historical_data
    )

    print(f"Enterprise Value: {enterprise_value}")
    print(f"Terminal Value: {terminal_value}")
    print(f"Equity Value: {equity_value}")
    print(f"Intrinsic Value per Share: {intrinsic_value_per_share}")

    summary_path = outputs_dir / f"{ticker}_valuation_summary.txt"
    with open(summary_path, "w", encoding="utf-8") as summary_file:
        summary_file.write(
            "Enterprise Value: {enterprise_value}\n".format(
                enterprise_value=enterprise_value
            )
        )
        summary_file.write(
            "Terminal Value: {terminal_value}\n".format(
                terminal_value=terminal_value
            )
        )
        summary_file.write(
            "Equity Value: {equity_value}\n".format(
                equity_value=equity_value
            )
        )
        summary_file.write(
            "Intrinsic Value per Share: {intrinsic_value_per_share}\n".format(
                intrinsic_value_per_share=intrinsic_value_per_share
            )
        )

    print(f"Saved outputs to {outputs_dir}")
