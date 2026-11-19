# FASE 1
# Menampilkan PlanReport.
#
# Yang dikerjakan:
# - Class ResultView(ttk.Frame) dengan method show(report: PlanReport) -> None dan clear() -> None.
# - Tampilkan: total pull yang mampu dibeli, peluang sukses, pull untuk 50/90/99% yakin, expected pull.
#   Nilai None (tidak tercapai dalam batas) tampil sebagai teks jelas, misal "lebih dari 2000 pull".
# - Fase 2: biaya uang asli dalam display currency.
# - Format angka lewat ui/parsing.py (format_percent, format_money).
#
# Jangan: memanggil service atau melakukan hitungan.
