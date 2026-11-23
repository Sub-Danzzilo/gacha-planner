from __future__ import annotations

from dataclasses import dataclass

from core.estimator import wilson_interval
from core.models.pity import PityState
from core.simulator import GachaSimulator

_CONFIDENCE = 0.95


@dataclass(frozen=True, slots=True)
class MultiTargetSpec:
    """The list of targets and how many copies of each are needed."""

    targets: tuple[tuple[str, int], ...]

    def __post_init__(self) -> None:
        if not self.targets:
            raise ValueError("At least one target is required")
        names = [name for name, _ in self.targets]
        if len(set(names)) != len(names):
            raise ValueError("Target names must be unique")
        for name, copies in self.targets:
            if not name.strip():
                raise ValueError("Target name cannot be empty")
            if copies < 1:
                raise ValueError("Copy count must be at least 1")


class MultiTargetEstimator:
    """Chance of collecting every target within a number of pulls, estimated by simulation.

    Targets share the pool and pity, so their chances must not simply be multiplied. The result is
    always an estimate with a 95% confidence interval.
    """

    def __init__(self, simulator: GachaSimulator, spec: MultiTargetSpec) -> None:
        known = {item.name for item in simulator.banner.items}
        for name, _ in spec.targets:
            if name not in known:
                raise ValueError(f"Target {name!r} is not on banner {simulator.banner.name!r}")
        self._simulator = simulator
        self._spec = spec

    def success_probability(self, pulls: int, trials: int) -> tuple[float, float, float]:
        if pulls < 0:
            raise ValueError("Pull count cannot be negative")
        if trials <= 0:
            raise ValueError("Trial count must be greater than 0")
        successes = sum(1 for _ in range(trials) if self._collect_one(pulls))
        lower, upper = wilson_interval(successes, trials, _CONFIDENCE)
        return successes / trials, lower, upper

    def _collect_one(self, pulls: int) -> bool:
        remaining = dict(self._spec.targets)
        tier_states: dict[str, PityState] = {}
        for _ in range(pulls):
            item = self._simulator.draw_item(tier_states)
            if item is None:
                continue
            left = remaining.get(item.name, 0)
            if left == 0:
                continue
            remaining[item.name] = left - 1
            if all(count == 0 for count in remaining.values()):
                return True
        return False
