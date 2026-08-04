import os
from pathlib import Path
from typing import List, Tuple

import pandas as pd
import requests

STATEMENTS = ["INCOME_STATEMENT", "BALANCE_SHEET", "CASH_FLOW"]


def require_api_key() -> str:
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Missing ALPHA_VANTAGE_API_KEY. Set it in your .env file or environment variables."
        )
    return api_key


def download_financial_statements(ticker: str, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    api_key = require_api_key()

    for statement in STATEMENTS:
        csv_path = output_dir / f"{ticker}_{statement}.csv"
        if csv_path.exists():
            print(f"Using cached {statement}.")
            continue

        response = requests.get(
            "https://www.alphavantage.co/query",
            params={
                "function": statement,
                "symbol": ticker,
                "apikey": api_key,
            },
            timeout=30,
        )
        response.raise_for_status()

        payload = response.json()
        annual_reports = payload.get("annualReports")
        if annual_reports is None:
            raise ValueError(
                f"Alpha Vantage response missing annualReports for {statement}: {payload}"
            )

        pd.DataFrame(annual_reports).to_csv(csv_path, index=False)
        print(f"Downloaded {statement}.")


def load_financial_statements(
    ticker: str, output_dir: Path
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    return (
        pd.read_csv(output_dir / f"{ticker}_INCOME_STATEMENT.csv"),
        pd.read_csv(output_dir / f"{ticker}_BALANCE_SHEET.csv"),
        pd.read_csv(output_dir / f"{ticker}_CASH_FLOW.csv"),
    )


def extract_float_column(
    df: pd.DataFrame, candidates: List[str], name: str
) -> pd.Series:
    for candidate in candidates:
        if candidate in df.columns:
            return pd.to_numeric(df[candidate], errors="coerce")
    raise KeyError(
        f"Required column {name} not found. Tried {candidates} in {list(df.columns)}."
    )


def build_historical_dataset(
    income_statement: pd.DataFrame,
    balance_sheet: pd.DataFrame,
    cash_flow: pd.DataFrame,
) -> pd.DataFrame:
    financial_data = pd.merge(
        income_statement,
        balance_sheet,
        on="fiscalDateEnding",
        suffixes=("_income", "_balance"),
    )
    financial_data = pd.merge(
        financial_data,
        cash_flow,
        on="fiscalDateEnding",
        suffixes=("", "_cashflow"),
    )

    return pd.DataFrame(
        {
            "fiscalDateEnding": financial_data["fiscalDateEnding"],
            "totalRevenue": extract_float_column(
                financial_data, ["totalRevenue"], "totalRevenue"
            ),
            "operatingIncome": extract_float_column(
                financial_data, ["operatingIncome"], "operatingIncome"
            ),
            "incomeTaxExpense": extract_float_column(
                financial_data, ["incomeTaxExpense"], "incomeTaxExpense"
            ),
            "incomeBeforeTax": extract_float_column(
                financial_data, ["incomeBeforeTax"], "incomeBeforeTax"
            ),
            "nopat": extract_float_column(
                financial_data, ["netIncome"], "netIncome"
            ),
            "depreciationAndAmortization": extract_float_column(
                financial_data,
                ["depreciationAndAmortization"],
                "depreciationAndAmortization",
            ),
            "capitalExpenditures": extract_float_column(
                financial_data,
                ["capitalExpenditures"],
                "capitalExpenditures",
            ),
            "cashAndCashEquivalents": extract_float_column(
                financial_data,
                ["cashAndCashEquivalentsAtCarryingValue", "cashAndCashEquivalents"],
                "cashAndCashEquivalents",
            ),
            "shortTermDebt": extract_float_column(
                financial_data, ["shortTermDebt"], "shortTermDebt"
            ),
            "longTermDebt": extract_float_column(
                financial_data, ["longTermDebt"], "longTermDebt"
            ),
            "totalCurrentAssets": extract_float_column(
                financial_data, ["totalCurrentAssets"], "totalCurrentAssets"
            ),
            "totalCurrentLiabilities": extract_float_column(
                financial_data,
                ["totalCurrentLiabilities"],
                "totalCurrentLiabilities",
            ),
            "commonStockSharesOutstanding": extract_float_column(
                financial_data,
                ["commonStockSharesOutstanding"],
                "commonStockSharesOutstanding",
            ),
            "accountsReceivable": extract_float_column(
                financial_data,
                ["currentNetReceivables", "accountsReceivable"],
                "accountsReceivable",
            ),
            "inventory": extract_float_column(financial_data, ["inventory"], "inventory"),
            "accountsPayable": extract_float_column(
                financial_data,
                ["currentAccountsPayable", "currentAccountsPayables", "accountsPayable"],
                "accountsPayable",
            ),
            "otherOperatingCurrentAssets": extract_float_column(
                financial_data,
                ["otherCurrentAssets", "otherOperatingCurrentAssets"],
                "otherOperatingCurrentAssets",
            ),
            "otherOperatingCurrentLiabilities": extract_float_column(
                financial_data,
                ["otherCurrentLiabilities", "otherOperatingCurrentLiabilities"],
                "otherOperatingCurrentLiabilities",
            ),
        }
    )


def validate_historical_data(historical_data: pd.DataFrame) -> pd.DataFrame:
    required_columns = [
        "fiscalDateEnding",
        "totalRevenue",
        "operatingIncome",
        "incomeTaxExpense",
        "incomeBeforeTax",
        "nopat",
        "depreciationAndAmortization",
        "capitalExpenditures",
        "cashAndCashEquivalents",
        "shortTermDebt",
        "longTermDebt",
        "totalCurrentAssets",
        "totalCurrentLiabilities",
        "commonStockSharesOutstanding",
        "accountsReceivable",
        "inventory",
        "accountsPayable",
        "otherOperatingCurrentAssets",
        "otherOperatingCurrentLiabilities",
    ]

    errors: List[str] = []

    if historical_data.empty:
        errors.append("Historical dataset is empty.")

    missing_columns = [
        column
        for column in required_columns
        if column not in historical_data.columns
    ]
    if missing_columns:
        errors.append(f"Missing columns: {missing_columns}")

    historical_data = historical_data.copy()
    historical_data["fiscalDateEnding"] = pd.to_datetime(
        historical_data["fiscalDateEnding"], errors="coerce"
    )
    if historical_data["fiscalDateEnding"].isna().any():
        errors.append("One or more fiscal dates are invalid.")

    if historical_data["fiscalDateEnding"].duplicated().any():
        duplicate_dates = historical_data.loc[
            historical_data["fiscalDateEnding"].duplicated(), "fiscalDateEnding"
        ].tolist()
        errors.append(f"Duplicate fiscal dates: {duplicate_dates}")

    numeric_columns = [column for column in required_columns if column != "fiscalDateEnding"]
    for column in numeric_columns:
        if column in historical_data.columns:
            if not pd.api.types.is_numeric_dtype(historical_data[column]):
                errors.append(f"{column} is not numeric.")
            if historical_data[column].isna().any():
                missing_dates = historical_data.loc[
                    historical_data[column].isna(), "fiscalDateEnding"
                ].tolist()
                errors.append(
                    f"{column} contains missing values for {missing_dates}."
                )

    for column in [
        "totalRevenue",
        "commonStockSharesOutstanding",
        "totalCurrentAssets",
    ]:
        if column in historical_data.columns and (historical_data[column] <= 0).any():
            errors.append(f"{column} contains zero or negative values.")

    for column in [
        "cashAndCashEquivalents",
        "shortTermDebt",
        "longTermDebt",
        "totalCurrentLiabilities",
    ]:
        if column in historical_data.columns and (historical_data[column] < 0).any():
            errors.append(f"{column} contains negative values.")

    if errors:
        raise ValueError("Historical data validation failed:\n- " + "\n- ".join(errors))

    print("Historical data validation passed.")
    return historical_data
