from __future__ import annotations

import hashlib
import hmac
import logging
import time
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode

import requests


logger = logging.getLogger("bot.client")


class BinanceAPIError(RuntimeError):
    def __init__(self, status_code: int, payload: Any):
        super().__init__(f"Binance API error (HTTP {status_code}): {payload}")
        self.status_code = status_code
        self.payload = payload


class NetworkError(RuntimeError):
    pass


@dataclass(frozen=True)
class BinanceFuturesConfig:
    api_key: str
    api_secret: str
    base_url: str = "https://testnet.binancefuture.com"
    recv_window: int = 5000
    timeout_seconds: int = 20


class BinanceFuturesClient:
    """
    Minimal Binance USDT-M Futures client for testnet with signed endpoints.
    """

    def __init__(self, config: BinanceFuturesConfig) -> None:
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({"X-MBX-APIKEY": self.config.api_key})

    def _sign(self, query_string: str) -> str:
        return hmac.new(
            self.config.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def _request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        signed: bool = False,
    ) -> dict[str, Any]:
        params = dict(params or {})

        if signed:
            params["timestamp"] = int(time.time() * 1000)
            params["recvWindow"] = self.config.recv_window
            qs = urlencode(params, doseq=True)
            params["signature"] = self._sign(qs)

        url = self.config.base_url.rstrip("/") + path

        try:
            logger.info("HTTP %s %s params=%s signed=%s", method, url, params, signed)
            resp = self.session.request(
                method=method,
                url=url,
                params=params,
                timeout=self.config.timeout_seconds,
            )
        except requests.RequestException as e:
            logger.exception("Network failure calling Binance")
            raise NetworkError(str(e)) from e

        content_type = resp.headers.get("Content-Type", "")
        try:
            data = resp.json() if "application/json" in content_type else {"raw": resp.text}
        except Exception:
            data = {"raw": resp.text}

        logger.info("HTTP %s response status=%s body=%s", method, resp.status_code, data)

        if resp.status_code >= 400:
            raise BinanceAPIError(resp.status_code, data)

        # Binance sometimes returns code/msg fields even with 200, but for futures
        # most errors are HTTP >= 4xx.
        return data

    # Public endpoints (useful for validation/diagnostics)
    def ping(self) -> dict[str, Any]:
        return self._request("GET", "/fapi/v1/ping", signed=False)

    # Signed order endpoint
    def create_order(self, **params: Any) -> dict[str, Any]:
        return self._request("POST", "/fapi/v1/order", params=params, signed=True)