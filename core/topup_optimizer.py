# FASE 2
# Cari kombinasi paket top-up termurah untuk memenuhi kebutuhan currency game.
#
# Masalah: unbounded knapsack (coin change) dengan minimisasi biaya, kebutuhan boleh terlampaui
# (membeli paket lebih besar yang masih lebih murah itu sah).
#
# Yang dikerjakan:
# - Dataclass TopUpPlan (frozen, slots): purchases: tuple[tuple[TopUpPackage, int], ...] (paket, jumlah beli),
#   total_price: Money, total_received: int, surplus: int.
# - Class TopUpOptimizer: menerima daftar TopUpPackage (semua harga harus dalam currency yang sama dan
#   semua memberi currency game yang sama; kalau tidak, lempar ValueError di konstruktor).
#   Method cheapest_plan(required_amount: int, first_purchase_available: bool = True) -> TopUpPlan.
# - Modelkan bonus pembelian pertama dengan memecah tiap paket jadi dua item: "salinan pertama" (hanya boleh 1x,
#   memberi first_purchase_total) dan "salinan berikutnya" (tak terbatas, memberi total_amount).
# - DP di atas jumlah currency game dari 0 sampai required_amount + jumlah terbesar satu paket.
#   Ambil biaya minimum untuk jumlah >= required_amount; tie-break pilih surplus terkecil.
# - required_amount <= 0 mengembalikan plan kosong.
#
# Tes wajib (tests/test_topup_optimizer.py): satu paket; dua paket di mana paket besar lebih murah per unit;
# kasus paket besar lebih murah walau melebihi kebutuhan; efek bonus pembelian pertama.
