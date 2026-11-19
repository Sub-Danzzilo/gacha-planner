# Rate estimation from observed pulls. Phase 4.
#
# Class `RateEstimator`:
#   - `estimate(self, successes: int, trials: int, confidence: float = 0.95) -> RateEstimate`
#         Point estimate `successes / trials` plus a Wilson score interval. Implement the Wilson
#         formula directly with the standard library (use `statistics.NormalDist` for the z
#         value). Do not use the plain normal approximation; it behaves badly for small counts
#         and rates near 0.
#
#   - `estimate_from_log(self, log: PullLog, tier_name: str, confidence: float = 0.95,
#                        exclude_pity_pulls: bool = True) -> RateEstimate`
#         When the game has pity, the raw success fraction overestimates the base rate because
#         guaranteed pulls always succeed. With `exclude_pity_pulls`, drop pulls forced by hard
#         pity and any pulls the user marks as being in the soft-pity zone before estimating.
#         State this limitation in a short comment and in the docstring of this method.
#
# Class `RateEstimate` (frozen dataclass):
#   - `point: float`, `lower: float`, `upper: float`, `confidence: float`, `trials: int`
#   - method `describe(self) -> str` producing plain text such as
#     "about 1.5% (95% interval 0.6% to 3.4%, 200 pulls)"
#
# Rules:
#   - `trials == 0` raises `InvalidRateError`; do not return a made-up estimate.
#   - The UI should be able to feed the lower, point and upper values into
#     `ProbabilityCalculator` to show best, likely and worst cases.
