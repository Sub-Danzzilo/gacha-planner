from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PityConfig:
    """Pity rules for one tier.

    Convention used across the project: ``pity_count`` is the number of consecutive failed pulls
    since the last hit, so the next pull is pull number ``pity_count + 1``. Hard pity ``H`` means
    pull ``H`` is guaranteed to hit, that is when ``pity_count == H - 1``.

    Soft pity that starts at pull ``S`` raises the rate by ``soft_pity_step`` on pull ``S``, by
    ``2 * soft_pity_step`` on pull ``S + 1``, and so on, capped at 1.0.
    """

    hard_pity: int | None = None
    soft_pity_start: int | None = None
    soft_pity_step: float = 0.0

    def __post_init__(self) -> None:
        if self.hard_pity is not None and self.hard_pity < 1:
            raise ValueError("Hard pity must be at least 1")
        if self.soft_pity_step < 0:
            raise ValueError("Soft pity step cannot be negative")
        if self.soft_pity_start is not None:
            if self.soft_pity_start < 1:
                raise ValueError("Soft pity must start at pull 1 or later")
            if self.soft_pity_step <= 0:
                raise ValueError("Soft pity requires soft_pity_step greater than 0")
            if self.hard_pity is not None and self.soft_pity_start >= self.hard_pity:
                raise ValueError("Soft pity must start before hard pity")

    def effective_rate(self, base_rate: float, pity_count: int) -> float:
        if not 0.0 < base_rate <= 1.0:
            raise ValueError("Base rate must be between 0 (exclusive) and 1")
        if pity_count < 0:
            raise ValueError("Pity count cannot be negative")
        pull_number = pity_count + 1
        if self.hard_pity is not None and pull_number >= self.hard_pity:
            return 1.0
        if self.soft_pity_start is not None and pull_number >= self.soft_pity_start:
            steps = pull_number - self.soft_pity_start + 1
            return min(1.0, base_rate + self.soft_pity_step * steps)
        return base_rate


@dataclass(frozen=True, slots=True)
class FeaturedGuarantee:
    """The 50/50 rule: a hit on this tier yields the featured item with ``win_chance``.

    If the player loses and ``guaranteed_after_loss`` is on, the next hit is certainly featured.
    """

    win_chance: float
    guaranteed_after_loss: bool = True

    def __post_init__(self) -> None:
        if not 0.0 < self.win_chance <= 1.0:
            raise ValueError("win_chance must be between 0 (exclusive) and 1")


@dataclass(frozen=True, slots=True)
class PityState:
    """The player's starting condition: pity already built up and guarantee status."""

    pity_count: int = 0
    guaranteed_featured: bool = False

    def __post_init__(self) -> None:
        if self.pity_count < 0:
            raise ValueError("Pity count cannot be negative")


@dataclass(frozen=True, slots=True)
class PullRule:
    """The only input the calculators and the simulator need for one tier.

    ``effective_rate`` is the chance for a single pull, not cumulative; cumulative chance lives in
    ``core/calculators``.
    """

    base_rate: float
    pity: PityConfig | None = None
    guarantee: FeaturedGuarantee | None = None

    def __post_init__(self) -> None:
        if not 0.0 < self.base_rate <= 1.0:
            raise ValueError("Base rate must be between 0 (exclusive) and 1")

    def effective_rate(self, pity_count: int) -> float:
        if self.pity is None:
            return self.base_rate
        return self.pity.effective_rate(self.base_rate, pity_count)

    def featured_chance(self, guaranteed: bool) -> float:
        if self.guarantee is None or guaranteed:
            return 1.0
        return self.guarantee.win_chance

    def guaranteed_flag_after_loss(self) -> bool:
        if self.guarantee is None:
            return False
        return self.guarantee.guaranteed_after_loss
