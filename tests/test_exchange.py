# Tests for core/exchange.py. Phase 2.
#
# Cases:
#   - manual rate and its implicit inverse
#   - identity conversion returns the same amount
#   - missing pair raises MissingExchangeRateError
#   - converting a game currency raises InvalidCurrencyError
#   - rounding for display uses ROUND_HALF_UP while the internal value keeps full precision
