import pytest

from core.models.pity import FeaturedGuarantee, PityConfig, PityState, PullRule


def test_flat_rate_without_pity() -> None:
    rule = PullRule(base_rate=0.013)
    assert rule.effective_rate(0) == pytest.approx(0.013)
    assert rule.effective_rate(500) == pytest.approx(0.013)


def test_hard_pity_is_certain_on_the_declared_pull() -> None:
    rule = PullRule(base_rate=0.5, pity=PityConfig(hard_pity=3))
    assert rule.effective_rate(0) == pytest.approx(0.5)
    assert rule.effective_rate(1) == pytest.approx(0.5)
    assert rule.effective_rate(2) == 1.0


def test_soft_pity_raises_rate_from_the_start_pull() -> None:
    rule = PullRule(
        base_rate=0.1, pity=PityConfig(hard_pity=5, soft_pity_start=3, soft_pity_step=0.2)
    )
    assert rule.effective_rate(0) == pytest.approx(0.1)
    assert rule.effective_rate(1) == pytest.approx(0.1)
    assert rule.effective_rate(2) == pytest.approx(0.3)
    assert rule.effective_rate(3) == pytest.approx(0.5)
    assert rule.effective_rate(4) == 1.0


def test_soft_pity_must_start_before_hard_pity() -> None:
    with pytest.raises(ValueError):
        PityConfig(hard_pity=5, soft_pity_start=5, soft_pity_step=0.1)


def test_soft_pity_without_step_is_invalid() -> None:
    with pytest.raises(ValueError):
        PityConfig(soft_pity_start=10)


def test_guarantee_chance_and_flag() -> None:
    rule = PullRule(base_rate=0.6, guarantee=FeaturedGuarantee(win_chance=0.5))
    assert rule.featured_chance(guaranteed=False) == pytest.approx(0.5)
    assert rule.featured_chance(guaranteed=True) == 1.0
    assert rule.guaranteed_flag_after_loss() is True


def test_guarantee_without_carry_over_does_not_set_flag() -> None:
    rule = PullRule(
        base_rate=0.6, guarantee=FeaturedGuarantee(win_chance=0.5, guaranteed_after_loss=False)
    )
    assert rule.guaranteed_flag_after_loss() is False


def test_rule_without_guarantee_always_gets_featured() -> None:
    assert PullRule(base_rate=0.6).featured_chance(guaranteed=False) == 1.0


@pytest.mark.parametrize("rate", [0.0, -0.1, 1.5])
def test_rule_rejects_invalid_base_rate(rate: float) -> None:
    with pytest.raises(ValueError):
        PullRule(base_rate=rate)


def test_state_rejects_negative_pity() -> None:
    with pytest.raises(ValueError):
        PityState(pity_count=-1)


def test_guarantee_rejects_invalid_win_chance() -> None:
    with pytest.raises(ValueError):
        FeaturedGuarantee(win_chance=0.0)
