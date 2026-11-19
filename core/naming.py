# FASE 2
# Pembuat nama item acak, untuk user yang tidak mau memikirkan nama.
#
# Yang dikerjakan:
# - Class RandomNameGenerator: menerima rng: random.Random (di-inject). Method generate(taken: set[str]) -> str
#   merangkai dua bagian dari tuple konstanta modul (misal kata sifat + benda) dan menjamin hasil tidak ada
#   di `taken`. Jika kombinasi habis, lempar error jelas, jangan loop selamanya.
# - Daftar kata cukup puluhan entri, tertulis langsung di file ini sebagai tuple[str, ...].
#
# Jangan: membaca file eksternal atau memakai library generator nama.
