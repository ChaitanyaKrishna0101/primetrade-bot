"""
Market monitor — live price display, P&L, and open position tracking.
Used by the 'monitor' and 'positions' CLI commands.
"""
from __future__ import annotations

from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich import box
import time

from .client import BinanceFuturesClient
from .logging_config import get_logger

logger = get_logger("monitor")
console = Console()


def show_account_summary(client: BinanceFuturesClient) -> None:
    account = client.get_account_info()
    assets = [a for a in account.get("assets", []) if float(a.get("walletBalance", 0)) > 0]

    table = Table(title="💼 Account Summary", box=box.ROUNDED)
    table.add_column("Asset", style="cyan bold")
    table.add_column("Wallet Balance", style="green")
    table.add_column("Unrealized PNL", style="yellow")
    table.add_column("Margin Balance", style="white")

    for asset in assets:
        pnl = float(asset.get("unrealizedProfit", 0))
        pnl_str = f"{'🟢' if pnl >= 0 else '🔴'} {pnl:.4f}"
        table.add_row(
            asset["asset"],
            f"{float(asset['walletBalance']):.4f}",
            pnl_str,
            f"{float(asset['marginBalance']):.4f}",
        )
    console.print(table)


def show_positions(client: BinanceFuturesClient, symbol: Optional[str] = None) -> None:
    positions = client.get_positions(symbol)
    active = [p for p in positions if float(p.get("positionAmt", 0)) != 0]

    if not active:
        console.print(Panel("[yellow]No open positions[/yellow]"))
        return

    table = Table(title="📊 Open Positions", box=box.ROUNDED)
    table.add_column("Symbol", style="cyan bold")
    table.add_column("Side", style="white")
    table.add_column("Size", style="white")
    table.add_column("Entry Price", style="yellow")
    table.add_column("Mark Price", style="white")
    table.add_column("Unrealized PNL", style="green")
    table.add_column("ROE %", style="magenta")

    for pos in active:
        amt = float(pos["positionAmt"])
        side = "🟢 LONG" if amt > 0 else "🔴 SHORT"
        pnl = float(pos.get("unRealizedProfit", 0))
        entry = float(pos.get("entryPrice", 0))
        mark = float(pos.get("markPrice", 0))
        roe = ((mark - entry) / entry * 100) if entry > 0 else 0
        if amt < 0:
            roe = -roe

        pnl_color = "green" if pnl >= 0 else "red"
        table.add_row(
            pos["symbol"],
            side,
            str(abs(amt)),
            f"{entry:.4f}",
            f"{mark:.4f}",
            f"[{pnl_color}]{pnl:.4f}[/{pnl_color}]",
            f"[{pnl_color}]{roe:.2f}%[/{pnl_color}]",
        )
    console.print(table)


def show_open_orders(client: BinanceFuturesClient, symbol: Optional[str] = None) -> None:
    orders = client.get_open_orders(symbol)
    if not orders:
        console.print(Panel("[yellow]No open orders[/yellow]"))
        return

    table = Table(title="📋 Open Orders", box=box.ROUNDED)
    table.add_column("Order ID", style="dim")
    table.add_column("Symbol", style="cyan bold")
    table.add_column("Side", style="white")
    table.add_column("Type", style="white")
    table.add_column("Qty", style="white")
    table.add_column("Price", style="yellow")
    table.add_column("Status", style="green")

    for order in orders:
        side_color = "green" if order["side"] == "BUY" else "red"
        table.add_row(
            str(order["orderId"]),
            order["symbol"],
            f"[{side_color}]{order['side']}[/{side_color}]",
            order["type"],
            order["origQty"],
            order.get("price", "MARKET"),
            order["status"],
        )
    console.print(table)


def show_ticker(client: BinanceFuturesClient, symbol: str) -> None:
    ticker = client.get_ticker(symbol)
    price = float(ticker.get("price", 0))
    console.print(
        Panel(
            f"[bold white]{symbol}[/bold white]  →  [bold green]${price:,.4f}[/bold green]",
            title="📈 Live Price",
        )
    )


def live_monitor(client: BinanceFuturesClient, symbol: str, refresh: int = 5) -> None:
    """Continuously refresh price + positions every `refresh` seconds."""
    console.print(f"[cyan]Live monitoring {symbol} — press Ctrl+C to stop[/cyan]")
    try:
        while True:
            console.clear()
            show_ticker(client, symbol)
            show_positions(client, symbol)
            show_open_orders(client, symbol)
            time.sleep(refresh)
    except KeyboardInterrupt:
        console.print("\n[yellow]Monitor stopped[/yellow]")
