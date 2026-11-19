# Exact probability calculations. Phase 1 (extended in phases 2 and 3).
#
# Class `ProbabilityCalculator`:
#   - `__init__(self, banner: Banner, max_pulls: int = 2000)`
#
#   - `distribution(self, starting_pity: int = 0) -> PullDistribution`
#         Distribution of the pull number at which the first target-tier success happens.
#         Use the closed form when the curve is a `FlatRateCurve`:
#             P(first success on pull n) = (1 - p) ** (n - 1) * p
#         For every other curve use a forward DP over the pity counter:
#             survive[k] = probability of having failed k times so far
#             hit at pull k+1 = survive[k] * curve.rate_at(k)
#             survive[k+1] = survive[k] * (1 - curve.rate_at(k))
#         Start the DP at `starting_pity`. Stop at `max_pulls` and record the leftover survival
#         probability as `tail_mass`. Complexity must be O(max_pulls); do not use recursion.
#
#   - `success_probability(self, pulls: int, starting_pity: int = 0) -> float`
#         Chance of at least one success within `pulls` pulls. Shortcut for
#         `distribution(...).probability_within(pulls)`.
#
#   - `pulls_for_confidence(self, confidence: float, starting_pity: int = 0) -> int`
#         Smallest pull count reaching the confidence level. Raise `InvalidRateError` if the
#         confidence is outside (0, 1). If the range is truncated, raise rather than guess.
#
#   - `expected_pulls(self, starting_pity: int = 0) -> float`
#
# Phase 2 additions:
#   - Support `Banner.guarantee` by extending the DP state to `(pity, guaranteed_flag)` where the
#     target is the featured item. A target-tier success is featured with probability
#     `featured_share` unless `guaranteed_flag` is set, in which case it is certain; a
#     non-featured success sets the flag if the rule carries over.
#   - Accept an initial `guaranteed_flag` so players can enter "I lost my last 50/50".
#
# Phase 3 additions:
#   - `distribution_for_copies(self, copies: int, ...) -> PullDistribution`
#         Same DP with an extra state dimension for copies collected, or repeated convolution
#         when the state carries over correctly; pick one and justify it in a short comment.
#   - Multiple distinct targets: design the public method signature now, implement after the
#     single-target path is tested.
#
# Rules:
#   - Pure functions of the inputs. No I/O, no randomness, no caching that changes results.
#   - Use `float` for probabilities. Guard against underflow by working in plain floats; if a
#     very long run would underflow, stop at `max_pulls` and report `tail_mass` instead.
