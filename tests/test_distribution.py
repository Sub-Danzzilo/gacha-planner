# Tests for core/distribution.py. Phase 1.
#
# Cases (hand-computable first):
#   - pmf for a flat 0.5 rate truncated at 2 pulls: probability_within(1) == 0.5,
#     probability_within(2) == 0.75, tail_mass == 0.25
#   - pulls_for_confidence returns the smallest n reaching the level and None when truncated
#     before reaching it
#   - expected_pulls for a flat rate matches 1 / p within a small tolerance on a long range
#   - constructor rejects a pmf whose total mass differs from 1 by more than 1e-9
#   - from_samples builds the right counts and moves samples above max_pulls into tail_mass
#   - phase 3: convolve of two flat-rate distributions matches the negative binomial pmf
