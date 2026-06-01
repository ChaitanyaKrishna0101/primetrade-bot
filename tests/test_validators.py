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
        assert validate_symbol("btcusdt") == "BTCUSDT", \
            "validate_symbol should convert lowercase to uppercase"

    def test_strips_whitespace(self):
        assert validate_symbol("  ETHUSDT  ") == "ETHUSDT", \
            "validate_symbol should strip leading and trailing whitespace"

    def test_rejects_empty(self):
        with pytest.raises(ValueError, match="symbol must be a non-empty string"):
            validate_symbol("")

    def test_rejects_special_chars(self):
        with pytest.raises(ValueError, match="looks wrong"):
            validate_symbol("BTC/USDT")


class TestValidateSide:
    def test_valid_buy(self):
        assert validate_side("buy") == "BUY", \
            "validate_side should convert 'buy' to uppercase 'BUY'"

    def test_valid_sell(self):
        assert validate_side("SELL") == "SELL", \
            "validate_side should accept and return 'SELL' unchanged"

    def test_rejects_invalid(self):
        with pytest.raises(ValueError, match="got 'LONG'"):
            validate_side("LONG")


class TestValidateQuantity:
    def test_valid_quantity(self):
        assert validate_quantity("0.01") == Decimal("0.01"), \
            "validate_quantity should convert valid string '0.01' to Decimal"

    def test_rejects_zero(self):
        with pytest.raises(ValueError, match="must be > 0"):
            validate_quantity(0)

    def test_rejects_negative(self):
        with pytest.raises(ValueError, match="must be > 0"):
            validate_quantity(-1)

    def test_rejects_non_numeric(self):
        with pytest.raises(ValueError, match="is not a valid number"):
            validate_quantity("abc")


class TestValidateOrderParams:
    def test_market_order_no_price(self):
        params = validate_order_params("BTCUSDT", "BUY", "MARKET", 0.01)
        assert params["order_type"] == "MARKET", \
            "MARKET order should have order_type set to 'MARKET'"
        assert params["price"] is None, \
            "MARKET order should have price set to None"

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
        assert params["symbol"] == "ETHUSDT", \
            "LIMIT order should have symbol set to 'ETHUSDT'"
        assert params["price"] == Decimal("2500"), \
            "LIMIT order should have price converted to Decimal('2500')"