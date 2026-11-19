# Per-pull success probability as a function of the pity counter. Phase 1.
#
# Pity counter convention: `pity` is the number of failed pulls since the last success, so the
# next pull has `pity + 1` as its pull number. Document this convention once at the top of the
# abstract class and use it everywhere.
#
# Abstract base class `RateCurve` (abc.ABC):
#   - `rate_at(self, pity: int) -> float`    probability that the next pull succeeds
#   - `hard_pity(self) -> int | None`         pull number at which success is certain, if any
#
# Implementations:
#   - `FlatRateCurve(base_rate: float)`
#         constant rate, no pity. `hard_pity()` returns None.
#   - `LinearSoftPityCurve(base_rate: float, soft_pity_start: int, step: float, hard_pity: int)`
#         base_rate before `soft_pity_start`, then increases by `step` per pull, capped at 1.0,
#         and is exactly 1.0 at `hard_pity`. Validate `soft_pity_start <= hard_pity` and
#         raise `InvalidBannerError` otherwise.
#   - `HardPityOnlyCurve(base_rate: float, hard_pity: int)`
#         flat until the hard pity pull, which is certain.
#   - `TableRateCurve(rates: Sequence[float])`
#         explicit per-pull rates supplied by the user for games with irregular soft pity.
#         Rates beyond the table length reuse the last entry; the final entry must be 1.0 if the
#         user says the game has hard pity.
#
# Rules:
#   - All curves validate their inputs in `__init__` and are immutable.
#   - Provide `to_dict()` / `from_dict()` only if `storage/serializers.py` cannot do it cleanly
#     from public attributes; prefer keeping serialization out of core.
#   - No randomness here.
