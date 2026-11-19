# FASE 1
# Kontrak semua kalkulator peluang.
#
# Yang dikerjakan:
# - ABC PullCalculator dengan method abstrak:
#   * success_probability(pulls: int, state: PityState) -> float
#       peluang dapat target minimal sekali dalam `pulls` pull dari kondisi awal `state`.
#   * pulls_for_confidence(confidence: float, state: PityState, max_pulls: int = 2000) -> int | None
#       pull paling sedikit agar peluang >= confidence; None jika tidak tercapai dalam max_pulls.
#   * expected_pulls(state: PityState) -> float
#       rata-rata pull sampai dapat target pertama.
#   * cumulative_curve(max_pulls: int, state: PityState) -> list[float]
#       indeks i = peluang sukses dalam i + 1 pull. Dipakai grafik di fase 3.
# - Validasi argumen umum (confidence di (0, 1), pulls >= 0) boleh ditaruh sebagai method non-abstrak
#   di base class supaya tidak diulang di tiap turunan.
#
# Jangan: menerima Money atau Currency. Kalkulator hanya mengenal jumlah pull.
