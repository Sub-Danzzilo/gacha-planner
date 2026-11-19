# FASE 1
# Tes untuk core/calculators/pity_dp.py.
# Kasus: tanpa pity sama dengan SimpleCalculator; hard pity membuat cdf = 1.0 tepat di pull ke-H;
# off-by-one pada batas soft pity dan hard pity (uji pull ke-H - 1, H, H + 1); guarantee 50/50 menaikkan
# expected pull ke kisaran yang bisa dihitung tangan untuk kasus sederhana; PityState awal menggeser kurva.
# Jelaskan di komentar tes cara angka harapan dihitung tangan, supaya tes bisa diverifikasi manusia.
