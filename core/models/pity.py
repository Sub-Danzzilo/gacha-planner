# FASE 1
# Aturan tarik satu tier: rate dasar, pity, dan guarantee. Ini jantung model probabilitas.
#
# Konvensi (WAJIB ditulis di docstring PityConfig dan dipatuhi semua kode):
#   pity_count = jumlah pull GAGAL berturut-turut sejak hit terakhir.
#   Pull berikutnya adalah pull ke-(pity_count + 1).
#   Hard pity H berarti pull ke-H pasti hit, yaitu saat pity_count == H - 1.
#
# Yang dikerjakan:
# - Dataclass PityConfig (frozen, slots):
#   hard_pity: int | None, soft_pity_start: int | None, soft_pity_step: float.
#   Soft pity: mulai dari pull ke-soft_pity_start, rate naik soft_pity_step (dalam pecahan 0..1) per pull.
#   Validasi: soft_pity_start < hard_pity jika keduanya ada; soft_pity_start tanpa soft_pity_step > 0 tidak valid.
#   Method effective_rate(base_rate: float, pity_count: int) -> float: rate pada pull ke-(pity_count + 1),
#   dipotong maksimal 1.0; hard pity mengembalikan 1.0.
# - Dataclass FeaturedGuarantee (frozen, slots): win_chance: float (misal 0.5 untuk 50/50),
#   guaranteed_after_loss: bool. Artinya: saat hit tier ini, peluang dapat item featured = win_chance;
#   jika kalah dan guaranteed_after_loss, hit berikutnya pasti featured.
# - Dataclass PityState (frozen, slots): pity_count: int = 0, guaranteed_featured: bool = False.
#   Ini kondisi awal user (misal sudah di pull ke-47 dan kalah 50/50 sebelumnya).
# - Dataclass PullRule (frozen, slots): base_rate: float, pity: PityConfig | None,
#   guarantee: FeaturedGuarantee | None. Ini satu-satunya input yang dibutuhkan kalkulator dan simulator.
#   Validasi: 0 < base_rate <= 1.
#
# Jangan: menaruh perhitungan peluang kumulatif di sini. Cuma data dan validasi.
