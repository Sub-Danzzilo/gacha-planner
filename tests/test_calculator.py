# Tests for core/calculator.py. Phase 1 (guarantee and copies in later phases).
#
# Cases:
#   - flat 0.5 rate: success_probability(2) == 0.75
#   - flat rate: pulls_for_confidence(0.9) equals ceil(ln(0.1) / ln(1 - p)) for several rates,
#     including 0.013 (expected result 176)
#   - hard pity only: success probability is exactly 1.0 at the hard pity pull
#   - soft pity curve: DP result equals a brute-force product computation for a small case
#   - starting_pity shifts the distribution as expected
#   - truncation: a tiny max_pulls produces a nonzero tail_mass and expected_pulls refuses to
#     return a silently biased value
#   - phase 2: 50/50 guarantee against a hand-derived two-state result
#   - phase 3: two copies via the DP match convolution of two single-copy distributions when
#     the state carries over correctly
