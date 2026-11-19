# Featured-item guarantee rule (the "50/50"). Phase 2.
#
# Class `FeaturedGuarantee` (frozen dataclass):
#   - `featured_share: float`
#         probability that a target-tier success is the featured item when no guarantee is
#         active (for example 0.5)
#   - `carries_over: bool = True`
#         if the player loses the 50/50, the next target-tier success is guaranteed featured
#   - `max_consecutive_losses: int | None = None`
#         for games with a different structure, such as a capped number of non-featured
#         results; leave unused unless a banner needs it
#
# Methods:
#   - `next_state(self, was_guaranteed: bool, won_roll: bool) -> bool`
#         returns the guaranteed flag after a target-tier success
#   - `featured_probability(self, guaranteed: bool) -> float`
#
# Validation: `featured_share` must be in (0, 1]. Raise `InvalidRateError` otherwise.
# No randomness in this class; callers roll the dice.
