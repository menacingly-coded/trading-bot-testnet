from __future__ import annotations

import logging
from dataclasses import asdict
from typing import Any

from .client import BinanceFuturesClient
from .validators import OrderInput


logger = logging.getLogger("bot.orders")


def place_order(client: BinanceFuturesClient, order: OrderInput) -> dict[str, Any]:
    """
    Places an order and returns the API response (dict).
    """
    params: dict[str, Any] = {
        "symbol": order.symbol,
        "side": order.side,
        "type": order.order_type,
        "quantity": order.quantity,
        # Use responseType RESULT to get fills/avgPrice when available.
        # On some endpoints it may be "ACK"/"RESULT"/"FULL".
        "newOrderRespType": "RESULT",
    }

    if order.order_type == "LIMIT":
        params["price"] = order.price
        params["timeInForce"] = "GTC"

    logger.info("Placing order: %s", asdict(order))
    return client.create_order(**params)


def summarize_order_response(resp: dict[str, Any]) -> dict[str, Any]:
    """
    Extracts key fields for clean printing.
    Fields vary depending on response type.
    """
    return {
        "orderId": resp.get("orderId"),
        "symbol": resp.get("symbol"),
        "status": resp.get("status"),
        "type": resp.get("type"),
        "side": resp.get("side"),
        "origQty": resp.get("origQty"),
        "executedQty": resp.get("executedQty"),
        # Futures may provide avgPrice; some responses provide it under "avgPrice".
        "avgPrice": resp.get("avgPrice") or resp.get("averagePrice"),
        "price": resp.get("price"),
        "updateTime": resp.get("updateTime"),
    }