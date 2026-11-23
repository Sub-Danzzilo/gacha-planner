from decimal import Decimal

import pytest

from core.models.currency import Currency, CurrencyKind, Money
from ui.parsing import (
    InputError,
    describe_error,
    format_money,
    format_percent,
    parse_decimal,
    parse_non_negative_int,
    parse_percent,
    parse_positive_int,
)

IDR = Currency(code="IDR", name="Rupiah", kind=CurrencyKind.REAL)
USD = Currency(code="USD", name="Dollar", kind=CurrencyKind.REAL, decimals=2)


@pytest.mark.parametrize("text", ["1.3", "1,3", " 1.3 % "])
def test_parse_percent_accepts_both_separators(text: str) -> None:
    assert parse_percent(text) == pytest.approx(0.013)


@pytest.mark.parametrize("text", ["", "abc", "-1", "101", "1.2.3"])
def test_parse_percent_rejects_invalid_text(text: str) -> None:
    with pytest.raises(InputError):
        parse_percent(text)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("16000", Decimal("16000")),
        ("16,000.50", Decimal("16000.50")),
        ("1.3", Decimal("1.3")),
        ("1,234", Decimal("1234")),
        ("0.5", Decimal("0.5")),
    ],
)
def test_parse_decimal_uses_dot_for_decimals(text: str, expected: Decimal) -> None:
    assert parse_decimal(text) == expected


@pytest.mark.parametrize("text", ["16.000,50", "1,3", "-5", "abc", "", "1.2.3"])
def test_parse_decimal_rejects_invalid_text(text: str) -> None:
    with pytest.raises(InputError):
        parse_decimal(text)


def test_integer_parsers() -> None:
    assert parse_positive_int("10") == 10
    assert parse_non_negative_int("0") == 0
    assert parse_non_negative_int("1,000") == 1000
    with pytest.raises(InputError):
        parse_positive_int("0")
    with pytest.raises(InputError):
        parse_non_negative_int("x")


def test_format_percent() -> None:
    assert format_percent(0.9) == "90.00%"
    assert format_percent(0.0125) == "1.25%"


def test_format_money_respects_currency_decimals() -> None:
    assert format_money(Money(Decimal("16000"), IDR)) == "16,000 IDR"
    assert format_money(Money(Decimal("1234.5"), USD)) == "1,234.50 USD"


def test_describe_error_unwraps_key_error() -> None:
    assert describe_error(KeyError("Banner not found")) == "Banner not found"
    assert describe_error(ValueError("Invalid value")) == "Invalid value"
