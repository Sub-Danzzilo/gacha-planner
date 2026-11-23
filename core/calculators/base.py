from __future__ import annotations

import abc

from core.models.pity import PityState

DEFAULT_MAX_PULLS = 2000


class PullCalculator(abc.ABC):
    """Contract for every probability calculator. Calculators only know pull counts."""

    @abc.abstractmethod
    def success_probability(self, pulls: int, state: PityState) -> float:
        """Chance of getting the target at least once within ``pulls`` pulls."""

    @abc.abstractmethod
    def pulls_for_confidence(
        self, confidence: float, state: PityState, max_pulls: int = DEFAULT_MAX_PULLS
    ) -> int | None:
        """The fewest pulls whose success chance reaches ``confidence``."""

    @abc.abstractmethod
    def expected_pulls(self, state: PityState) -> float:
        """Average number of pulls until the first target."""

    @abc.abstractmethod
    def cumulative_curve(self, max_pulls: int, state: PityState) -> list[float]:
        """Index ``i`` holds the chance of success within ``i + 1`` pulls."""

    @staticmethod
    def validate_confidence(confidence: float) -> None:
        if not 0.0 < confidence < 1.0:
            raise ValueError("Confidence must be between 0 and 1 (both exclusive)")

    @staticmethod
    def validate_pulls(pulls: int) -> None:
        if pulls < 0:
            raise ValueError("Pull count cannot be negative")

    @staticmethod
    def validate_max_pulls(max_pulls: int) -> None:
        if max_pulls < 1:
            raise ValueError("max_pulls must be at least 1")
