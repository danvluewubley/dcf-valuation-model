from pathlib import Path

from model.data import (
    build_historical_dataset,
    download_financial_statements,
    load_financial_statements,
)
from model.reverse_dcf_support import (
    build_default_reverse_dcf_assumptions,
    calculate_market_enterprise_value,
    ensure_directories,
    extract_market_inputs,
    find_implied_starting_growth_rate,
    get_alpha_vantage_api_key,
    get_latest_stock_price,
    get_stock_price_data,
    get_recent_historical_data,
    print_reverse_dcf_results,
)


def run_reverse_dcf(ticker: str) -> None:
    ticker = ticker.upper()
    alpha_vantage_api_key = get_alpha_vantage_api_key()

    project_root = Path(__file__).parent.parent
    output_dir, outputs_dir = ensure_directories(project_root, ticker)

    download_financial_statements(ticker, output_dir)

    income_statement, balance_sheet, cash_flow = load_financial_statements(
        ticker,
        output_dir,
    )

    historical_data = build_historical_dataset(
        income_statement,
        balance_sheet,
        cash_flow,
    )

    if historical_data.empty:
        raise ValueError(
            f"No historical financial data was built for {ticker}."
        )

    stock_price_data = get_stock_price_data(ticker, alpha_vantage_api_key, output_dir)
    stock_price = get_latest_stock_price(stock_price_data)

    latest_data = historical_data.iloc[0].to_dict()
    shares_outstanding, total_debt, cash = extract_market_inputs(latest_data)
    market_enterprise_value = calculate_market_enterprise_value(
        stock_price,
        shares_outstanding,
        total_debt,
        cash,
    )

    forecast_years = 5
    fade_rate = 0.90
    tolerance = 0.0001
    max_iterations = 100

    forecast_assumptions = build_default_reverse_dcf_assumptions(
        forecast_years=forecast_years,
        starting_growth_rate=0.20,
        fade_rate=fade_rate,
    )

    recent_data = get_recent_historical_data(historical_data, years=forecast_years)

    (
        implied_growth_rate,
        enterprise_value,
        difference,
        relative_error,
        iterations,
        forecasted_data,
    ) = find_implied_starting_growth_rate(
        recent_data,
        market_enterprise_value,
        forecast_assumptions,
        fade_rate=fade_rate,
        tolerance=tolerance,
        max_iterations=max_iterations,
    )

    print_reverse_dcf_results(
        ticker=ticker,
        stock_price=stock_price,
        market_enterprise_value=market_enterprise_value,
        forecast_assumptions=forecast_assumptions,
        implied_growth_rate=implied_growth_rate,
        fade_rate=fade_rate,
        difference=difference,
        relative_error=relative_error,
        iterations=iterations,
        tolerance=tolerance,
    )
