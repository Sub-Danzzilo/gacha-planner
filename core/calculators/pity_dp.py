# FASE 1
# Kalkulator dengan hard/soft pity dan guarantee featured, memakai dynamic programming.
#
# Konsep:
# - State per pull: (pity_count, guaranteed_featured). Simpan distribusi peluang di tiap state.
# - Dari tiap state, hitung rate efektif lewat PityConfig.effective_rate. Dua cabang:
#     tidak hit -> pity_count + 1, flag tetap;
#     hit       -> dapat featured dengan peluang win_chance (atau 1.0 jika guaranteed_featured):
#                    featured: selesai (massa peluang masuk "sukses di pull ke-k"),
#                    kalah:    pity_count reset 0, guaranteed_featured = guaranteed_after_loss.
#   Tanpa FeaturedGuarantee, setiap hit dianggap target.
# - Hasilnya pmf: peluang target pertama didapat tepat di pull ke-k. cdf = jumlah kumulatif pmf.
#
# Yang dikerjakan:
# - Class PityCalculator(PullCalculator), menerima rule: PullRule.
# - Hitung pmf/cdf sekali per (state, max_pulls) lalu cache di instance. Semua method base class
#   dijawab dari cdf tersebut.
# - Kompleksitas O(max_pulls * jumlah_state). Jumlah state kecil (hard pity * 2), jadi aman.
# - Tanpa hard pity, distribusi dipotong di max_pulls; sisa peluang di ekor tidak dihitung. Dokumentasikan
#   di docstring supaya pemanggil tahu cdf bisa sedikit di bawah nilai sebenarnya.
# - expected_pulls: jumlahkan k * pmf[k], tambah koreksi ekor jika tanpa hard pity.
#
# Tes wajib (tests/test_pity_calculator.py):
# - Tanpa pity dan guarantee: hasil sama dengan SimpleCalculator (toleransi float).
# - Dengan hard pity: cdf mencapai 1.0 pada pull ke-H dari state awal 0, tidak pernah menurun.
# - PityState awal (misal pity_count = 60) menggeser kurva ke kiri dibanding state 0.
# - Cocok dengan GachaSimulator pada seed tetap dalam toleransi statistik.
