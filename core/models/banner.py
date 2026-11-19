# FASE 1
# Banner gacha: tier rate, item, dan biaya tarik.
#
# Yang dikerjakan:
# - Dataclass RateTier (frozen, slots): name: str (misal "Bintang 5"), rule: PullRule.
# - Dataclass Banner (frozen, slots):
#   name: str, tiers: tuple[RateTier, ...], items: tuple[Item, ...],
#   cost_per_pull: Money (dalam currency game), ends_on: date | None = None.
#   Method tier(name: str) -> RateTier: cari tier, lempar KeyError dengan pesan jelas jika tidak ada.
#   Validasi: nama tier unik, setiap Item.tier_name ada di tiers, cost_per_pull.currency.kind == GAME.
#
# Aturan khusus:
# - Fase 1 cukup mendukung satu tier yang dihitung. Struktur tuple dipertahankan supaya multi-tier
#   di fase 3 tidak mengubah model.
# - Banner tidak menghitung apa pun. Ia hanya wadah data.
