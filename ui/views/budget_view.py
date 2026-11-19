# FASE 2
# Form pemasukan rutin dan deadline banner.
#
# Yang dikerjakan:
# - Class BudgetView(ttk.Frame): daftar IncomeSource (nama, currency, jumlah, periode, tanggal kredit pertama),
#   pemilih tanggal deadline banner (Entry bertanggal berformat YYYY-MM-DD dengan validasi; jangan tambah
#   dependency kalender).
# - Method get_incomes() -> list[IncomeSource] dan get_deadline() -> date | None.
# - Tampilkan hasil proyeksi (jumlah pull saat deadline, kebutuhan pemasukan harian) lewat method show(...).
#
# Jangan: menghitung proyeksi di sini. Panggil lewat App -> PlannerService.
