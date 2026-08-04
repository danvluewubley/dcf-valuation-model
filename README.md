# Automated DCF Valuation Model

A Python-based equity valuation tool that retrieves financial statement data, builds five-year operating forecasts, calculates unlevered free cash flow, and estimates a company's intrinsic value using discounted cash flow analysis.

Version 2 expands the original model with bull, base, and bear scenarios, a reverse DCF solver, input validation, automated testing, and reusable valuation modules.

## Features

### Standard DCF Valuation

* Retrieves annual financial statements from Alpha Vantage
* Builds and caches a standardized historical financial dataset
* Calculates historical operating and valuation metrics
* Produces five-year financial forecasts
* Calculates NOPAT and unlevered free cash flow
* Discounts projected cash flows using WACC
* Calculates terminal value using the perpetual-growth method
* Converts enterprise value to equity value
* Calculates intrinsic value per share

### Scenario Analysis

The model runs three predefined valuation scenarios:

* **Bear case:** Slower revenue growth, lower margins, higher WACC, and lower terminal growth
* **Base case:** Central operating and valuation assumptions
* **Bull case:** Stronger growth, margin expansion, lower WACC, and higher terminal growth

Each scenario produces:

* Forecasted financial data
* Enterprise value
* Terminal value
* Equity value
* Intrinsic value per share

### Reverse DCF

The reverse DCF estimates the revenue growth assumptions implied by the company's current market valuation.

The model:

1. Retrieves the latest available closing stock price
2. Calculates market equity value
3. Converts market equity value to market enterprise value
4. Holds operating margin, tax rate, capital intensity, WACC, and terminal growth constant
5. Uses binary search to solve for the starting revenue growth rate that causes the calculated enterprise value to match the market enterprise value
6. Applies a declining annual growth path using a configurable fade rate

Example output:

```text
Reverse DCF Results
Ticker: AAPL
Current Stock Price: $303.42
Market Enterprise Value: $4,617,565,163,740.00

Market-Implied Revenue Growth
Year 1: 38.69%
Year 2: 34.82%
Year 3: 31.34%
Year 4: 28.21%
Year 5: 25.38%

Fixed Assumptions
Operating Margin: [31.0%, 31.2%, 31.5%, 31.7%, 32.0%]
WACC: 10.91%
Terminal Growth Rate: 2.50%

Model Error: -$349.5 million
Relative Error: 0.0076%
Solver Status: Converged
```

## Valuation Methodology

### Revenue Forecast

Revenue is forecast by applying annual growth assumptions to the previous year's revenue:

```text
Forecast Revenue = Previous-Year Revenue × (1 + Revenue Growth Rate)
```

### NOPAT

```text
NOPAT = Operating Income × (1 − Tax Rate)
```

### Unlevered Free Cash Flow

```text
UFCF = NOPAT
     + Depreciation and Amortization
     − Capital Expenditures
     − Change in Operating Net Working Capital
```

### Terminal Value

The model uses the perpetual-growth method:

```text
Terminal Value =
Final-Year UFCF × (1 + Terminal Growth Rate)
────────────────────────────────────────────
WACC − Terminal Growth Rate
```

### Enterprise Value

```text
Enterprise Value =
Present Value of Forecast UFCF
+ Present Value of Terminal Value
```

### Equity Value

```text
Equity Value =
Enterprise Value
− Total Debt
+ Cash and Cash Equivalents
```

### Intrinsic Value Per Share

```text
Intrinsic Value Per Share =
Equity Value
────────────
Shares Outstanding
```

## Project Structure

```text
dcf-valuation-model/
├── main.py
├── requirements.txt
├── README.md
├── .env
├── data/
│   └── TICKER/
├── outputs/
│   └── TICKER/
├── model/
│   ├── assumptions.py
│   ├── data.py
│   ├── forecast.py
│   ├── orchestrator.py
│   ├── reverse_dcf.py
│   ├── reverse_dcf_support/
│   ├── validation.py
│   └── valuation.py
└── tests/
```

### Module Responsibilities

