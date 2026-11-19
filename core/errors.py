# Domain exceptions. Phase 1.
#
# Define a small hierarchy rooted at `GachaPlannerError(Exception)`:
#   - `InvalidRateError`        rate or probability outside [0, 1], or a curve that is not monotonic
#                               where the rule requires it
#   - `InvalidBannerError`      inconsistent banner definition (tier rates summing above 1,
#                               hard pity lower than soft pity, empty tier, unknown target item)
#   - `InvalidCurrencyError`    unknown currency, negative amount, mixing real and game currency
#                               without a conversion
#   - `MissingExchangeRateError`  no manual rate available for a currency pair (phase 2)
#   - `UnreachableTargetError`  a target cannot be reached under the given budget model (phase 2)
#   - `StorageError`            unreadable, corrupt or unsupported-version profile file
#
# Rules:
#   - Each exception takes a clear message built by the caller; no formatting logic in here.
#   - Do not add exception classes that nothing raises.
