# Items and tiers. Phase 1 (image support in phase 5).
#
# Classes:
#   - `Tier` (frozen dataclass): `name: str`, `rate: float`, `rank: int`
#         `rank` orders tiers by rarity (higher is rarer). `rate` is the base per-pull
#         probability of landing in this tier before pity effects.
#   - `Item` (frozen dataclass): `name: str`, `tier: Tier`, `featured: bool = False`,
#         `image_path: Path | None = None`
#         `image_path` is stored but not read in this module; image loading belongs to the UI.
#   - `ItemNameGenerator`
#         `__init__(self, rng: random.Random)` and `next_name(self) -> str`.
#         Produces placeholder names for users who do not want to type item names. Use two
#         small word lists (adjective + noun) kept as module-level tuples. Names must be unique
#         within one generator instance. Keep the word lists short and neutral.
#
# Validation:
#   - Empty names raise `InvalidBannerError`.
#   - Rates must be within [0, 1].
