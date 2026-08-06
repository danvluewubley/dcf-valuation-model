from pathlib import Path


def ensure_directories(project_root: Path, ticker: str) -> tuple[Path, Path]:
    """Create and return the data and outputs directories for a ticker."""
    output_dir = project_root / "data" / ticker
    outputs_dir = project_root / "outputs" / ticker
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs_dir.mkdir(parents=True, exist_ok=True)
    return output_dir, outputs_dir


def extract_market_inputs(latest_data: dict) -> tuple[float, float, float]:
    """Extract market input values from latest stock and balance sheet data."""
    shares_outstanding = float(latest_data.get("commonStockSharesOutstanding", 0.0))
    total_debt = float(
        latest_data.get("shortTermDebt", 0.0)
        + latest_data.get("longTermDebt", 0.0)
    )
    cash = float(latest_data.get("cashAndCashEquivalents", 0.0))

    if shares_outstanding <= 0:
        raise ValueError("Shares outstanding must be greater than zero.")

    if total_debt < 0:
        raise ValueError("Total debt cannot be negative.")

    if cash < 0:
        raise ValueError("Cash cannot be negative.")

    return shares_outstanding, total_debt, cash


def calculate_market_enterprise_value(
    stock_price: float,
    shares_outstanding: float,
    total_debt: float,
    cash: float,
) -> float:
    """Calculate the market enterprise value from stock price, shares, debt, and cash."""
    market_equity_value = stock_price * shares_outstanding
    return market_equity_value + total_debt - cash
