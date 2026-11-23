from __future__ import annotations

from core.calculators.base import DEFAULT_MAX_PULLS, PullCalculator
from core.models.pity import PityState, PullRule

_TAIL_EPSILON = 1e-12


class PityCalculator(PullCalculator):
    """Pity and featured-guarantee calculator using a forward DP over states.

    The state per pull is ``(pity_count, guaranteed_featured)``. Without hard pity the
    distribution is cut at ``max_pulls`` and the remaining tail mass is not counted, so the cdf can
    be slightly below its true value.
    """

    def __init__(self, rule: PullRule) -> None:
        self._rule = rule
        self._cache: dict[tuple[PityState, int], tuple[float, ...]] = {}

    def success_probability(self, pulls: int, state: PityState) -> float:
        self.validate_pulls(pulls)
        if pulls == 0:
            return 0.0
        return sum(self._pmf(state, max(pulls, DEFAULT_MAX_PULLS))[: pulls + 1])

    def pulls_for_confidence(
        self, confidence: float, state: PityState, max_pulls: int = DEFAULT_MAX_PULLS
    ) -> int | None:
        self.validate_confidence(confidence)
        self.validate_max_pulls(max_pulls)
        running = 0.0
        for pull, mass in enumerate(self._pmf(state, max_pulls)):
            if pull == 0:
                continue
            running += mass
            if running >= confidence:
                return pull
        return None

    def expected_pulls(self, state: PityState) -> float:
        pmf = self._pmf(state, DEFAULT_MAX_PULLS)
        expected = sum(pull * mass for pull, mass in enumerate(pmf))
        tail = 1.0 - sum(pmf)
        if tail > _TAIL_EPSILON:
            # The tail is approximated like a memoryless process at the final rate: the expected
            # extra pulls after N failures is 1 / rate.
            rate = self._rule.effective_rate(self._pity_cap(state.pity_count))
            expected += tail * (DEFAULT_MAX_PULLS + 1.0 / rate)
        return expected

    def cumulative_curve(self, max_pulls: int, state: PityState) -> list[float]:
        self.validate_max_pulls(max_pulls)
        curve: list[float] = []
        running = 0.0
        for pull, mass in enumerate(self._pmf(state, max_pulls)):
            if pull == 0:
                continue
            running += mass
            curve.append(running)
        return curve

    def _pmf(self, state: PityState, max_pulls: int) -> tuple[float, ...]:
        key = (state, max_pulls)
        cached = self._cache.get(key)
        if cached is None:
            cached = self._build_pmf(state, max_pulls)
            self._cache[key] = cached
        return cached

    def _build_pmf(self, state: PityState, max_pulls: int) -> tuple[float, ...]:
        cap = self._pity_cap(state.pity_count)
        pmf = [0.0] * (max_pulls + 1)
        current: dict[tuple[int, bool], float] = {
            (min(state.pity_count, cap), state.guaranteed_featured): 1.0
        }
        for pull in range(1, max_pulls + 1):
            following: dict[tuple[int, bool], float] = {}
            obtained = 0.0
            for (pity, guaranteed), mass in current.items():
                rate = self._rule.effective_rate(pity)
                hit_mass = mass * rate
                if hit_mass > 0.0:
                    won_mass = hit_mass * self._rule.featured_chance(guaranteed)
                    obtained += won_mass
                    lost_mass = hit_mass - won_mass
                    if lost_mass > 0.0:
                        self._accumulate(
                            following,
                            (0, self._rule.guaranteed_flag_after_loss()),
                            lost_mass,
                        )
                miss_mass = mass * (1.0 - rate)
                if miss_mass > 0.0:
                    self._accumulate(following, (min(pity + 1, cap), guaranteed), miss_mass)
            pmf[pull] = obtained
            current = following
            if not current:
                break
        return tuple(pmf)

    @staticmethod
    def _accumulate(
        states: dict[tuple[int, bool], float], key: tuple[int, bool], mass: float
    ) -> None:
        states[key] = states.get(key, 0.0) + mass

    def _pity_cap(self, starting_pity: int) -> int:
        """Highest pity counter worth tracking.

        Once soft pity without hard pity reaches rate 1.0 the hit is certain, so the state does not
        need to grow further.
        """
        pity = self._rule.pity
        if pity is None:
            return 0
        if pity.hard_pity is not None:
            return pity.hard_pity - 1
        cap = starting_pity
        while cap < DEFAULT_MAX_PULLS and self._rule.effective_rate(cap) < 1.0:
            cap += 1
        return cap
