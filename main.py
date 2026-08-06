import argparse

import dotenv

from model.orchestrator import run_model
from model.reverse_dcf import run_reverse_dcf

dotenv.load_dotenv()


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments for valuation analysis."""
    parser = argparse.ArgumentParser(
        description=(
            "Run standard DCF, scenario, sensitivity, "
            "and reverse DCF analyses."
        )
    )

    parser.add_argument(
        "ticker",
        type=str,
        help="Stock ticker symbol, such as AAPL or MSFT.",
    )

    parser.add_argument(
        "--analysis",
        choices=[
            "standard",
            "scenarios",
            "reverse-growth",
            "reverse-margin",
        ],
        default="standard",
        help="Type of valuation analysis to run.",
    )

    parser.add_argument(
        "--wacc",
        type=float,
        help="Optional WACC override as a decimal, such as 0.10.",
    )

    parser.add_argument(
        "--terminal-growth",
        type=float,
        help=(
            "Optional terminal growth override as a decimal, "
            "such as 0.025."
        ),
    )

    parser.add_argument(
        "--fade-rate",
        type=float,
        default=0.90,
        help="Reverse DCF fade rate. Default: 0.90.",
    )
    

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    if args.analysis == "reverse-growth":
        run_reverse_dcf(args.ticker, args.analysis, args.fade_rate)
    elif args.analysis == "reverse-margin":
        run_reverse_dcf(args.ticker, args.analysis, args.fade_rate)
    elif args.analysis == "scenarios":
        run_model(args.ticker, analysis=args.analysis)
    elif args.analysis == "standard":
        run_model(
            args.ticker,
            args.analysis,
            args.wacc if args.wacc is not None else 0.1091,
            args.terminal_growth if args.terminal_growth is not None else 0.025,
        )
    else:
        raise ValueError(
            f"Unsupported analysis mode: {args.analysis}"
        )
