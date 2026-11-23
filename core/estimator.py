from __future__ import annotations

import math
from dataclasses import dataclass
from statistics import NormalDist

from core.models.pull_log import PullLog


@dataclass(frozen=True, slots=True)
class RateEstimate:
    point: float
    lower: float
    upper: float
    confidence: float
    trials: int

    def describe(self) -> str:
        return (
            f"about {self.point * 100:.1f}% "
            f"({self.confidence * 100:.0f}% interval "
            f"{self.lower * 100:.1f}% to {self.upper * 100:.1f}%, {self.trials} pulls)"
        )


def wilson_interval(successes: int, trials: int, confidence: float = 0.95) -> tuple[float, float]:
    """Wilson interval for a proportion; shared by the estimator and multi-target simulation."""
    if trials <= 0:
        raise ValueError("Trial count must be greater than 0")
    if not 0 <= successes <= trials:
        raise ValueError("Success count must be between 0 and the trial count")
    if not 0.0 < confidence < 1.0:
        raise ValueError("Confidence must be between 0 and 1 (both exclusive)")

    z = NormalDist().inv_cdf(1.0 - (1.0 - confidence) / 2.0)
    point = successes / trials
    denominator = 1.0 + z * z / trials
    center = (point + z * z / (2.0 * trials)) / denominator
    margin = z * math.sqrt(point * (1.0 - point) / trials + z * z / (4.0 * trials * trials))
    margin /= denominator
    lower = 0.0 if successes == 0 else max(0.0, center - margin)
    upper = 1.0 if successes == trials else min(1.0, center + margin)
    return lower, upper


class RateEstimator:
    """Estimates a rate from observed pulls."""

    def estimate(self, successes: int, trials: int, confidence: float = 0.95) -> RateEstimate:
        lower, upper = wilson_interval(successes, trials, confidence)
        return RateEstimate(
            point=successes / trials,
            lower=lower,
            upper=upper,
            confidence=confidence,
            trials=trials,
        )

    def estimate_from_log(
        self, log: PullLog, tier_name: str, confidence: float = 0.95
    ) -> RateEstimate:
        """Estimates one tier's rate from a pull log.

        If the game uses pity, this estimates the observed effective rate rather than the base
        rate: pulls forced by hard pity always succeed and push the estimate up.
        """
        return self.estimate(log.hits(tier_name), log.total(), confidence)
