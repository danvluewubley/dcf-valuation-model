import argparse

import dotenv

from model.orchestrator import run_model

dotenv.load_dotenv()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a DCF valuation for a single ticker."
    )
    parser.add_argument(
        "ticker",
        nargs="?",
        default="AAPL",
        help="Ticker symbol to value.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_model(args.ticker)
