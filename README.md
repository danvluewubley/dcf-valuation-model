# DCF Valuation Model

A Python-based discounted cash flow valuation tool that retrieves financial data, forecasts unlevered free cash flow, estimates intrinsic value, and performs scenario and reverse DCF analysis.

## Features

* Alpha Vantage financial-statement retrieval
* Five-year operating forecasts
* NOPAT and unlevered free cash flow calculations
* Enterprise value, equity value, and intrinsic value per share
* Bear, base, and bull scenarios
* Revenue-growth reverse DCF
* Operating-margin reverse DCF
* Reverse DCF feasibility checks
* Financial-data and stock-price caching
* Input validation
* Automated tests
* Command-line interface

## Valuation Methodology

The model calculates unlevered free cash flow as:

```text
UFCF
= NOPAT
+ Depreciation and Amortization
− Capital Expenditures
− Change in Operating Net Working Capital
```

Enterprise value is calculated as:

```text
Enterprise Value
= Present Value of Forecast-Period UFCF
+ Present Value of Terminal Value
```

Equity value and intrinsic value per share are then calculated as:

```text
Equity Value
= Enterprise Value
− Debt
+ Cash
```

```text
Intrinsic Value Per Share
= Equity Value ÷ Shares Outstanding
```

## Reverse DCF

The reverse DCF estimates the assumptions required to justify the company’s current market enterprise value.

Supported variables:

1. Starting revenue-growth rate
2. Starting operating margin

The model uses binary search to find the value that minimizes the difference between modeled and market enterprise value.

If the target valuation cannot be reached within the configured bounds, the model returns an infeasible-result message instead of producing an unrealistic assumption.

## Installation

Clone the repository:

```bash
git clone https://github.com/danvluewubley/dcf-valuation-model.git
cd dcf-valuation-model
```

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS or Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file and add your Alpha Vantage API key:

```env
ALPHA_VANTAGE_API_KEY=your_api_key_here
```

## Usage

Run the standard DCF:

```bash
python main.py AAPL
```

```bash
python main.py AAPL --analysis standard
```

Run bear, base, and bull scenarios:

```bash
python main.py AAPL --analysis scenarios
```

Run the revenue-growth reverse DCF:

```bash
python main.py AAPL --analysis reverse-growth
```

Run the operating-margin reverse DCF:

```bash
python main.py AAPL --analysis reverse-margin
```

Override valuation assumptions:

```bash
python main.py AAPL \
    --analysis standard \
    --wacc 0.10 \
    --terminal-growth 0.025
```

Change the reverse DCF fade rate:

```bash
python main.py AAPL \
    --analysis reverse-growth \
    --fade-rate 0.90
```

View all commands:

```bash
python main.py --help
```

## Project Structure

```text
dcf-valuation-model/
├── main.py
├── model/
│   ├── assumptions/
│   ├── data/
│   ├── forecast/
│   ├── reverse_dcf_support/
│   ├── validation/
│   ├── valuation/
│   ├── orchestrator.py
│   └── reverse_dcf.py
├── tests/
├── requirements.txt
├── .env.example
└── README.md
```

## Testing

Run the complete test suite:

```bash
pytest -v
```

The tests cover forecasting, UFCF, valuation, validation, and both reverse DCF solvers.

## Version 2

Version 2 includes:

* Modular code organization
* Historical and custom forecast assumptions
* Bear, base, and bull scenarios
* Revenue-growth reverse DCF
* Operating-margin reverse DCF
* Feasibility detection
* Market enterprise value calculation
* Data caching
* Expanded validation
* Automated tests
* Improved CLI functionality

## Limitations

* Valuation results are highly sensitive to growth, margins, WACC, and terminal growth.
* The model depends on Alpha Vantage data availability and field consistency.
* Forecasts are company-level rather than segment-level.
* Reverse DCF results depend on the assumptions held constant.
* Market prices may be loaded from cached data when API limits are reached.

## Future Improvements

* Historical and forecast charts
* Sensitivity tables and heatmaps
* Excel export
* Improved terminal output
* Combined revenue-growth and operating-margin analysis

## Disclaimer

This project is intended for educational and portfolio purposes only. It does not constitute investment advice.

## Author

**Daniel Wu**
