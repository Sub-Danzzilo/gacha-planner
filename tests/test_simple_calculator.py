from itertools import pairwise

import pytest

from core.calculators.simple import SimpleCalculator
from core.models.pity import PityState

INITIAL = PityState()


def test_flat_rate_over_two_pulls() -> None:
    assert SimpleCalculator(0.5).success_probability(2, INITIAL) == pytest.approx(0.75)


def test_known_confidence_case() -> None:
    assert SimpleCalculator(0.013).pulls_for_confidence(0.9, INITIAL) == 176


def test_known_expected_pulls() -> None:
    assert SimpleCalculator(0.013).expected_pulls(INITIAL) == pytest.approx(76.923, abs=1e-3)


def test_zero_pulls_never_succeeds() -> None:
    assert SimpleCalculator(0.5).success_probability(0, INITIAL) == 0.0


def test_certain_rate_needs_one_pull() -> None:
    calculator = SimpleCalculator(1.0)
    assert calculator.success_probability(1, INITIAL) == 1.0
    assert calculator.pulls_for_confidence(0.99, INITIAL) == 1
    assert calculator.expected_pulls(INITIAL) == 1.0


def test_cumulative_curve_is_monotone() -> None:
    curve = SimpleCalculator(0.05).cumulative_curve(50, INITIAL)
    assert len(curve) == 50
    assert all(later >= earlier for earlier, later in pairwise(curve))
    assert curve[-1] == pytest.approx(1.0 - 0.95**50)


def test_confidence_not_reached_within_limit() -> None:
    assert SimpleCalculator(0.5).pulls_for_confidence(0.99, INITIAL, max_pulls=2) is None


@pytest.mark.parametrize("confidence", [0.0, 1.0, -0.1])
def test_invalid_confidence(confidence: float) -> None:
    with pytest.raises(ValueError):
        SimpleCalculator(0.5).pulls_for_confidence(confidence, INITIAL)


def test_negative_pulls() -> None:
    with pytest.raises(ValueError):
        SimpleCalculator(0.5).success_probability(-1, INITIAL)


@pytest.mark.parametrize("rate", [0.0, -0.5, 1.5])
def test_invalid_rate(rate: float) -> None:
    with pytest.raises(ValueError):
        SimpleCalculator(rate)


def test_state_is_ignored_without_pity() -> None:
    calculator = SimpleCalculator(0.5)
    assert calculator.success_probability(2, INITIAL) == calculator.success_probability(
        2, PityState(pity_count=40)
    )
