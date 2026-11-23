from decimal import Decimal

import pytest

from core.models.currency import Currency, CurrencyKind, Money
from core.models.topup import TopUpPackage
from core.topup_optimizer import TopUpOptimizer

DIAMOND = Currency(code="DIAMOND", name="Diamond", kind=CurrencyKind.GAME)
IDR = Currency(code="IDR", name="Rupiah", kind=CurrencyKind.REAL)
USD = Currency(code="USD", name="Dolar", kind=CurrencyKind.REAL, decimals=2)


def _package(
    price: str,
    amount: int,
    currency: Currency = IDR,
    bonus: int = 0,
    first_bonus: int = 0,
) -> TopUpPackage:
    return TopUpPackage(
        price=Money(Decimal(price), currency),
        grants=DIAMOND,
        base_amount=amount,
        bonus_amount=bonus,
        first_purchase_bonus=first_bonus,
    )


def test_exact_fit_with_one_package() -> None:
    plan = TopUpOptimizer([_package("16000", 60)]).cheapest_plan(60)
    assert plan.total_price == Money(Decimal("16000"), IDR)
    assert plan.total_received == 60
    assert plan.surplus == 0
    assert len(plan.purchases) == 1


def test_single_package_may_overshoot() -> None:
    plan = TopUpOptimizer([_package("16000", 60)]).cheapest_plan(100)
    assert plan.total_price == Money(Decimal("32000"), IDR)
    assert plan.total_received == 120
    assert plan.surplus == 20


def test_cheaper_large_package_wins_even_when_it_overshoots() -> None:
    small = _package("16000", 60)
    large = _package("75000", 330)
    plan = TopUpOptimizer([small, large]).cheapest_plan(300)
    assert plan.total_price == Money(Decimal("75000"), IDR)
    assert plan.total_received == 330
    assert plan.surplus == 30


def test_first_purchase_bonus_is_used_once() -> None:
    package = _package("10000", 50, first_bonus=30)
    optimizer = TopUpOptimizer([package])
    with_bonus = optimizer.cheapest_plan(70)
    assert with_bonus.total_price == Money(Decimal("10000"), IDR)
    assert with_bonus.total_received == 80
    without_bonus = optimizer.cheapest_plan(70, first_purchase_available=False)
    assert without_bonus.total_price == Money(Decimal("20000"), IDR)
    assert without_bonus.total_received == 100


def test_empty_requirement_returns_empty_plan() -> None:
    plan = TopUpOptimizer([_package("16000", 60)]).cheapest_plan(0)
    assert plan.purchases == ()
    assert plan.total_received == 0
    assert plan.surplus == 0
    assert plan.total_price.amount == Decimal(0)


def test_mixed_price_currencies_are_rejected() -> None:
    with pytest.raises(ValueError):
        TopUpOptimizer([_package("16000", 60), _package("5", 300, currency=USD)])


def test_empty_package_list_is_rejected() -> None:
    with pytest.raises(ValueError):
        TopUpOptimizer([])


def test_combination_matches_brute_force() -> None:
    cheap = _package("7", 3)
    big = _package("10", 5)
    plan = TopUpOptimizer([cheap, big]).cheapest_plan(8)
    # Options: 3 + 5 = 8 for 17, cheaper than 2 x 5 = 10 for 20.
    assert plan.total_price == Money(Decimal("17"), IDR)
    assert plan.total_received == 8
    assert plan.surplus == 0
    counts = {package.total_amount: count for package, count in plan.purchases}
    assert counts == {3: 1, 5: 1}


def test_tie_break_prefers_smaller_surplus() -> None:
    exact = _package("10", 5)
    overshoot = _package("20", 11)
    plan = TopUpOptimizer([exact, overshoot]).cheapest_plan(10)
    assert plan.total_price == Money(Decimal("20"), IDR)
    assert plan.surplus == 0
    assert plan.purchases == ((exact, 2),)
