def print_reverse_dcf_results(
    ticker: str,
    stock_price: float,
    market_enterprise_value: float,
    forecast_assumptions: dict,
    implied_growth_rate: float,
    fade_rate: float,
    difference: float,
    relative_error: float,
    iterations: int,
    tolerance: float,
) -> None:
    growth_rates = forecast_assumptions["forecast"]["revenue_growth_rate"]

    print("Reverse DCF results:")
    print(f"Ticker: {ticker}")
    print(f"Current Stock Price: ${stock_price:,.2f}")
    print(f"Market Enterprise Value: ${market_enterprise_value:,.2f}")
    print("Assumptions:")
    print(f"Starting revenue growth rate: {implied_growth_rate:.2%}")
    print(f"Fade rate: {fade_rate:.2%}")
    print(f"Ending revenue growth rate: {growth_rates[-1]:.2%}")
    print("Implied Revenue Growth:")
    for year_index, growth_rate in enumerate(growth_rates, start=1):
        print(f"Year {year_index}: {growth_rate:.2%}")

    print("Fixed assumptions:")
    print(f"Operating margin: {forecast_assumptions['forecast']['operating_margin']}")
    print(f"WACC: {forecast_assumptions['valuation']['WACC']:.2%}")
    print(
        f"Terminal growth rate: "
        f"{forecast_assumptions['valuation']['terminal_growth_rate']:.2%}"
    )
    print(f"Model Difference: ${difference:,.2f} ({relative_error:.4%})")
    print(f"Iterations: {iterations}")
    print(f"Converged: {relative_error <= tolerance}")
