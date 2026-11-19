# FASE 3
# Grafik peluang. Memakai matplotlib yang ditanam di Tkinter.
#
# Yang dikerjakan:
# - Fungsi build_cumulative_figure(curve: list[float], markers: dict[str, int | None]) -> Figure.
#   Sumbu x = jumlah pull, sumbu y = peluang sukses kumulatif. Garis horizontal di 50%, 90%, 99% dan
#   penanda pull-nya.
# - Fungsi build_histogram_figure(result: SimulationResult) -> Figure untuk distribusi hasil simulasi.
# - Class FigureFrame(ttk.Frame): membungkus FigureCanvasTkAgg; method set_figure(figure: Figure) -> None.
#
# Aturan khusus:
# - Buat Figure langsung (matplotlib.figure.Figure). Dilarang memakai pyplot dan plt.show(); pyplot menyimpan
#   state global dan bentrok dengan event loop Tkinter.
# - Label sumbu dan judul dalam bahasa Indonesia. Warna harus tetap terbaca di tema gelap (fase 5).
