from datetime import datetime

from core.models.pull_log import PullLog, PullRecord


def _record(tier: str, banner: str = "Banner A") -> PullRecord:
    return PullRecord(
        banner_name=banner,
        tier_name=tier,
        item_name=None,
        pulled_at=datetime(2026, 1, 1, 12, 0),
    )


def test_empty_log() -> None:
    log = PullLog()
    assert len(log) == 0
    assert log.total() == 0
    assert log.hits("5-star") == 0


def test_add_and_extend() -> None:
    log = PullLog([_record("5-star")])
    log.add(_record("3-star"))
    log.extend([_record("5-star"), _record("3-star")])
    assert log.total() == 4
    assert log.hits("5-star") == 2
    assert log.hits("4-star") == 0


def test_iteration_keeps_order() -> None:
    log = PullLog([_record("3-star"), _record("5-star")])
    tiers = [record.tier_name for record in log]
    assert tiers == ["3-star", "5-star"]


def test_for_banner_filters_records() -> None:
    log = PullLog([_record("3-star"), _record("5-star", banner="Banner B")])
    filtered = log.for_banner("Banner B")
    assert filtered.total() == 1
    assert log.total() == 2
