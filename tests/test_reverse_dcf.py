import pytest
import pandas as pd

from model.forecast import calculate_ufcf, forecast_financials
from model.valuation import calculate_dcf_metrics, calculate_enterprise_value
from model.reverse_dcf_support import (
    build_default_reverse_dcf_assumptions,
    build_operating_margin_reverse_dcf_assumptions,
    calculate_market_enterprise_value,
    extract_market_inputs,
    find_implied_starting_growth_rate,
    find_implied_starting_operating_margin,
    get_recent_historical_data,
)


@pytest.fixture
def reverse_dcf_historical_data():
    return pd.DataFrame(
        [
            {
                "fiscalDateEnding": "2018-12-31",
                "totalRevenue": 100.0,
                "operatingIncome": 20.0,
                "incomeTaxExpense": 4.0,
                "incomeBeforeTax": 20.0,
                "depreciationAndAmortization": 10.0,
                "capitalExpenditures": 5.0,
                "accountsReceivable": 10.0,
                "inventory": 5.0,
                "otherOperatingCurrentAssets": 2.0,
                "accountsPayable": 3.0,
                "otherOperatingCurrentLiabilities": 1.0,
                "shortTermDebt": 5.0,
                "longTermDebt": 10.0,
                "cashAndCashEquivalents": 2.0,
                "commonStockSharesOutstanding": 2.0,
            },
            {
                "fiscalDateEnding": "2019-12-31",
                "totalRevenue": 110.0,
                "operatingIncome": 22.0,
                "incomeTaxExpense": 4.4,
                "incomeBeforeTax": 22.0,
                "depreciationAndAmortization": 11.0,
                "capitalExpenditures": 5.5,
                "accountsReceivable": 11.0,
                "inventory": 5.5,
                "otherOperatingCurrentAssets": 2.2,
                "accountsPayable": 3.3,
                "otherOperatingCurrentLiabilities": 1.1,
                "shortTermDebt": 5.0,
                "longTermDebt": 10.0,
                "cashAndCashEquivalents": 2.0,
                "commonStockSharesOutstanding": 2.0,
            },
            {
                "fiscalDateEnding": "2020-12-31",
                "totalRevenue": 121.0,
                "operatingIncome": 24.2,
                "incomeTaxExpense": 4.84,
                "incomeBeforeTax": 24.2,
                "depreciationAndAmortization": 12.1,
                "capitalExpenditures": 6.05,
                "accountsReceivable": 12.1,
                "inventory": 6.05,
                "otherOperatingCurrentAssets": 2.42,
                "accountsPayable": 3.63,
                "otherOperatingCurrentLiabilities": 1.21,
                "shortTermDebt": 5.0,
                "longTermDebt": 10.0,
                "cashAndCashEquivalents": 2.0,
                "commonStockSharesOutstanding": 2.0,
            },
            {
                "fiscalDateEnding": "2021-12-31",
                "totalRevenue": 133.1,
                "operatingIncome": 26.62,
                "incomeTaxExpense": 5.324,
                "incomeBeforeTax": 26.62,
                "depreciationAndAmortization": 13.31,
                "capitalExpenditures": 6.655,
                "accountsReceivable": 13.31,
                "inventory": 6.655,
                "otherOperatingCurrentAssets": 2.662,
                "accountsPayable": 3.993,
                "otherOperatingCurrentLiabilities": 1.331,
                "shortTermDebt": 5.0,
                "longTermDebt": 10.0,
                "cashAndCashEquivalents": 2.0,
                "commonStockSharesOutstanding": 2.0,
            },
            {
                "fiscalDateEnding": "2022-12-31",
                "totalRevenue": 146.41,
                "operatingIncome": 29.282,
                "incomeTaxExpense": 5.8564,
                "incomeBeforeTax": 29.282,
                "depreciationAndAmortization": 14.641,
                "capitalExpenditures": 7.3205,
                "accountsReceivable": 14.641,
                "inventory": 7.3205,
                "otherOperatingCurrentAssets": 2.9282,
                "accountsPayable": 4.1783,
                "otherOperatingCurrentLiabilities": 1.4641,
                "shortTermDebt": 5.0,
                "longTermDebt": 10.0,
                "cashAndCashEquivalents": 2.0,
                "commonStockSharesOutstanding": 2.0,
            },
            {
                "fiscalDateEnding": "2023-12-31",
                "totalRevenue": 161.051,
                "operatingIncome": 32.2102,
                "incomeTaxExpense": 6.44204,
                "incomeBeforeTax": 32.2102,
                "depreciationAndAmortization": 16.1051,
                "capitalExpenditures": 8.05255,
                "accountsReceivable": 16.1051,
                "inventory": 8.05255,
                "otherOperatingCurrentAssets": 3.22102,
                "accountsPayable": 4.83153,
                "otherOperatingCurrentLiabilities": 1.61051,
                "shortTermDebt": 5.0,
                "longTermDebt": 10.0,
                "cashAndCashEquivalents": 2.0,
                "commonStockSharesOutstanding": 2.0,
            },
        ]
    )


def test_build_default_reverse_dcf_assumptions_contains_expected_fields():
    assumptions = build_default_reverse_dcf_assumptions(
        forecast_years=5,
        starting_growth_rate=0.10,
        fade_rate=0.90,
    )

    assert assumptions["forecast_years"] == 5
    assert len(assumptions["forecast"]["revenue_growth_rate"]) == 5
    assert assumptions["forecast"]["revenue_growth_rate"][0] == pytest.approx(0.10)
    assert assumptions["forecast"]["revenue_growth_rate"][1] == pytest.approx(0.09)
    assert assumptions["valuation"]["WACC"] == pytest.approx(0.1091)


