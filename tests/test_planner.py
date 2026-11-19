# Tests for core/planner.py. Phase 2.
#
# Cases:
#   - projected balance with daily and weekly income over a known date range
#   - one-time income lands on the right day
#   - required_daily_income is zero when the balance already suffices
#   - shortfall math at the boundaries (deadline today, deadline in the past raises)
#   - no call to date.today(); all dates come from arguments
