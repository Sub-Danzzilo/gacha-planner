from __future__ import annotations

import math

from core.calculators.base import DEFAULT_MAX_PULLS, PullCalculator
from core.models.pity import PityState


class SimpleCalculator(PullCalculator):
    """Closed-form calculator for a banner without pity.

    ``PityState`` is ignored because without pity the result does not depend on pull history.
    """

    def __init__(self, rate: float) -> None:
        if not 0.0 < rate <= 1.0:
            raise ValueError("Rate must be between 0 (exclusive) and 1")
        self._rate = rate

    def success_probability(self, pulls: int, state: PityState) -> float:
        self.validate_pulls(pulls)
        if pulls == 0:
            return 0.0
        if self._rate >= 1.0:
            return 1.0
        return -math.expm1(pulls * math.log1p(-self._rate))

    def pulls_for_confidence(
        self, confidence: float, state: PityState, max_pulls: int = DEFAULT_MAX_PULLS
    ) -> int | None:
        self.validate_confidence(confidence)
        self.validate_max_pulls(max_pulls)
        if self._rate >= 1.0:
            return 1
        needed = math.ceil(math.log1p(-confidence) / math.log1p(-self._rate))
        return needed if needed <= max_pulls else None

    def expected_pulls(self, state: PityState) -> float:
        return 1.0 / self._rate

    def cumulative_curve(self, max_pulls: int, state: PityState) -> list[float]:
        self.validate_max_pulls(max_pulls)
        if self._rate >= 1.0:
            return [1.0] * max_pulls
        survival_step = math.log1p(-self._rate)
        return [-math.expm1(n * survival_step) for n in range(1, max_pulls + 1)]