def test_build_operating_margin_reverse_dcf_assumptions_contains_expected_fields():
    assumptions = build_operating_margin_reverse_dcf_assumptions(
        forecast_years=5,
        starting_operating_margin=0.30,
        fade_rate=0.90,
    )

    assert assumptions["forecast_years"] == 5
    assert assumptions["forecast"]["operating_margin"][0] == pytest.approx(0.30)
    assert assumptions["forecast"]["operating_margin"][1] == pytest.approx(0.27)
    assert assumptions["forecast"]["revenue_growth_rate"][0] == pytest.approx(0.06)


def test_extract_market_inputs_validates_and_returns_values():
    latest_data = {
        "commonStockSharesOutstanding": 4,
        "shortTermDebt": 6,
        "longTermDebt": 4,
        "cashAndCashEquivalents": 1,
    }

    shares, debt, cash = extract_market_inputs(latest_data)

    assert shares == pytest.approx(4.0)
    assert debt == pytest.approx(10.0)
    assert cash == pytest.approx(1.0)


def test_extract_market_inputs_raises_for_invalid_values():
    with pytest.raises(ValueError, match="Shares outstanding must be greater than zero"):
        extract_market_inputs({"commonStockSharesOutstanding": 0})

    with pytest.raises(ValueError, match="Total debt cannot be negative"):
        extract_market_inputs({"commonStockSharesOutstanding": 1, "shortTermDebt": -1, "longTermDebt": 0})

    with pytest.raises(ValueError, match="Cash cannot be negative"):
        extract_market_inputs({"commonStockSharesOutstanding": 1, "cashAndCashEquivalents": -5})


def test_calculate_market_enterprise_value():
    market_ev = calculate_market_enterprise_value(
        stock_price=50.0,
        shares_outstanding=10.0,
        total_debt=5.0,
        cash=2.0,
    )

    assert market_ev == pytest.approx(503.0)


def test_get_recent_historical_data_returns_last_n_years(reverse_dcf_historical_data):
    data = reverse_dcf_historical_data.sample(frac=1, random_state=1).reset_index(drop=True)
    recent = get_recent_historical_data(data, years=3)

    assert len(recent) == 3
    assert recent["fiscalDateEnding"].tolist() == [
        "2021-12-31",
        "2022-12-31",
        "2023-12-31",
    ]


def test_find_implied_starting_growth_rate_finds_known_value(reverse_dcf_historical_data):
    metrics = calculate_dcf_metrics(reverse_dcf_historical_data)
    recent = get_recent_historical_data(metrics, years=5)

    base_assumptions = build_default_reverse_dcf_assumptions(
        forecast_years=5,
        starting_growth_rate=0.05,
        fade_rate=0.90,
    )
    forecasted = forecast_financials(recent, base_assumptions)
    forecasted = calculate_ufcf(forecasted, recent["operatingNetWorkingCapital"].iloc[-1])
    target_ev, _ = calculate_enterprise_value(forecasted, base_assumptions)

    assumptions_for_search = build_default_reverse_dcf_assumptions(
        forecast_years=5,
        starting_growth_rate=0.10,
        fade_rate=0.90,
    )

    implied_growth_rate, enterprise_value, difference, relative_error, iterations, forecasted_data = (
        find_implied_starting_growth_rate(
            recent,
            target_ev,
            assumptions_for_search,
            fade_rate=0.90,
            tolerance=1e-5,
            max_iterations=100,
        )
    )

    assert implied_growth_rate == pytest.approx(0.05, rel=1e-3)
    assert relative_error <= 1e-5
    assert iterations > 0
    assert "freeCashFlow" in forecasted_data.columns
    assert enterprise_value == pytest.approx(target_ev, rel=1e-5)


def test_find_implied_starting_operating_margin_finds_known_value(reverse_dcf_historical_data):
    metrics = calculate_dcf_metrics(reverse_dcf_historical_data)
    recent = get_recent_historical_data(metrics, years=5)

    base_assumptions = build_operating_margin_reverse_dcf_assumptions(
        forecast_years=5,
        starting_operating_margin=0.15,
        fade_rate=0.90,
    )
    forecasted = forecast_financials(recent, base_assumptions)
    forecasted = calculate_ufcf(forecasted)
    target_ev, _ = calculate_enterprise_value(forecasted, base_assumptions)

    assumptions_for_search = build_operating_margin_reverse_dcf_assumptions(
        forecast_years=5,
        starting_operating_margin=0.30,
        fade_rate=0.90,
    )

    implied_operating_margin, enterprise_value, difference, relative_error, iterations, forecasted_data = (
        find_implied_starting_operating_margin(
            recent,
            target_ev,
            assumptions_for_search,
            fade_rate=0.90,
            tolerance=1e-5,
            max_iterations=100,
        )
    )

    assert implied_operating_margin == pytest.approx(0.15, rel=1e-3)
    assert relative_error <= 1e-5
    assert iterations > 0
    assert "freeCashFlow" in forecasted_data.columns
    assert enterprise_value == pytest.approx(target_ev, rel=1e-5)


def test_find_implied_starting_operating_margin_raises_when_target_unachievable(reverse_dcf_historical_data):
    metrics = calculate_dcf_metrics(reverse_dcf_historical_data)
    recent = get_recent_historical_data(metrics, years=5)

    assumptions = build_operating_margin_reverse_dcf_assumptions(
        forecast_years=5,
        starting_operating_margin=0.30,
        fade_rate=0.90,
    )

    with pytest.raises(ValueError, match="No feasible operating margin found"):
        find_implied_starting_operating_margin(
            recent,
            market_enterprise_value=1_000_000_000.0,
            forecast_assumptions=assumptions,
            fade_rate=0.90,
            tolerance=1e-5,
            max_iterations=100,
        )
