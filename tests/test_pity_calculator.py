import random
from collections.abc import Sequence
from decimal import Decimal

import pytest

from core.calculators.pity_dp import PityCalculator
from core.calculators.simple import SimpleCalculator
from core.models.banner import Banner, RateTier
from core.models.currency import Currency, CurrencyKind, Money
from core.models.pity import FeaturedGuarantee, PityConfig, PityState, PullRule
from core.simulator import GachaSimulator

INITIAL = PityState()
DIAMOND = Currency(code="DIAMOND", name="Diamond", kind=CurrencyKind.GAME)


def _brute_force_cdf(rates: Sequence[float]) -> list[float]:
    """Cdf directly from the per-pull rates, without the DP."""
    survival = 1.0
    running = 0.0
    cdf: list[float] = []
    for rate in rates:
        running += survival * rate
        survival *= 1.0 - rate
        cdf.append(running)
    return cdf


def test_without_pity_matches_simple_calculator() -> None:
    pity_calculator = PityCalculator(PullRule(base_rate=0.3))
    simple = SimpleCalculator(0.3)
    for pulls in (0, 1, 5, 20):
        assert pity_calculator.success_probability(pulls, INITIAL) == pytest.approx(
            simple.success_probability(pulls, INITIAL), abs=1e-9
        )
    assert pity_calculator.pulls_for_confidence(0.9, INITIAL) == simple.pulls_for_confidence(
        0.9, INITIAL
    )
    assert pity_calculator.expected_pulls(INITIAL) == pytest.approx(
        simple.expected_pulls(INITIAL), rel=1e-9
    )


def test_hard_pity_is_certain_at_the_declared_pull() -> None:
    calculator = PityCalculator(PullRule(base_rate=0.5, pity=PityConfig(hard_pity=3)))
    assert calculator.success_probability(2, INITIAL) == pytest.approx(0.75)
    assert calculator.success_probability(3, INITIAL) == pytest.approx(1.0)
    assert calculator.cumulative_curve(5, INITIAL) == pytest.approx([0.5, 0.75, 1.0, 1.0, 1.0])
    assert calculator.expected_pulls(INITIAL) == pytest.approx(1.75)


def test_soft_pity_matches_brute_force() -> None:
    rule = PullRule(
        base_rate=0.1, pity=PityConfig(hard_pity=5, soft_pity_start=3, soft_pity_step=0.2)
    )
    calculator = PityCalculator(rule)
    expected = _brute_force_cdf([0.1, 0.1, 0.3, 0.5, 1.0])
    assert calculator.cumulative_curve(5, INITIAL) == pytest.approx(expected)
    assert calculator.expected_pulls(INITIAL) == pytest.approx(3.5605, abs=1e-9)


def test_soft_and_hard_pity_boundaries() -> None:
    rule = PullRule(
        base_rate=0.1, pity=PityConfig(hard_pity=5, soft_pity_start=3, soft_pity_step=0.2)
    )
    calculator = PityCalculator(rule)
    curve = calculator.cumulative_curve(6, INITIAL)
    assert curve[2] == pytest.approx(0.433)
    assert curve[3] == pytest.approx(0.7165)
    assert curve[4] == pytest.approx(1.0)
    assert curve[5] == pytest.approx(1.0)


def test_starting_pity_shifts_distribution() -> None:
    rule = PullRule(
        base_rate=0.1, pity=PityConfig(hard_pity=5, soft_pity_start=3, soft_pity_step=0.2)
    )
    calculator = PityCalculator(rule)
    fresh = calculator.cumulative_curve(5, INITIAL)
    advanced = calculator.cumulative_curve(5, PityState(pity_count=3))
    assert advanced[0] == pytest.approx(0.5)
    assert advanced[0] > fresh[0]


def test_fifty_fifty_guarantee_expected_pulls() -> None:
    rule = PullRule(base_rate=0.5, guarantee=FeaturedGuarantee(win_chance=0.5))
    calculator = PityCalculator(rule)
    # One hit takes 2 pulls on average. The first hit wins 50% of the time, so the expected
    # number of hits is 1.5 and the total is 3.
    assert calculator.expected_pulls(INITIAL) == pytest.approx(3.0, abs=1e-6)
    assert calculator.success_probability(1, INITIAL) == pytest.approx(0.25)


def test_starting_guaranteed_flag_is_certain_on_first_hit() -> None:
    rule = PullRule(base_rate=0.5, guarantee=FeaturedGuarantee(win_chance=0.5))
    calculator = PityCalculator(rule)
    assert calculator.success_probability(2, PityState(guaranteed_featured=True)) == pytest.approx(
        0.75
    )


def test_truncation_tail_is_corrected_in_expected_pulls() -> None:
    calculator = PityCalculator(PullRule(base_rate=0.001))
    assert calculator.expected_pulls(INITIAL) == pytest.approx(1000.0, abs=0.5)


def test_confidence_beyond_limit_returns_none() -> None:
    calculator = PityCalculator(PullRule(base_rate=0.5))
    assert calculator.pulls_for_confidence(0.9, INITIAL, max_pulls=1) is None


def test_matches_simulator_with_fixed_seed() -> None:
    banner = Banner(
        name="Test",
        tiers=(
            RateTier(
                name="5-star",
                rule=PullRule(base_rate=0.05, pity=PityConfig(hard_pity=20)),
            ),
        ),
        items=(),
        cost_per_pull=Money(Decimal("160"), DIAMOND),
    )
    calculator = PityCalculator(banner.tier("5-star").rule)
    simulator = GachaSimulator(banner, "5-star", random.Random(2024))
    result = simulator.run(trials=4000)
    assert result.mean() == pytest.approx(calculator.expected_pulls(INITIAL), rel=0.05)
    assert result.probability_within(10) == pytest.approx(
        calculator.success_probability(10, INITIAL), abs=0.03
    )
