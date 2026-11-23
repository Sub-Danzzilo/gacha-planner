from datetime import date
from decimal import Decimal

import pytest

from core.models.banner import Banner, RateTier
from core.models.currency import Currency, CurrencyKind, CurrencyMismatchError, Money
from core.models.item import Item
from core.models.pity import PullRule

DIAMOND = Currency(code="DIAMOND", name="Diamond", kind=CurrencyKind.GAME)
IDR = Currency(code="IDR", name="Rupiah", kind=CurrencyKind.REAL)


def _banner(
    items: tuple[Item, ...] = (),
    cost: Money | None = None,
    tiers: tuple[RateTier, ...] | None = None,
) -> Banner:
    return Banner(
        name="Test banner",
        tiers=tiers or (RateTier(name="5-star", rule=PullRule(base_rate=0.6)),),
        items=items,
        cost_per_pull=cost or Money(Decimal("160"), DIAMOND),
    )


def test_banner_accepts_valid_definition() -> None:
    banner = _banner(items=(Item(name="Sword", tier_name="5-star", is_featured=True),))
    assert banner.tier("5-star").rule.base_rate == pytest.approx(0.6)
    assert banner.ends_on is None


def test_banner_keeps_deadline() -> None:
    banner = Banner(
        name="Banner",
        tiers=(RateTier(name="5-star", rule=PullRule(base_rate=0.6)),),
        items=(),
        cost_per_pull=Money(Decimal("160"), DIAMOND),
        ends_on=date(2026, 12, 31),
    )
    assert banner.ends_on == date(2026, 12, 31)


def test_banner_rejects_duplicate_tier_names() -> None:
    tiers = (
        RateTier(name="5-star", rule=PullRule(base_rate=0.6)),
        RateTier(name="5-star", rule=PullRule(base_rate=0.5)),
    )
    with pytest.raises(ValueError):
        _banner(tiers=tiers)


def test_banner_rejects_item_with_unknown_tier() -> None:
    with pytest.raises(ValueError):
        _banner(items=(Item(name="Sword", tier_name="4-star"),))


def test_banner_requires_game_currency_cost() -> None:
    with pytest.raises(ValueError):
        _banner(cost=Money(Decimal("1"), IDR))


def test_banner_requires_positive_cost() -> None:
    with pytest.raises(ValueError):
        _banner(cost=Money(Decimal("0"), DIAMOND))


def test_banner_requires_at_least_one_tier() -> None:
    with pytest.raises(ValueError):
        Banner(
            name="Empty",
            tiers=(),
            items=(),
            cost_per_pull=Money(Decimal("160"), DIAMOND),
        )


def test_unknown_tier_raises_key_error() -> None:
    with pytest.raises(KeyError):
        _banner().tier("4-star")


def test_items_for_tier_filters_items() -> None:
    banner = _banner(
        items=(
            Item(name="Sword", tier_name="5-star"),
            Item(name="Spear", tier_name="5-star"),
            Item(name="Shield", tier_name="4-star"),
        ),
        tiers=(
            RateTier(name="5-star", rule=PullRule(base_rate=0.6)),
            RateTier(name="4-star", rule=PullRule(base_rate=0.5)),
        ),
    )
    names = [item.name for item in banner.items_for_tier("5-star")]
    assert names == ["Sword", "Spear"]


def test_pulls_affordable_uses_floor_division() -> None:
    banner = _banner()
    assert banner.pulls_affordable(Money(Decimal("16000"), DIAMOND)) == 100
    assert banner.pulls_affordable(Money(Decimal("159"), DIAMOND)) == 0


def test_pulls_affordable_rejects_other_currency() -> None:
    with pytest.raises(CurrencyMismatchError):
        _banner().pulls_affordable(Money(Decimal("16000"), IDR))
