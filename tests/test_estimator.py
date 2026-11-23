from datetime import datetime

import pytest

from core.estimator import RateEstimator, wilson_interval
from core.models.pull_log import PullLog, PullRecord


def test_wilson_matches_reference_value() -> None:
    lower, upper = wilson_interval(3, 200)
    assert lower == pytest.approx(0.0051, abs=0.001)
    assert upper == pytest.approx(0.0432, abs=0.001)


def test_wilson_stays_inside_unit_interval() -> None:
    lower, upper = wilson_interval(0, 100)
    assert lower == 0.0
    assert 0.0 < upper < 0.1
    lower, upper = wilson_interval(100, 100)
    assert upper == 1.0
    assert 0.9 < lower < 1.0


def test_wilson_rejects_empty_sample() -> None:
    with pytest.raises(ValueError):
        wilson_interval(0, 0)


def test_wilson_rejects_impossible_counts() -> None:
    with pytest.raises(ValueError):
        wilson_interval(5, 3)


def test_estimate_describe() -> None:
    estimate = RateEstimator().estimate(3, 200)
    text = estimate.describe()
    assert "1.5%" in text
    assert "200 pull" in text
    assert estimate.point == pytest.approx(0.015)


def test_estimate_from_log_counts_tier_hits() -> None:
    records = [
        PullRecord(
            banner_name="A",
            tier_name="5-star" if index < 3 else "3-star",
            item_name=None,
            pulled_at=datetime(2026, 1, 1),
        )
        for index in range(200)
    ]
    estimate = RateEstimator().estimate_from_log(PullLog(records), "5-star")
    assert estimate.trials == 200
    assert estimate.point == pytest.approx(0.015)
