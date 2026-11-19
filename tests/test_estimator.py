# Tests for core/estimator.py. Phase 4.
#
# Cases:
#   - Wilson interval against known reference values (for example 3 successes in 200 trials)
#   - interval always stays within [0, 1], including 0 successes and all successes
#   - trials == 0 raises the domain exception
#   - estimate_from_log with exclude_pity_pulls drops forced pulls
#   - describe() output format
