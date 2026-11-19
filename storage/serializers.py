# Conversion between domain objects and plain JSON-compatible dictionaries. Phase 1.
#
# Class `ProfileSerializer`:
#   - `to_dict(self, profile: GameProfile) -> dict[str, Any]`
#   - `from_dict(self, data: Mapping[str, Any]) -> GameProfile`
#
# Class `GameProfile` (frozen dataclass; keep it in this file or in `core/` if the planner
# needs it, but do not create a second file just for it):
#   - `name: str`
#   - `currencies: tuple[Currency, ...]`
#   - `banners: tuple[Banner, ...]`
#   - `packages: tuple[TopUpPackage, ...]`       phase 2
#   - `exchange_rates: dict[tuple[str, str], Decimal]`   phase 2
#   - `pull_logs: dict[str, PullLog]`            phase 4
#
# Rules:
#   - Every serialized profile carries `"schema_version": int`. Start at 1. Unknown or newer
#     versions raise `StorageError` with a clear message.
#   - `Decimal` values are stored as strings, never floats.
#   - Rate curves are stored as `{"type": "<name>", ...params}`. Dispatch on `type` with an
#     explicit mapping, not `eval`, `pickle` or dynamic imports.
#   - Missing or wrongly typed fields raise `StorageError` naming the field.
#   - Paths to item images are stored relative to the profile file where possible.
#   - Keep serialization logic here so that `core/` stays free of JSON concerns.
