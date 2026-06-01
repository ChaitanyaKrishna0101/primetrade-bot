"""
Low-level Binance Spot REST client (Testnet).
Handles authentication (HMAC-SHA256), request signing,
retry-with-backoff, and structured error translation.
"""
from __future__ import annotations

import hashlib
import hmac
import time
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import httpx

from .logging_config import get_logger

logger = get_logger("client")

BASE_URL = "https://testnet.binance.vision"
RECV_WINDOW = 5000
MAX_RETRIES = 3
BACKOFF_BASE = 1.5


class BinanceAPIError(Exception):
    def __init__(self, code: int, message: str, raw: dict | None = None):
        self.code = code
        self.message = message
        self.raw = raw or {}
        super().__init__(f"[{code}] {message}")


class NetworkError(Exception):
    pass


class BinanceFuturesClient:
    def __init__(self, api_key: str, api_secret: str, base_url: str = BASE_URL):
        if not api_key or not api_secret:
            raise ValueError("API key and secret must be non-empty strings")
        self._api_key = api_key
        self._api_secret = api_secret.encode()
        self._base_url = base_url.rstrip("/")
        self._session = httpx.Client(
            timeout=httpx.Timeout(10.0, connect=5.0),
            headers={
                "X-MBX-APIKEY": self._api_key,
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )
        logger.info("BinanceFuturesClient initialised", extra={"base_url": self._base_url})

    def _sign(self, params: dict) -> dict:
        params["timestamp"] = int(time.time() * 1000) - 1000
        params["recvWindow"] = RECV_WINDOW
        query = urlencode(params)
        sig = hmac.new(self._api_secret, query.encode(), hashlib.sha256).hexdigest()
        params["signature"] = sig
        return params

    def _request(self, method: str, path: str, params: Optional[dict] = None, sign: bool = False) -> dict:
        params = params or {}
        if sign:
            params = self._sign(params)

        url = f"{self._base_url}{path}"
        safe_params = {k: v for k, v in params.items() if k != "signature"}
        logger.debug("API request", extra={"method": method, "path": path, "params": safe_params})

        last_exc: Exception | None = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                if method.upper() == "GET":
                    resp = self._session.get(url, params=params)
                elif method.upper() == "DELETE":
                    resp = self._session.delete(url, params=params)
                else:
                    resp = self._session.post(url, data=params)

                logger.debug("API response", extra={"status": resp.status_code, "path": path, "attempt": attempt})

                data = resp.json()

                if resp.status_code != 200:
                    code = data.get("code", resp.status_code)
                    msg = data.get("msg", resp.text)
                    logger.error("API error", extra={"code": code, "error_msg": msg, "path": path})
                    raise BinanceAPIError(code, msg, data)

                return data

            except (httpx.TimeoutException, httpx.NetworkError) as exc:
                logger.warning(f"Network error attempt {attempt}/{MAX_RETRIES}: {exc}", extra={"path": path})
                last_exc = exc
                if attempt < MAX_RETRIES:
                    time.sleep(BACKOFF_BASE ** attempt)

        raise NetworkError(f"All {MAX_RETRIES} attempts failed for {path}: {last_exc}")

    def close(self):
        self._session.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def get_server_time(self) -> dict:
        return self._request("GET", "/api/v3/time")

    def get_exchange_info(self) -> dict:
        return self._request("GET", "/api/v3/exchangeInfo")

    def get_symbol_info(self, symbol: str) -> Optional[dict]:
        info = self.get_exchange_info()
        for s in info.get("symbols", []):
            if s["symbol"] == symbol:
                return s
        return None

    def get_account_info(self) -> dict:
        return self._request("GET", "/api/v3/account", sign=True)

    def get_positions(self, symbol: Optional[str] = None) -> list:
        # Spot testnet has no positions endpoint ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â return open orders instead
        params = {}
        if symbol:
            params["symbol"] = symbol
        return self._request("GET", "/api/v3/openOrders", params=params, sign=True)

    def get_ticker(self, symbol: str) -> dict:
        return self._request("GET", "/api/v3/ticker/price", params={"symbol": symbol})

    def get_klines(self, symbol: str, interval: str = "1m", limit: int = 100) -> list:
        return self._request(
            "GET",
            "/api/v3/klines",
            params={"symbol": symbol, "interval": interval, "limit": limit},
        )

    def place_order(self, **kwargs) -> dict:
        params = {k: v for k, v in kwargs.items() if v is not None}
        logger.info("Placing order: %s", str(params))
        result = self._request("POST", "/api/v3/order", params=params, sign=True)
        logger.info("Order placed orderId=%s status=%s", result.get("orderId"), result.get("status"))
        return result

    def cancel_order(self, symbol: str, order_id: int) -> dict:
        params = {"symbol": symbol, "orderId": order_id}
        return self._request("DELETE", "/api/v3/order", params=params, sign=True)

    def get_open_orders(self, symbol: Optional[str] = None) -> list:
        params = {}
        if symbol:
            params["symbol"] = symbol
        return self._request("GET", "/api/v3/openOrders", params=params, sign=True)

    def get_order(self, symbol: str, order_id: int) -> dict:
        params = {"symbol": symbol, "orderId": order_id}
        return self._request("GET", "/api/v3/order", params=params, sign=True)