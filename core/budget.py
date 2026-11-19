# FASE 2
# Proyeksi resource sampai deadline banner, berdasarkan saldo dan pemasukan rutin.
#
# Yang dikerjakan:
# - Enum IncomePeriod: DAILY, WEEKLY, MONTHLY.
# - Dataclass IncomeSource (frozen, slots): name: str, currency_code: str, amount: int,
#   period: IncomePeriod, first_credit: date.
#   Aturan kredit: DAILY tiap hari; WEEKLY tiap 7 hari dari first_credit; MONTHLY di tanggal yang sama tiap
#   bulan dari first_credit (jika bulan lebih pendek, pakai hari terakhir bulan itu).
# - Class BudgetPlanner:
#   * credits_between(source: IncomeSource, today: date, deadline: date) -> int
#       jumlah currency yang masuk pada tanggal di rentang (today, deadline], today tidak dihitung,
#       deadline dihitung. Tulis aturan ini di docstring, dan uji pada batas.
#   * projected_pulls(...): saldo sekarang + pemasukan sampai deadline, dikonversi ke jumlah pull lewat
#       harga per pull banner (konversi antar currency game memakai CurrencyConverter).
#   * required_daily_income(target_pulls: int, ...) -> Decimal: pemasukan per hari yang dibutuhkan untuk
#       mencapai target sebelum deadline. Jika deadline sudah lewat, lempar ValueError.
#
# Jangan: menghitung peluang (itu kalkulator) atau menyentuh file.
