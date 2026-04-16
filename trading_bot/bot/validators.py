from __future__ import annotations

from dataclasses import dataclass


class ValidationError(ValueError):
    pass


@dataclass(frozen=True)
class OrderInput:
    symbol: str
    side: str
    order_type: str
    quantity: float
    price: float | None = None


def validate_symbol(symbol: str) -> str:
    s = symbol.strip().upper()
    if not s or len(s) < 6:
        raise ValidationError("symbol looks invalid (example: BTCUSDT).")
    # Binance futures symbols are typically uppercase without separators
    if any(ch.isspace() for ch in s):
        raise ValidationError("symbol must not contain spaces.")
    return s


def validate_side(side: str) -> str:
    s = side.strip().upper()
    if s not in {"BUY", "SELL"}:
        raise ValidationError("side must be BUY or SELL.")
    return s


def validate_order_type(order_type: str) -> str:
    t = order_type.strip().upper()
    if t not in {"MARKET", "LIMIT"}:
        raise ValidationError("order type must be MARKET or LIMIT.")
    return t


def validate_quantity(qty: str) -> float:
    try:
        v = float(qty)
    except Exception as e:
        raise ValidationError("quantity must be a number.") from e
    if v <= 0:
        raise ValidationError("quantity must be > 0.")
    return v


def validate_price(price: str) -> float:
    try:
        v = float(price)
    except Exception as e:
        raise ValidationError("price must be a number.") from e
    if v <= 0:
        raise ValidationError("price must be > 0.")
    return v


def build_and_validate_order_input(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: str | None,
) -> OrderInput:
    s = validate_symbol(symbol)
    sd = validate_side(side)
    ot = validate_order_type(order_type)
    q = validate_quantity(quantity)

    if ot == "LIMIT":
        if price is None:
            raise ValidationError("price is required for LIMIT orders.")
        p = validate_price(price)
    else:
        if price is not None:
            # Not an error; but keep UX clean.
            p = None
        else:
            p = None

    return OrderInput(symbol=s, side=sd, order_type=ot, quantity=q, price=p)