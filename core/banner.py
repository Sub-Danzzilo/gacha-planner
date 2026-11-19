# Banner definition. Phase 1 (guarantee support added in phase 2).
#
# Class `Banner` (frozen dataclass or a plain class with read-only properties):
#   - `name: str`
#   - `tiers: tuple[Tier, ...]`
#   - `items: tuple[Item, ...]`
#   - `rate_curve: RateCurve`        curve applied to the tier the user targets
#   - `target_tier: Tier`            tier the player is pulling for
#   - `pull_cost: Decimal`           price of one pull
#   - `cost_currency: Currency`      currency the pull cost is expressed in
#   - `guarantee: FeaturedGuarantee | None = None`    phase 2; leave the field out until then
#
# Methods:
#   - `validate(self) -> None`        called from `__init__`; raises `InvalidBannerError` when
#                                      tier rates sum above 1.0, the target tier is not in
#                                      `tiers`, or no item belongs to the target tier
#   - `featured_items(self) -> tuple[Item, ...]`
#   - `pulls_affordable(self, balance: Decimal) -> int`
#         `floor(balance / pull_cost)`; raise `InvalidCurrencyError` if the balance currency
#         differs from `cost_currency` (the caller converts first)
#
# Design note: only the target tier gets a pity curve in the MVP. Do not generalize to
# per-tier curves until a real requirement appears.
