# FASE 1
# Kalkulator tanpa pity, rumus tertutup.
#
# Yang dikerjakan:
# - Class SimpleCalculator(PullCalculator), menerima rate: float.
#   success_probability: 1 - (1 - p) ** n
#   pulls_for_confidence: ceil(log(1 - c) / log(1 - p))
#   expected_pulls: 1 / p
# - Tangani kasus tepi secara eksplisit: p == 1 (selalu 1 pull), confidence mendekati 1,
#   pulls == 0 (peluang 0).
# - Abaikan PityState: kalau state.pity_count != 0 tidak mengubah hasil karena tidak ada pity.
#
# Tes wajib (tests/test_simple_calculator.py): p = 0.013, confidence 0.9 -> 176 pull; expected ~ 76.9.
# Untuk presisi numerik pada p kecil, pertimbangkan math.log1p dan math.expm1.
