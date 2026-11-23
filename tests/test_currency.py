import operator
from collections.abc import Callable
from decimal import Decimal
from typing import cast

import pytest

from core.models.currency import Currency, CurrencyKind, CurrencyMismatchError, Money

DIAMOND = Currency(code="DIAMOND", name="Diamond", kind=CurrencyKind.GAME)
USD = Currency(code="USD", name="Dolar", kind=CurrencyKind.REAL, decimals=2)


def test_currency_rejects_lowercase_code() -> None:
    with pytest.raises(ValueError):
        Currency(code="usd", name="Dolar", kind=CurrencyKind.REAL)


def test_currency_rejects_negative_decimals() -> None:
    with pytest.raises(ValueError):
        Currency(code="USD", name="Dolar", kind=CurrencyKind.REAL, decimals=-1)


def test_money_rejects_float() -> None:
    with pytest.raises(TypeError):
        Money(amount=cast(Decimal, 1.5), currency=USD)


def test_money_add_and_subtract() -> None:
    total = Money(Decimal("10"), DIAMOND) + Money(Decimal("5"), DIAMOND)
    assert total == Money(Decimal("15"), DIAMOND)
    assert total - Money(Decimal("20"), DIAMOND) == Money(Decimal("-5"), DIAMOND)


def test_money_multiplies_by_int_and_decimal() -> None:
    price = Money(Decimal("160"), DIAMOND)
    assert price * 3 == Money(Decimal("480"), DIAMOND)
    assert 3 * price == Money(Decimal("480"), DIAMOND)
    assert price * Decimal("0.5") == Money(Decimal("80"), DIAMOND)


def test_money_rejects_float_factor() -> None:
    with pytest.raises(TypeError):
        Money(Decimal("10"), DIAMOND) * cast(Decimal, 2.5)


def test_money_mixing_currencies_raises() -> None:
    with pytest.raises(CurrencyMismatchError):
        Money(Decimal("1"), DIAMOND) + Money(Decimal("1"), USD)
    with pytest.raises(CurrencyMismatchError):
        Money(Decimal("1"), DIAMOND) - Money(Decimal("1"), USD)


def test_money_comparison_within_same_currency() -> None:
    assert Money(Decimal("1"), DIAMOND) < Money(Decimal("2"), DIAMOND)
    assert Money(Decimal("1"), DIAMOND) <= Money(Decimal("1"), DIAMOND)
    assert Money(Decimal("3"), DIAMOND) > Money(Decimal("2"), DIAMOND)
    assert Money(Decimal("2"), DIAMOND) >= Money(Decimal("2"), DIAMOND)


@pytest.mark.parametrize(
    "compare",
    [operator.lt, operator.le, operator.gt, operator.ge],
)
def test_money_ordering_across_currencies_raises(
    compare: Callable[[Money, Money], bool],
) -> None:
    with pytest.raises(CurrencyMismatchError):
        compare(Money(Decimal("1"), DIAMOND), Money(Decimal("1"), USD))
    with pytest.raises(CurrencyMismatchError):
        compare(Money(Decimal("1"), USD), Money(Decimal("1"), DIAMOND))


def test_money_equality_across_currencies_is_false() -> None:
    dollars = Money(Decimal("1"), USD)
    diamonds = Money(Decimal("1"), DIAMOND)
    assert dollars != diamonds
    assert (dollars == diamonds) is False