| Module                       | Responsibility                                                                         |
| ---------------------------- | -------------------------------------------------------------------------------------- |
| `main.py`                    | Parses command-line arguments and selects the standard or reverse DCF workflow         |
| `model/data.py`              | Downloads, loads, cleans, and combines financial statement data                        |
| `model/assumptions.py`       | Stores historical, custom, bull, base, and bear forecast assumptions                   |
| `model/forecast.py`          | Produces financial forecasts and calculates UFCF                                       |
| `model/valuation.py`         | Calculates enterprise value, equity value, and intrinsic value per share               |
| `model/orchestrator.py`      | Coordinates standard DCF and scenario analysis                                         |
| `model/reverse_dcf.py`       | Coordinates the reverse DCF workflow                                                   |
| `model/reverse_dcf_support/` | Handles market-data caching, market-value calculations, solving, and output formatting |
| `model/validation.py`        | Validates historical data, assumptions, and equity-value inputs                        |
| `tests/`                     | Contains automated tests for core model calculations and validation                    |

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/danvluewubley/dcf-valuation-model.git
cd dcf-valuation-model
```

### 2. Create a virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the Alpha Vantage API key

Create a `.env` file in the project root:

```env
ALPHA_VANTAGE_API_KEY=your_api_key_here
```

Do not commit the `.env` file or expose the API key publicly.

## Usage

### Run the standard DCF and scenario analysis

```bash
python main.py AAPL
```

A ticker can be supplied for another supported public company:

```bash
python main.py TSLA
```

If no ticker is provided, the program defaults to `AAPL`.

### Run the reverse DCF

```bash
python main.py AAPL --reverse
```

Example:

```bash
python main.py TSLA --reverse
```

## Output Files

The program stores downloaded data and generated results in ticker-specific directories.

```text
data/
└── AAPL/
    ├── income_statement.csv
    ├── balance_sheet.csv
    ├── cash_flow.csv
    └── stock_price.json

outputs/
└── AAPL/
    ├── AAPL_historical_data.csv
    ├── forecast_data/
    │   ├── AAPL_forecasted_data_bear.csv
    │   ├── AAPL_forecasted_data_base.csv
    │   └── AAPL_forecasted_data_bull.csv
    └── valuation_summaries/
        ├── AAPL_valuation_summary_bear.txt
        ├── AAPL_valuation_summary_base.txt
        └── AAPL_valuation_summary_bull.txt
```

Cached data reduces unnecessary API requests and helps the program operate within Alpha Vantage request limits.

## Validation

Before completing a valuation, the program checks for:

* Missing historical financial fields
* Invalid or duplicate fiscal dates
* Missing or nonnumeric financial values
* Zero or negative revenue
* Zero or negative shares outstanding
* Negative debt or cash balances
* Missing forecast assumptions
* Invalid forecast periods
* Negative capital expenditure assumptions
* Invalid WACC values
* Terminal growth greater than or equal to WACC

The model raises a descriptive error when an input fails validation instead of producing an unreliable valuation.

## Testing

The project uses `pytest` for automated testing.

Run the full test suite with:

```bash
pytest
```

For more detailed output:

```bash
pytest -v
```

The tests are designed to verify core calculations and protect the valuation engine from regressions as new features are added.

## Example Scenario Results

Example Apple valuation output:

| Scenario | Enterprise Value |    Equity Value | Intrinsic Value Per Share |
| -------- | ---------------: | --------------: | ------------------------: |
| Bear     |  $1.059 trillion | $0.994 trillion |                    $66.23 |
| Base     |  $1.509 trillion | $1.444 trillion |                    $96.26 |
| Bull     |  $2.033 trillion | $1.968 trillion |                   $131.19 |

These values are model outputs based on the included assumptions and should not be interpreted as investment recommendations.

## V2 Improvements

Version 2 adds:

* Year-specific forecast assumptions
* Bull, base, and bear scenario analysis
* Reverse DCF analysis
* Binary-search optimization for market-implied growth
* Daily stock-price caching
* Historical-data caching
* Historical-data validation
* Forecast-assumption validation
* Valuation-assumption validation
* Equity-input validation
* Automated unit tests
* Expanded command-line functionality
* Modular reverse DCF support functions

## Limitations

* Forecast results are highly sensitive to WACC, terminal growth, revenue growth, and operating-margin assumptions.
* Financial statement field availability and definitions may vary across companies.
* The model relies on Alpha Vantage data and is subject to its coverage and request limits.
* Scenario assumptions are predefined and may not reflect current analyst consensus.
* The reverse DCF currently solves for revenue growth while holding the other major assumptions constant.
* The model does not currently include segment-level forecasting, comparable-company analysis, precedent transactions, or Monte Carlo simulation.
* Current market prices may be loaded from cached data when the API request limit has been reached.

## Planned Enhancements

* Historical-versus-forecast charts
* UFCF visualization
* Scenario comparison charts
* WACC and terminal-growth sensitivity heatmap
* Reverse DCF growth comparison chart
* Formatted Excel valuation report
* Improved interactive command-line interface
* Additional reverse DCF solve variables
* Automated documentation and release workflow

## Disclaimer

This project is intended for educational and portfolio purposes only. It does not constitute investment advice, a recommendation to buy or sell securities, or a substitute for independent financial research.

## Author

**Daniel Wu**

Finance student and developer interested in valuation, financial modeling, data analysis, and investment research.
