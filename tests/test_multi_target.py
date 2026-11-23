import random
from decimal import Decimal

import pytest

from core.calculators.multi_target import MultiTargetEstimator, MultiTargetSpec
from core.models.banner import Banner, RateTier
from core.models.currency import Currency, CurrencyKind, Money
from core.models.item import Item
from core.models.pity import PullRule
from core.simulator import GachaSimulator

DIAMOND = Currency(code="DIAMOND", name="Diamond", kind=CurrencyKind.GAME)


def _banner(items: tuple[Item, ...], rate: float = 1.0) -> Banner:
    return Banner(
        name="Test",
        tiers=(RateTier(name="5-star", rule=PullRule(base_rate=rate)),),
        items=items,
        cost_per_pull=Money(Decimal("160"), DIAMOND),
    )


def _simulator(banner: Banner, seed: int = 1) -> GachaSimulator:
    return GachaSimulator(banner, "5-star", random.Random(seed))


def test_collects_all_copies_when_pool_has_one_item() -> None:
    banner = _banner((Item(name="Sword", tier_name="5-star"),))
    estimator = MultiTargetEstimator(_simulator(banner), MultiTargetSpec((("Sword", 2),)))
    point, lower, upper = estimator.success_probability(pulls=2, trials=20)
    assert point == 1.0
    assert lower < 1.0
    assert upper == 1.0


def test_insufficient_pulls_never_succeeds() -> None:
    banner = _banner((Item(name="Sword", tier_name="5-star"),))
    estimator = MultiTargetEstimator(_simulator(banner, 2), MultiTargetSpec((("Sword", 3),)))
    point, lower, upper = estimator.success_probability(pulls=2, trials=20)
    assert point == 0.0
    assert lower == 0.0
    assert upper > 0.0


def test_unknown_target_is_rejected() -> None:
    banner = _banner((Item(name="Sword", tier_name="5-star"),))
    with pytest.raises(ValueError):
        MultiTargetEstimator(_simulator(banner), MultiTargetSpec((("Spear", 1),)))


def test_empty_target_spec_is_rejected() -> None:
    with pytest.raises(ValueError):
        MultiTargetSpec(())


def test_duplicate_target_and_zero_copies_are_rejected() -> None:
    with pytest.raises(ValueError):
        MultiTargetSpec((("Sword", 1), ("Sword", 2)))
    with pytest.raises(ValueError):
        MultiTargetSpec((("Sword", 0),))


def test_invalid_arguments_are_rejected() -> None:
    banner = _banner((Item(name="Sword", tier_name="5-star"),))
    estimator = MultiTargetEstimator(_simulator(banner), MultiTargetSpec((("Sword", 1),)))
    with pytest.raises(ValueError):
        estimator.success_probability(pulls=-1, trials=10)
    with pytest.raises(ValueError):
        estimator.success_probability(pulls=1, trials=0)
