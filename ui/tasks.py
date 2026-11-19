# FASE 3
# Menjalankan pekerjaan berat (simulasi Monte Carlo) tanpa membekukan jendela.
#
# Yang dikerjakan:
# - Class BackgroundTask: jalankan sebuah callable di threading.Thread, kirim progress dan hasil lewat
#   queue.Queue, dan baca queue itu dari event loop dengan widget.after(...).
# - API: start(work: Callable[[Callable[[int, int], None]], T], on_progress: Callable[[int, int], None],
#   on_done: Callable[[T], None], on_error: Callable[[Exception], None]) -> None, dan cancel() -> None.
# - Hanya satu task aktif per instance; start saat masih jalan harus ditolak atau membatalkan yang lama
#   (pilih satu, tuliskan di docstring).
#
# Aturan khusus:
# - Tkinter tidak thread-safe. Thread latar DILARANG menyentuh widget secara langsung; semua lewat queue.
