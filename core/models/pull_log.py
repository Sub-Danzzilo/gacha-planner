# FASE 4
# Riwayat pull milik user, dipakai untuk mengestimasi rate yang tidak diumumkan game.
#
# Yang dikerjakan:
# - Dataclass PullRecord (frozen, slots): banner_name: str, tier_name: str, item_name: str | None,
#   pulled_at: datetime, was_featured: bool | None.
# - Class PullLog: kumpulan PullRecord. Method add(record), total() -> int,
#   hits(tier_name: str) -> int, for_banner(banner_name: str) -> PullLog.
#   Tidak boleh memutasi record yang sudah masuk.
#
# Jangan: menghitung estimasi rate di sini (itu core/estimator.py).
