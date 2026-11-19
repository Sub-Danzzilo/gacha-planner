# FASE 1
# Mengubah teks dari kolom isian menjadi nilai bertipe. Satu-satunya tempat konversi persen <-> pecahan.
#
# Yang dikerjakan:
# - parse_percent(text: str) -> float: "1.3" atau "1,3" (koma desimal ala Indonesia) -> 0.013.
#   Tolak nilai di luar 0..100 dan teks kosong.
# - parse_decimal(text: str) -> Decimal: terima "16000", "16.000,50"? Putuskan satu aturan sederhana
#   (misal: koma = desimal, titik = pemisah ribuan) dan tuliskan di docstring. Tolak teks ambigu.
# - parse_positive_int(text: str) -> int.
# - format_percent(value: float) -> str dan format_money(money: Money) -> str untuk tampilan balik
#   (pemisah ribuan dan desimal sesuai aturan yang sama).
# - Kesalahan input dilempar sebagai InputError(ValueError) dengan pesan Indonesia yang bisa langsung
#   ditampilkan ke user (menyebut kolom apa yang salah akan diurus pemanggil).
#
# Tes wajib (tests/test_parsing.py): "1,3", "1.3", spasi di tepi, nilai negatif, huruf, kosong.
