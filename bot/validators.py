"""
Input validation layer — all checks before any API call is made.
Raises ValueError with actionable messages on bad input.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Optional


VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_MARKET", "STOP_LIMIT"}
MIN_QUANTITY = Decimal("0.001")
MAX_SYMBOL_LEN = 20


def validate_symbol(symbol: str) -> str:
    """Normalise and sanity-check a trading pair symbol."""
    if not symbol or not isinstance(symbol, str):
        raise ValueError("symbol must be a non-empty string (e.g. BTCUSDT)")
    symbol = symbol.strip().upper()
    if len(symbol) > MAX_SYMBOL_LEN or not symbol.isalnum():
        raise ValueError(
            f"symbol '{symbol}' looks wrong — expected alphanumeric, max {MAX_SYMBOL_LEN} chars"
        )
    return symbol


def validate_side(side: str) -> str:
    """Ensure side is BUY or SELL (case-insensitive)."""
    if not side or not isinstance(side, str):
        raise ValueError("side must be BUY or SELL")
    side = side.strip().upper()
    if side not in VALID_SIDES:
        raise ValueError(f"side must be one of {VALID_SIDES}, got '{side}'")
    return side


def validate_order_type(order_type: str) -> str:
    """Ensure order type is supported."""
    if not order_type or not isinstance(order_type, str):
        raise ValueError(f"order_type must be one of {VALID_ORDER_TYPES}")
    order_type = order_type.strip().upper()
    if order_type not in VALID_ORDER_TYPES:
        raise ValueError(
            f"order_type must be one of {VALID_ORDER_TYPES}, got '{order_type}'"
        )
    return order_type


def validate_quantity(quantity: str | float | Decimal) -> Decimal:
    """Parse and validate quantity — must be positive."""
    try:
        qty = Decimal(str(quantity))
    except InvalidOperation:
        raise ValueError(f"quantity '{quantity}' is not a valid number")
    if qty <= 0:
        raise ValueError(f"quantity must be > 0, got {qty}")
    if qty < MIN_QUANTITY:
        raise ValueError(f"quantity {qty} is below minimum allowed {MIN_QUANTITY}")
    return qty


def validate_price(price: Optional[str | float | Decimal]) -> Optional[Decimal]:
    """Parse and validate an optional price — required for LIMIT orders."""
    if price is None:
        return None
    try:
        p = Decimal(str(price))
    except InvalidOperation:
        raise ValueError(f"price '{price}' is not a valid number")
    if p <= 0:
        raise ValueError(f"price must be > 0, got {p}")
    return p


def validate_stop_price(stop_price: Optional[str | float | Decimal]) -> Optional[Decimal]:
    """Parse and validate an optional stop price."""
    return validate_price(stop_price)


def validate_order_params(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str | float,
    price: Optional[str | float] = None,
    stop_price: Optional[str | float] = None,
) -> dict:
    """
    Full cross-field validation.
    Returns a clean dict ready for the API layer.
    """
    params = {
        "symbol": validate_symbol(symbol),
        "side": validate_side(side),
        "order_type": validate_order_type(order_type),
        "quantity": validate_quantity(quantity),
        "price": validate_price(price),
        "stop_price": validate_stop_price(stop_price),
    }

    ot = params["order_type"]

    if ot == "LIMIT" and params["price"] is None:
        raise ValueError("price is required for LIMIT orders")

    if ot == "STOP_LIMIT":
        if params["price"] is None:
            raise ValueError("price (limit price) is required for STOP_LIMIT orders")
        if params["stop_price"] is None:
            raise ValueError("stop_price is required for STOP_LIMIT orders")
        if params["stop_price"] >= params["price"] and params["side"] == "BUY":
            raise ValueError(
                "For a BUY STOP_LIMIT, stop_price should be below price"
            )

    if ot == "STOP_MARKET" and params["stop_price"] is None:
        raise ValueError("stop_price is required for STOP_MARKET orders")

    if ot == "MARKET" and params["price"] is not None:
        raise ValueError("price must not be set for MARKET orders")

    return params
