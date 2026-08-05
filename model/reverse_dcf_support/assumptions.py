from model.forecast import calculate_ufcf, forecast_financials
from model.valuation import calculate_enterprise_value
from copy import deepcopy


def build_default_reverse_dcf_assumptions(
    forecast_years: int = 5,
    starting_growth_rate: float = 0.20,
    fade_rate: float = 0.90,
) -> dict:
    return {
        "forecast_years": forecast_years,
        "forecast": {
            "revenue_growth_rate": [
                starting_growth_rate * (fade_rate ** i)
                for i in range(forecast_years)
            ],
            "operating_margin": [0.310, 0.312, 0.315, 0.317, 0.320],
            "tax_rate": [0.16] * forecast_years,
            "daPercentRevenue": [0.029, 0.029, 0.0285, 0.028, 0.028],
            "capexPercentRevenue": [0.031, 0.030, 0.030, 0.029, 0.029],
            "nwcPercentRevenue": [
                -0.140,
                -0.140,
                -0.139,
                -0.138,
                -0.138,
            ],
        },
        "valuation": {
            "WACC": 0.1091,
            "terminal_growth_rate": 0.025,
        },
    }

def build_operating_margin_reverse_dcf_assumptions(
    forecast_years: int = 5,
    starting_operating_margin: float = 0.30,
    fade_rate: float = 0.90,
) -> dict:
    return {
        "forecast_years": forecast_years,
        "forecast": {
            "revenue_growth_rate": [0.06, 0.055, 0.05, 0.04, 0.03],
            "operating_margin": [
                starting_operating_margin * (fade_rate ** i)
                for i in range(forecast_years)
            ],
            "tax_rate": [0.16] * forecast_years,
            "daPercentRevenue": [0.029, 0.029, 0.0285, 0.028, 0.028],
            "capexPercentRevenue": [0.031, 0.030, 0.030, 0.029, 0.029],
            "nwcPercentRevenue": [
                -0.140,
                -0.140,
                -0.139,
                -0.138,
                -0.138,
            ],
        },
        "valuation": {
            "WACC": 0.1091,
            "terminal_growth_rate": 0.025,
        },
    }


def get_recent_historical_data(historical_data, years: int = 5):
    return (
        historical_data.sort_values("fiscalDateEnding")
        .tail(years)
        .reset_index(drop=True)
    )


def find_implied_starting_growth_rate(
    historical_data,
    market_enterprise_value: float,
    forecast_assumptions: dict,
    fade_rate: float = 0.90,
    tolerance: float = 0.0001,
    max_iterations: int = 100,
) -> tuple[float, float, float, float, int, dict]:
    low_growth = 0.0
    high_growth = 1.0
    implied_growth_rate = forecast_assumptions["forecast"]["revenue_growth_rate"][0]
    forecasted_data = None
    enterprise_value = 0.0
    difference = 0.0

    for iteration in range(max_iterations):
        implied_growth_rate = (low_growth + high_growth) / 2
        forecast_assumptions["forecast"]["revenue_growth_rate"] = [
            implied_growth_rate * (fade_rate ** i)
            for i in range(forecast_assumptions["forecast_years"])
        ]

        forecasted_data = forecast_financials(historical_data, forecast_assumptions)
        forecasted_data = calculate_ufcf(
            forecasted_data,
            historical_data["operatingNetWorkingCapital"].iloc[-1],
        )

        enterprise_value, _ = calculate_enterprise_value(
            forecasted_data,
            forecast_assumptions,
        )

        difference = enterprise_value - market_enterprise_value
        relative_error = abs(difference) / market_enterprise_value

        if relative_error <= tolerance:
            break

        if difference < 0:
            low_growth = implied_growth_rate
        else:
            high_growth = implied_growth_rate

    return (
        implied_growth_rate,
        enterprise_value,
        difference,
        abs(difference) / market_enterprise_value,
        iteration + 1,
        forecasted_data,
    )


def find_implied_starting_operating_margin(
    historical_data,
    market_enterprise_value: float,
    forecast_assumptions: dict,
    fade_rate: float = 0.90,
    tolerance: float = 0.0001,
    max_iterations: int = 100,
) -> tuple[float, float, float, float, int, dict]:
    low_margin = 0.0
    high_margin = 0.70

    working_assumptions = deepcopy(forecast_assumptions)

    implied_operating_margin = (
        working_assumptions["forecast"]["operating_margin"][0]
    )
    forecasted_data = None
    enterprise_value = 0.0
    difference = 0.0

    # Test whether the target EV is achievable at the maximum margin.
    working_assumptions["forecast"]["operating_margin"] = [
        high_margin * (fade_rate**i)
        for i in range(working_assumptions["forecast_years"])
    ]

    test_data = forecast_financials(
        historical_data,
        working_assumptions,
    )
    test_data = calculate_ufcf(test_data)

    maximum_enterprise_value, _ = calculate_enterprise_value(
        test_data,
        working_assumptions,
    )

    if maximum_enterprise_value < market_enterprise_value:
        raise ValueError(
            "No feasible operating margin found. "
            f"A {high_margin:.1%} starting operating margin produces an "
            f"enterprise value of ${maximum_enterprise_value:,.2f}, "
            f"below the target of ${market_enterprise_value:,.2f}."
        )

    for iteration in range(1, max_iterations + 1):
        implied_operating_margin = (low_margin + high_margin) / 2

        working_assumptions["forecast"]["operating_margin"] = [
            implied_operating_margin * (fade_rate**i)
            for i in range(working_assumptions["forecast_years"])
        ]

        forecasted_data = forecast_financials(
            historical_data,
            working_assumptions,
        )
        forecasted_data = calculate_ufcf(forecasted_data)

        enterprise_value, _ = calculate_enterprise_value(
            forecasted_data,
            working_assumptions,
        )

        difference = enterprise_value - market_enterprise_value
        relative_error = abs(difference) / market_enterprise_value

        if relative_error <= tolerance:
            break

        if difference < 0:
            low_margin = implied_operating_margin
        else:
            high_margin = implied_operating_margin

    return (
        implied_operating_margin,
        enterprise_value,
        difference,
        abs(difference) / market_enterprise_value,
        iteration,
        forecasted_data,
    )