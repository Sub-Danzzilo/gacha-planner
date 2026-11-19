# FASE 1
# Model currency dan nilai uang. Dipakai oleh hampir semua modul lain, jadi harus kecil dan ketat.
#
# Yang dikerjakan:
# - Enum CurrencyKind: GAME, REAL.
# - Dataclass Currency (frozen, slots): code: str (unik, huruf besar, contoh "IDR", "USD", "DIAMOND"),
#   name: str, kind: CurrencyKind, decimals: int (IDR 0, USD 2, currency game 0).
#   Validasi: code tidak kosong dan huruf besar, decimals >= 0.
# - Dataclass Money (frozen, slots): amount: Decimal, currency: Currency.
#   * Tolak float di __post_init__ (lempar TypeError). Uang hanya boleh Decimal.
#   * Operasi: penjumlahan, pengurangan, perkalian dengan int/Decimal, perbandingan.
#     Operasi antar Money hanya boleh jika currency sama; jika beda lempar CurrencyMismatchError.
# - Class CurrencyMismatchError(ValueError).
#
# Aturan khusus:
# - Jangan membulatkan di sini. Pembulatan ke desimal currency dilakukan di core/exchange.py.
# - Jangan menaruh logika kurs atau konversi di file ini.
