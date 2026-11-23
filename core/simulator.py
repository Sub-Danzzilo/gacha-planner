from __future__ import annotations

import math
import random
from collections.abc import Callable, MutableMapping
from dataclasses import dataclass

from core.models.banner import Banner, RateTier
from core.models.item import Item
from core.models.pity import PityState

_PROGRESS_STEPS = 100
_INITIAL_STATE = PityState()


@dataclass(frozen=True, slots=True)
class SimulationResult:
    """Pull counts sampled per trial and the pull bound used to display the histogram."""

    samples: tuple[int, ...]
    max_pulls: int

    def __post_init__(self) -> None:
        if not self.samples:
            raise ValueError("Simulation results need at least one sample")
        if self.max_pulls < 1:
            raise ValueError("max_pulls must be greater than 0")

    def mean(self) -> float:
        return sum(self.samples) / len(self.samples)

    def probability_within(self, pulls: int) -> float:
        if pulls < 0:
            raise ValueError("Pull count cannot be negative")
        return sum(1 for sample in self.samples if sample <= pulls) / len(self.samples)

    def quantile(self, probability: float) -> int:
        """Smallest pull reached by at least ``probability`` of the trials."""
        if not 0.0 < probability <= 1.0:
            raise ValueError("Quantile must be between 0 (exclusive) and 1")
        ordered = sorted(self.samples)
        index = min(len(ordered) - 1, math.ceil(probability * len(ordered)) - 1)
        return ordered[index]


class GachaSimulator:
    """Monte Carlo for a single target tier on a single banner."""

    def __init__(
        self,
        banner: Banner,
        tier_name: str,
        rng: random.Random,
        safety_cap: int = 100_000,
    ) -> None:
        if safety_cap < 1:
            raise ValueError("Safety cap must be at least 1 pull")
        self._banner = banner
        self._tier = banner.tier(tier_name)
        self._rng = rng
        self._safety_cap = safety_cap

    @property
    def banner(self) -> Banner:
        return self._banner

    def simulate_once(self, state: PityState = _INITIAL_STATE) -> int:
        pity = state.pity_count
        guaranteed = state.guaranteed_featured
        rule = self._tier.rule
        for pull in range(1, self._safety_cap + 1):
            if self._rng.random() < rule.effective_rate(pity):
                if self._rng.random() < rule.featured_chance(guaranteed):
                    return pull
                guaranteed = rule.guaranteed_flag_after_loss()
                pity = 0
            else:
                pity += 1
        raise ValueError(f"No hit within {self._safety_cap} pulls; check the rate and pity rules")

    def run(
        self,
        trials: int,
        max_pulls: int = 2000,
        state: PityState = _INITIAL_STATE,
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> SimulationResult:
        if trials <= 0:
            raise ValueError("Trial count must be greater than 0")
        if max_pulls <= 0:
            raise ValueError("max_pulls must be greater than 0")
        samples: list[int] = []
        step = max(1, math.ceil(trials / _PROGRESS_STEPS))
        for trial in range(1, trials + 1):
            samples.append(self.simulate_once(state))
            if progress_callback is not None and trial % step == 0:
                progress_callback(trial, trials)
        if progress_callback is not None:
            progress_callback(trials, trials)
        return SimulationResult(tuple(samples), max_pulls)

    def simulate_budget(self, pulls: int, trials: int, state: PityState = _INITIAL_STATE) -> float:
        if pulls < 0:
            raise ValueError("Pull count cannot be negative")
        if trials <= 0:
            raise ValueError("Trial count must be greater than 0")
        hits = sum(1 for _ in range(trials) if self.simulate_once(state) <= pulls)
        return hits / trials

    def draw_item(self, tier_states: MutableMapping[str, PityState]) -> Item | None:
        """One pull that resolves the first tier to hit, following the banner's declared order.

        Tiers that miss gain pity of their own; tiers after the first hit are not rolled on that
        pull.
        """
        for tier in self._banner.tiers:
            if not self._banner.items_for_tier(tier.name):
                continue
            state = tier_states.get(tier.name, PityState())
            if self._rng.random() < tier.rule.effective_rate(state.pity_count):
                item, featured = self._resolve_hit(tier, state)
                tier_states[tier.name] = PityState(
                    0, False if featured else tier.rule.guaranteed_flag_after_loss()
                )
                return item
            tier_states[tier.name] = PityState(state.pity_count + 1, state.guaranteed_featured)
        return None

    def _resolve_hit(self, tier: RateTier, state: PityState) -> tuple[Item, bool]:
        pool = self._banner.items_for_tier(tier.name)
        if tier.rule.guarantee is None:
            return self._rng.choice(pool), False
        won = self._rng.random() < tier.rule.featured_chance(state.guaranteed_featured)
        featured = [item for item in pool if item.is_featured]
        ordinary = [item for item in pool if not item.is_featured]
        if won and featured:
            return self._rng.choice(featured), True
        if ordinary:
            return self._rng.choice(ordinary), False
        return self._rng.choice(featured), False
