# FASE 1
# Tes untuk core/calculators/simple.py.
# Kasus: p = 0.013 dan confidence 0.9 -> 176 pull; expected ~ 76.9; pulls = 0 -> peluang 0; p = 1 -> 1 pull;
# kurva kumulatif naik monoton; argumen tidak valid (confidence 0 atau 1, pulls negatif) melempar ValueError.
# Pakai pytest.mark.parametrize untuk kasus berderet. Bandingkan float dengan pytest.approx.
