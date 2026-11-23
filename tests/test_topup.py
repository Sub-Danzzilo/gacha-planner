from decimal import Decimal

import pytest

from core.models.currency import Currency, CurrencyKind, Money
from core.models.topup import TopUpPackage

DIAMOND = Currency(code="DIAMOND", name="Diamond", kind=CurrencyKind.GAME)
IDR = Currency(code="IDR", name="Rupiah", kind=CurrencyKind.REAL)


def _package(
    price: Money | None = None,
    grants: Currency = DIAMOND,
    base_amount: int = 60,
    bonus_amount: int = 0,
    first_purchase_bonus: int = 0,
) -> TopUpPackage:
    return TopUpPackage(
        price=price if price is not None else Money(Decimal("16000"), IDR),
        grants=grants,
        base_amount=base_amount,
        bonus_amount=bonus_amount,
        first_purchase_bonus=first_purchase_bonus,
    )


def test_total_amount_includes_regular_bonus() -> None:
    package = _package(bonus_amount=10, first_purchase_bonus=5)
    assert package.total_amount == 70
    assert package.first_purchase_total == 75


def test_package_requires_real_price() -> None:
    with pytest.raises(ValueError):
        _package(price=Money(Decimal("16000"), DIAMOND))


def test_package_requires_game_grants() -> None:
    with pytest.raises(ValueError):
        _package(grants=IDR)


def test_package_rejects_non_positive_amounts() -> None:
    with pytest.raises(ValueError):
        _package(base_amount=0)
    with pytest.raises(ValueError):
        _package(bonus_amount=-1)
    with pytest.raises(ValueError):
        _package(price=Money(Decimal("0"), IDR))
