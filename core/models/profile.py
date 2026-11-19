# FASE 2
# Satu profil = satu game milik user. Unit yang disimpan dan dimuat dari JSON.
#
# Yang dikerjakan:
# - Dataclass GameProfile: name: str, currencies: tuple[Currency, ...], balances: dict[str, Money]
#   (kunci = currency code), banners: tuple[Banner, ...], topup_packages: tuple[TopUpPackage, ...],
#   exchange_rates: tuple[ExchangeRate, ...], incomes: tuple[IncomeSource, ...],
#   display_currency_code: str (mata uang untuk menampilkan biaya uang asli).
#   Tidak perlu frozen karena user mengedit profil; kalau mutable, jangan beri default list/dict yang dibagi
#   (pakai field(default_factory=...)).
# - Validasi konsistensi: semua code yang dirujuk (balance, paket, kurs, income, display) ada di currencies.
#
# Jangan: membaca/menulis file di sini. Itu storage/.
