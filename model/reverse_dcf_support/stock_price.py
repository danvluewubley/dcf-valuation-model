from datetime import date
import json
from pathlib import Path

import dotenv
import requests


def get_alpha_vantage_api_key() -> str:
    api_key = dotenv.get_key(dotenv.find_dotenv(), "ALPHA_VANTAGE_API_KEY")
    if not api_key:
        raise ValueError("ALPHA_VANTAGE_API_KEY was not found in the .env file.")
    return api_key


def load_stock_price_cache(cache_path: Path, allow_stale: bool = False) -> dict | None:
    if not cache_path.exists():
        return None

    try:
        with cache_path.open("r", encoding="utf-8") as file:
            cached_data = json.load(file)

        if "api_response" in cached_data:
            if cached_data.get("cached_date") == date.today().isoformat() or allow_stale:
                print(f"Loading {cache_path.stem} from cache...")
                return cached_data["api_response"]
            return None

        if "Time Series (Daily)" in cached_data:
            print(f"Loading {cache_path.stem} from legacy cache (wrapping)...")
            wrapped = {
                "cached_date": date.today().isoformat(),
                "ticker": cache_path.parent.name,
                "api_response": cached_data,
            }
            with cache_path.open("w", encoding="utf-8") as file:
                json.dump(wrapped, file, indent=4)
            return cached_data
    except (json.JSONDecodeError, KeyError, TypeError):
        print("Invalid stock-price cache. Downloading fresh data...")

    return None


def save_stock_price_cache(cache_path: Path, stock_price_data: dict) -> None:
    cache_contents = {
        "cached_date": date.today().isoformat(),
        "ticker": cache_path.parent.name,
        "api_response": stock_price_data,
    }
    with cache_path.open("w", encoding="utf-8") as file:
        json.dump(cache_contents, file, indent=4)


def download_stock_price_data(ticker: str, api_key: str) -> dict:
    response = requests.get(
        "https://www.alphavantage.co/query",
        params={
            "function": "TIME_SERIES_DAILY",
            "symbol": ticker,
            "apikey": api_key,
        },
        timeout=30,
    )
    response.raise_for_status()

    stock_price_data = response.json()

    if "Error Message" in stock_price_data:
        raise ValueError(
            f"Alpha Vantage returned an error for {ticker}: "
            f"{stock_price_data['Error Message']}"
        )

    if "Note" in stock_price_data:
        raise RuntimeError(
            f"Alpha Vantage API limit reached: "
            f"{stock_price_data['Note']}"
        )

    if "Information" in stock_price_data:
        raise RuntimeError(
            f"Alpha Vantage message: "
            f"{stock_price_data['Information']}"
        )

    if "Time Series (Daily)" not in stock_price_data:
        raise ValueError(
            f"No daily stock-price data returned for {ticker}."
        )

    return stock_price_data


def get_stock_price_data(
    ticker: str,
    api_key: str,
    output_dir: Path,
) -> dict:
    cache_path = output_dir / "stock_price.json"
    cached_data = load_stock_price_cache(cache_path)
    if cached_data is not None:
        return cached_data

    print(f"Downloading {ticker} stock price...")
    try:
        stock_price_data = download_stock_price_data(ticker, api_key)
        save_stock_price_cache(cache_path, stock_price_data)
        return stock_price_data
    except RuntimeError as exc:
        if "API limit" in str(exc) or "message" in str(exc):
            print(
                "Rate limit or API informational response encountered; "
                "falling back to cached stock-price data if available."
            )
            fallback_data = load_stock_price_cache(cache_path, allow_stale=True)
            if fallback_data is not None:
                return fallback_data
        raise


def get_latest_stock_price(stock_price_data: dict) -> float:
    daily_prices = stock_price_data["Time Series (Daily)"]
    latest_date = max(daily_prices.keys())
    latest_close = daily_prices[latest_date]["4. close"]
    return float(latest_close)
