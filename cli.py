#!/usr/bin/env python3
import os
from dotenv import load_dotenv
load_dotenv()

import typer
from rich.console import Console
from rich.panel import Panel
from typing import Optional
from typing_extensions import Annotated

from bot.logging_config import setup_logging, get_logger
from bot.client import BinanceFuturesClient, BinanceAPIError, NetworkError
from bot.validators import validate_order_params
from bot.orders import place_order
from bot.monitor import show_account_summary, show_positions, show_open_orders, show_ticker, live_monitor
from bot.ai_analyst import analyse_trade, print_ai_analysis

setup_logging(log_dir=os.getenv("LOG_DIR", "logs"))
logger = get_logger("cli")
console = Console()
app = typer.Typer(name="primetrade-bot", help="PrimeTrade Bot - Binance Futures Testnet Trading CLI", add_completion=False)

def _get_client() -> BinanceFuturesClient:
    api_key = os.getenv("BINANCE_API_KEY", "")
    api_secret = os.getenv("BINANCE_API_SECRET", "")
    base_url = os.getenv("BINANCE_BASE_URL", "https://testnet.binancefuture.com")
    if not api_key or not api_secret:
        console.print(Panel("[bold red]Missing API credentials![/bold red]", title="Setup Required"))
        raise typer.Exit(1)
    return BinanceFuturesClient(api_key, api_secret, base_url)

@app.command()
def order(
    symbol: Annotated[str, typer.Option("--symbol", "-s", help="Trading pair, e.g. BTCUSDT")],
    side: Annotated[str, typer.Option("--side", help="BUY or SELL")],
    quantity: Annotated[float, typer.Option("--qty", "-q", help="Order quantity")],
    order_type: Annotated[str, typer.Option("--type", "-t", help="MARKET / LIMIT / STOP_MARKET / STOP_LIMIT")] = "MARKET",
    price: Annotated[Optional[float], typer.Option("--price", "-p", help="Limit price")] = None,
    stop_price: Annotated[Optional[float], typer.Option("--stop-price", help="Stop trigger price")] = None,
    time_in_force: Annotated[str, typer.Option("--tif", help="GTC/IOC/FOK")] = "GTC",
    no_ai: Annotated[bool, typer.Option("--no-ai", help="Skip AI analysis")] = False,
    yes: Annotated[bool, typer.Option("--yes", "-y", help="Skip confirmation")] = False,
):
    """Place a futures order on Binance Testnet."""
    try:
        params = validate_order_params(symbol=symbol, side=side, order_type=order_type, quantity=quantity, price=price, stop_price=stop_price)
    except ValueError as exc:
        console.print(f"[bold red]Validation error:[/bold red] {exc}")
        raise typer.Exit(1)

    client = _get_client()

    if not no_ai:
        try:
            current_price_data = client.get_ticker(params["symbol"])
            current_price = float(current_price_data.get("price", 0))
            klines = client.get_klines(params["symbol"], "15m", 20)
        except Exception:
            current_price = None
            klines = None
        analysis = analyse_trade(symbol=str(params["symbol"]), side=str(params["side"]), order_type=str(params["order_type"]), quantity=float(params["quantity"]), price=float(params["price"]) if params["price"] else None, current_price=current_price, klines=klines)
        print_ai_analysis(analysis)
        if analysis.get("recommendation") == "ABORT" and not yes:
            abort = typer.confirm("AI recommends ABORTING. Continue anyway?")
            if not abort:
                console.print("[yellow]Order cancelled.[/yellow]")
                raise typer.Exit(0)

    if not yes:
        confirmed = typer.confirm(f"Confirm: {params['side']} {params['quantity']} {params['symbol']} @ {params['order_type']}" + (f" price={params['price']}" if params["price"] else "") + "?")
        if not confirmed:
            console.print("[yellow]Order cancelled.[/yellow]")
            raise typer.Exit(0)

    try:
        result = place_order(client=client, symbol=str(params["symbol"]), side=str(params["side"]), order_type=str(params["order_type"]), quantity=params["quantity"], price=params["price"], stop_price=params["stop_price"], time_in_force=time_in_force)
        logger.info("Order completed successfully", extra={"result": result})
    except BinanceAPIError as exc:
        console.print(f"[bold red]API Error [{exc.code}]:[/bold red] {exc.message}")
        raise typer.Exit(1)
    except NetworkError as exc:
        console.print(f"[bold red]Network Error:[/bold red] {exc}")
        raise typer.Exit(1)
    except Exception as exc:
        console.print(f"[bold red]Unexpected error:[/bold red] {exc}")
        raise typer.Exit(1)
    finally:
        client.close()

@app.command()
def positions(symbol: Annotated[Optional[str], typer.Option("--symbol", "-s")] = None):
    """Show open futures positions."""
    client = _get_client()
    try:
        show_positions(client, symbol)
    finally:
        client.close()

@app.command()
def orders(symbol: Annotated[Optional[str], typer.Option("--symbol", "-s")] = None):
    """Show open orders."""
    client = _get_client()
    try:
        show_open_orders(client, symbol)
    finally:
        client.close()

@app.command()
def account():
    """Show account balance and margin summary."""
    client = _get_client()
    try:
        show_account_summary(client)
    finally:
        client.close()

@app.command()
def ticker(symbol: Annotated[str, typer.Option("--symbol", "-s", help="Symbol to check")]):
    """Show current market price."""
    client = _get_client()
    try:
        show_ticker(client, symbol)
    finally:
        client.close()

@app.command()
def monitor(
    symbol: Annotated[str, typer.Option("--symbol", "-s", help="Symbol to monitor")],
    refresh: Annotated[int, typer.Option("--refresh", "-r", help="Refresh interval seconds")] = 5,
):
    """Live-monitor price, positions, and open orders."""
    client = _get_client()
    try:
        live_monitor(client, symbol, refresh)
    finally:
        client.close()

@app.command()
def cancel(
    symbol: Annotated[str, typer.Option("--symbol", "-s", help="Symbol")],
    order_id: Annotated[int, typer.Option("--order-id", help="Order ID to cancel")],
):
    """Cancel an open order by ID."""
    client = _get_client()
    try:
        result = client.cancel_order(symbol.upper(), order_id)
        console.print(Panel(f"[green]Order {result.get('orderId')} cancelled - status: {result.get('status')}[/green]"))
        logger.info(f"Order {order_id} cancelled", extra={"result": result})
    except BinanceAPIError as exc:
        console.print(f"[bold red]API Error:[/bold red] {exc.message}")
        raise typer.Exit(1)
    finally:
        client.close()

if __name__ == "__main__":
    app()