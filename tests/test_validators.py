"""
Unit tests for input validation — run with: pytest tests/
No API credentials required.
"""
import pytest
from decimal import Decimal

from bot.validators import (
    validate_symbol,
    validate_side,
    validate_order_type,
    validate_quantity,
    validate_price,
    validate_order_params,
)


class TestValidateSymbol:
    def test_normalises_to_uppercase(self):
        assert validate_symbol("btcusdt") == "BTCUSDT"

    def test_strips_whitespace(self):
        assert validate_symbol("  ETHUSDT  ") == "ETHUSDT"

    def test_rejects_empty(self):
        with pytest.raises(ValueError):
            validate_symbol("")

    def test_rejects_special_chars(self):
        with pytest.raises(ValueError):
            validate_symbol("BTC/USDT")


class TestValidateSide:
    def test_valid_buy(self):
        assert validate_side("buy") == "BUY"

    def test_valid_sell(self):
        assert validate_side("SELL") == "SELL"

    def test_rejects_invalid(self):
        with pytest.raises(ValueError):
            validate_side("LONG")


class TestValidateQuantity:
    def test_valid_quantity(self):
        assert validate_quantity("0.01") == Decimal("0.01")

    def test_rejects_zero(self):
        with pytest.raises(ValueError):
            validate_quantity(0)

    def test_rejects_negative(self):
        with pytest.raises(ValueError):
            validate_quantity(-1)

    def test_rejects_non_numeric(self):
        with pytest.raises(ValueError):
            validate_quantity("abc")


class TestValidateOrderParams:
    def test_market_order_no_price(self):
        params = validate_order_params("BTCUSDT", "BUY", "MARKET", 0.01)
        assert params["order_type"] == "MARKET"
        assert params["price"] is None

    def test_limit_requires_price(self):
        with pytest.raises(ValueError, match="price is required"):
            validate_order_params("BTCUSDT", "BUY", "LIMIT", 0.01)

    def test_market_rejects_price(self):
        with pytest.raises(ValueError, match="price must not be set"):
            validate_order_params("BTCUSDT", "BUY", "MARKET", 0.01, price=50000)

    def test_stop_limit_requires_stop_price(self):
        with pytest.raises(ValueError, match="stop_price is required"):
            validate_order_params("BTCUSDT", "SELL", "STOP_LIMIT", 0.01, price=58000)

    def test_valid_limit_order(self):
        params = validate_order_params("ETHUSDT", "SELL", "LIMIT", 0.5, price=2500)
        assert params["symbol"] == "ETHUSDT"
        assert params["price"] == Decimal("2500")
