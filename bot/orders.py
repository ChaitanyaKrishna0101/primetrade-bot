"""
Order logic layer — translates validated params into Binance API calls.
Handles formatting (precision), result normalisation, and pretty-printing.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from .client import BinanceFuturesClient
from .logging_config import get_logger

logger = get_logger("orders")
console = Console()


def _format_decimal(value: Optional[Decimal], precision: int = 8) -> Optional[str]:
    if value is None:
        return None
    return f"{value:.{precision}f}".rstrip("0").rstrip(".")


def _get_precision(client: BinanceFuturesClient, symbol: str) -> tuple[int, int]:
    """Return (quantity_precision, price_precision) for a symbol."""
    info = client.get_symbol_info(symbol)
    if not info:
        return 3, 2  # safe fallback
    return info.get("quantityPrecision", 3), info.get("pricePrecision", 2)


def _print_order_summary(params: dict) -> None:
    """Print the request summary before sending."""
    table = Table(title="📤 Order Request", box=box.ROUNDED, show_header=False)
    table.add_column("Field", style="cyan bold")
    table.add_column("Value", style="white")
    for k, v in params.items():
        if v is not None:
            table.add_row(k.upper(), str(v))
    console.print(table)


def _print_order_result(result: dict) -> None:
    """Print a nicely formatted order response."""
    status = result.get("status", "UNKNOWN")
    color = "green" if status in ("FILLED", "NEW") else "yellow"

    table = Table(title="📥 Order Response", box=box.ROUNDED, show_header=False)
    table.add_column("Field", style="cyan bold")
    table.add_column("Value", style=color)

    fields = [
        ("orderId", "Order ID"),
        ("symbol", "Symbol"),
        ("side", "Side"),
        ("type", "Type"),
        ("origQty", "Requested Qty"),
        ("executedQty", "Executed Qty"),
        ("avgPrice", "Avg Fill Price"),
        ("price", "Limit Price"),
        ("stopPrice", "Stop Price"),
        ("status", "Status"),
        ("timeInForce", "Time In Force"),
        ("updateTime", "Update Time"),
    ]
    for key, label in fields:
        val = result.get(key)
        if val is not None and str(val) not in ("", "0", "0.00000000"):
            table.add_row(label, str(val))

    console.print(table)

    if status in ("FILLED", "PARTIALLY_FILLED"):
        console.print(Panel(f"[bold green]✅ Order {status} successfully![/bold green]"))
    elif status == "NEW":
        console.print(Panel("[bold yellow]🕐 Order placed and waiting to be filled[/bold yellow]"))
    else:
        console.print(Panel(f"[bold red]⚠️  Order status: {status}[/bold red]"))


def place_market_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    quantity: Decimal,
) -> dict:
    qty_prec, _ = _get_precision(client, symbol)
    qty_str = f"{quantity:.{qty_prec}f}"

    params = {"symbol": symbol, "side": side, "type": "MARKET", "quantity": qty_str}
    _print_order_summary(params)
    result = client.place_order(**params)
    _print_order_result(result)
    return result


def place_limit_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    quantity: Decimal,
    price: Decimal,
    time_in_force: str = "GTC",
) -> dict:
    qty_prec, price_prec = _get_precision(client, symbol)
    qty_str = f"{quantity:.{qty_prec}f}"
    price_str = f"{price:.{price_prec}f}"

    params = {
        "symbol": symbol,
        "side": side,
        "type": "LIMIT",
        "quantity": qty_str,
        "price": price_str,
        "timeInForce": time_in_force,
    }
    _print_order_summary(params)
    result = client.place_order(**params)
    _print_order_result(result)
    return result


def place_stop_market_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    quantity: Decimal,
    stop_price: Decimal,
) -> dict:
    qty_prec, price_prec = _get_precision(client, symbol)
    qty_str = f"{quantity:.{qty_prec}f}"
    stop_str = f"{stop_price:.{price_prec}f}"

    params = {
        "symbol": symbol,
        "side": side,
        "type": "STOP_MARKET",
        "quantity": qty_str,
        "stopPrice": stop_str,
    }
    _print_order_summary(params)
    result = client.place_order(**params)
    _print_order_result(result)
    return result


def place_stop_limit_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    quantity: Decimal,
    price: Decimal,
    stop_price: Decimal,
    time_in_force: str = "GTC",
) -> dict:
    qty_prec, price_prec = _get_precision(client, symbol)
    qty_str = f"{quantity:.{qty_prec}f}"
    price_str = f"{price:.{price_prec}f}"
    stop_str = f"{stop_price:.{price_prec}f}"

    params = {
        "symbol": symbol,
        "side": side,
        "type": "STOP",
        "quantity": qty_str,
        "price": price_str,
        "stopPrice": stop_str,
        "timeInForce": time_in_force,
    }
    _print_order_summary(params)
    result = client.place_order(**params)
    _print_order_result(result)
    return result


def place_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    order_type: str,
    quantity: Decimal,
    price: Optional[Decimal] = None,
    stop_price: Optional[Decimal] = None,
    time_in_force: str = "GTC",
) -> dict:
    """Unified dispatcher — routes to the correct order function."""
    ot = order_type.upper()
    if ot == "MARKET":
        return place_market_order(client, symbol, side, quantity)
    elif ot == "LIMIT":
        return place_limit_order(client, symbol, side, quantity, price, time_in_force)
    elif ot == "STOP_MARKET":
        return place_stop_market_order(client, symbol, side, quantity, stop_price)
    elif ot == "STOP_LIMIT":
        return place_stop_limit_order(client, symbol, side, quantity, price, stop_price, time_in_force)
    else:
        raise ValueError(f"Unsupported order type: {order_type}")
