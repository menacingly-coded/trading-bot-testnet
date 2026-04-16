from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from bot.client import BinanceFuturesClient, BinanceFuturesConfig, BinanceAPIError, NetworkError
from bot.logging_config import setup_logging
from bot.orders import place_order, summarize_order_response
from bot.validators import ValidationError, build_and_validate_order_input


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Simplified Binance Futures Testnet trading bot")
    p.add_argument("--symbol", required=True, help="e.g., BTCUSDT")
    p.add_argument("--side", required=True, choices=["BUY", "SELL"], help="BUY or SELL")
    p.add_argument("--type", required=True, choices=["MARKET", "LIMIT"], help="MARKET or LIMIT")
    p.add_argument("--quantity", required=True, help="Order quantity (number)")
    p.add_argument("--price", required=False, help="Required for LIMIT orders")
    p.add_argument(
        "--base-url",
        default="https://testnet.binancefuture.com",
        help="Binance Futures testnet base URL",
    )
    p.add_argument(
        "--log-file",
        default="trading_bot.log",
        help="Log filename (stored under ./logs)",
    )
    return p


def main() -> int:
    args = build_parser().parse_args()

    log_path = setup_logging(log_file=args.log_file)

    # Load .env if present (optional), but environment variables still work without it.
    load_dotenv(dotenv_path=Path(".env"), override=False)

    api_key = os.getenv("BINANCE_API_KEY", "").strip()
    api_secret = os.getenv("BINANCE_API_SECRET", "").strip()

    if not api_key or not api_secret:
        print("ERROR: Missing BINANCE_API_KEY / BINANCE_API_SECRET environment variables.", file=sys.stderr)
        print("Tip: Create a .env file or export the variables in your shell.", file=sys.stderr)
        return 2

    try:
        order_input = build_and_validate_order_input(
            symbol=args.symbol,
            side=args.side,
            order_type=args.type,
            quantity=args.quantity,
            price=args.price,
        )
    except ValidationError as e:
        print(f"INPUT ERROR: {e}", file=sys.stderr)
        return 2

    client = BinanceFuturesClient(
        BinanceFuturesConfig(
            api_key=api_key,
            api_secret=api_secret,
            base_url=args.base_url,
        )
    )

    # Print request summary
    print("=== Order Request Summary ===")
    print(json.dumps(order_input.__dict__, indent=2, sort_keys=True))
    print(f"(Logging to: {log_path})")
    print()

    try:
        resp = place_order(client, order_input)
    except BinanceAPIError as e:
        print("=== Order Failed (API Error) ===", file=sys.stderr)
        print(str(e), file=sys.stderr)
        return 1
    except NetworkError as e:
        print("=== Order Failed (Network Error) ===", file=sys.stderr)
        print(str(e), file=sys.stderr)
        return 1
    except Exception as e:
        print("=== Order Failed (Unexpected Error) ===", file=sys.stderr)
        print(repr(e), file=sys.stderr)
        return 1

    # Print response details
    print("=== Order Response Details ===")
    print(json.dumps(summarize_order_response(resp), indent=2, sort_keys=True))
    print()
    print("SUCCESS: Order placed on Binance Futures Testnet.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())