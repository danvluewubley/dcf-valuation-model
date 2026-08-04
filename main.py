import argparse

import dotenv

from model.orchestrator import run_model
from model.reverse_dcf import run_reverse_dcf

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
    parser.add_argument(
        "--reverse",
        action="store_true",
        help="Run reverse DCF model.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.reverse:
        run_reverse_dcf(args.ticker)
    else:
        run_model(args.ticker)
