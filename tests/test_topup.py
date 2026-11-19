# Tests for core/topup.py. Phase 2.
#
# Cases:
#   - exact fit with one package
#   - cheaper-per-unit large package beats several small ones even when it overshoots
#   - first-time-only package is used at most once
#   - no packages available and needed > 0 raises the domain exception
#   - needed <= 0 returns an empty plan
#   - costs in different price currencies are compared after conversion
