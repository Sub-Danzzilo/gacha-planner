import random
from decimal import Decimal

import pytest

from core.calculators.pity_dp import PityCalculator
from core.models.banner import Banner, RateTier
from core.models.currency import Currency, CurrencyKind, Money
from core.models.item import Item
from core.models.pity import PityConfig, PityState, PullRule
from core.simulator import GachaSimulator, SimulationResult

DIAMOND = Currency(code="DIAMOND", name="Diamond", kind=CurrencyKind.GAME)
INITIAL = PityState()


class _NeverHits(random.Random):
    def random(self) -> float:
        return 0.999


def _banner(base_rate: float, hard_pity: int | None = None) -> Banner:
    pity = None if hard_pity is None else PityConfig(hard_pity=hard_pity)
    return Banner(
        name="Test",
        tiers=(RateTier(name="5-star", rule=PullRule(base_rate=base_rate, pity=pity)),),
        items=(Item(name="Sword", tier_name="5-star", is_featured=True),),
        cost_per_pull=Money(Decimal("160"), DIAMOND),
    )


def test_same_seed_gives_identical_samples() -> None:
    first = GachaSimulator(_banner(0.05), "5-star", random.Random(9)).run(trials=50)
    second = GachaSimulator(_banner(0.05), "5-star", random.Random(9)).run(trials=50)
    assert first.samples == second.samples


def test_mean_matches_calculator() -> None:
    banner = _banner(0.25)
    simulator = GachaSimulator(banner, "5-star", random.Random(77))
    result = simulator.run(trials=4000)
    calculator = PityCalculator(banner.tier("5-star").rule)
    assert result.mean() == pytest.approx(calculator.expected_pulls(INITIAL), rel=0.05)


def test_hard_pity_is_never_exceeded() -> None:
    simulator = GachaSimulator(_banner(0.01, hard_pity=5), "5-star", random.Random(4))
    result = simulator.run(trials=300)
    assert max(result.samples) <= 5


def test_progress_callback_ends_at_total() -> None:
    calls: list[tuple[int, int]] = []
    simulator = GachaSimulator(_banner(0.5), "5-star", random.Random(2))
    simulator.run(trials=250, progress_callback=lambda done, total: calls.append((done, total)))
    assert calls[-1] == (250, 250)
    assert len(calls) <= 102
    assert all(total == 250 for _, total in calls)


def test_non_positive_trials_is_rejected() -> None:
    simulator = GachaSimulator(_banner(0.5), "5-star", random.Random(1))
    with pytest.raises(ValueError):
        simulator.run(trials=0)


def test_non_positive_max_pulls_is_rejected() -> None:
    simulator = GachaSimulator(_banner(0.5), "5-star", random.Random(1))
    with pytest.raises(ValueError):
        simulator.run(trials=10, max_pulls=0)


def test_simulate_budget_matches_exact_probability() -> None:
    banner = _banner(0.1)
    simulator = GachaSimulator(banner, "5-star", random.Random(31))
    calculator = PityCalculator(banner.tier("5-star").rule)
    estimate = simulator.simulate_budget(10, trials=3000)
    assert estimate == pytest.approx(calculator.success_probability(10, INITIAL), abs=0.03)


def test_draw_item_always_hits_when_rate_is_one() -> None:
    banner = _banner(1.0)
    simulator = GachaSimulator(banner, "5-star", random.Random(5))
    states: dict[str, PityState] = {}
    item = simulator.draw_item(states)
    assert item is not None
    assert item.name == "Sword"
    assert states["5-star"] == PityState(0, False)


def test_draw_item_on_miss_increments_pity() -> None:
    banner = _banner(0.5)
    simulator = GachaSimulator(banner, "5-star", _NeverHits())
    states: dict[str, PityState] = {}
    assert simulator.draw_item(states) is None
    assert states["5-star"] == PityState(1, False)


def test_draw_item_skips_tier_without_items() -> None:
    banner = Banner(
        name="Test",
        tiers=(RateTier(name="5-star", rule=PullRule(base_rate=0.5)),),
        items=(),
        cost_per_pull=Money(Decimal("160"), DIAMOND),
    )
    simulator = GachaSimulator(banner, "5-star", random.Random(5))
    states: dict[str, PityState] = {}
    assert simulator.draw_item(states) is None
    assert states == {}


def test_simulation_result_helpers() -> None:
    result = SimulationResult(samples=(1, 2, 2, 4), max_pulls=10)
    assert result.mean() == pytest.approx(2.25)
    assert result.probability_within(2) == pytest.approx(0.75)
    assert result.quantile(0.5) == 2


def test_empty_samples_are_rejected() -> None:
    with pytest.raises(ValueError):
        SimulationResult(samples=(), max_pulls=10)
