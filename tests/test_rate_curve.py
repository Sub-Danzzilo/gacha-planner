# Tests for core/rate_curve.py. Phase 1.
#
# Cases:
#   - FlatRateCurve returns the same rate for any pity and has no hard pity
#   - LinearSoftPityCurve: base rate before the soft pity start, linear rise after, capped at
#     1.0, exactly 1.0 at hard pity
#   - HardPityOnlyCurve: flat then 1.0 on the hard pity pull
#   - TableRateCurve: explicit rates, last entry reused beyond the table
#   - invalid inputs (rate outside [0, 1], soft pity start above hard pity) raise the right
#     domain exception
