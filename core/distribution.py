# Probability distribution over "number of pulls needed". Phase 1 (extended in phase 3).
#
# This is the shared result type. Both the exact calculator and the Monte Carlo simulator
# produce a `PullDistribution`, which is what makes them directly comparable in tests.
#
# Class `PullDistribution`:
#   - Constructed from a probability mass function: `pmf: Sequence[float]` where `pmf[n]` is the
#     probability that the target is obtained on exactly pull number `n` (index 0 is always 0.0).
#   - Also stores `tail_mass: float`, the probability mass beyond the last index (used when the
#     DP or simulation is truncated at `max_pulls`). `sum(pmf) + tail_mass` must be 1.0 within
#     1e-9; validate and raise `InvalidRateError` otherwise.
#   - `max_pulls -> int`
#   - `probability_exactly(n: int) -> float`
#   - `probability_within(n: int) -> float`        cumulative probability of success in <= n pulls
#   - `pulls_for_confidence(confidence: float) -> int | None`
#         smallest n with `probability_within(n) >= confidence`; None if the truncated range
#         never reaches it
#   - `expected_pulls() -> float`
#         if `tail_mass` is above 1e-6, raise or return a clearly flagged lower bound; do not
#         silently return a biased number
#   - `cumulative_curve() -> list[float]`          for charting (phase 3)
#   - `@classmethod from_samples(cls, samples: Sequence[int], max_pulls: int) -> PullDistribution`
#         builds the empirical distribution from simulator output
#   - Phase 3: `convolve(self, other: PullDistribution) -> PullDistribution`
#         distribution of the sum of two independent stages (used for multiple copies)
#
# Keep it immutable. Store the pmf as a tuple. No plotting code here.
