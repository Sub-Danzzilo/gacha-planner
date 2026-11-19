# FASE 3
# Peluang mendapatkan beberapa item target sekaligus, dan duplikat item yang sama.
#
# Alasan pakai simulasi: target-target berbagi pool dan pity, jadi peluangnya tidak bisa dikali begitu saja.
#
# Yang dikerjakan:
# - Dataclass MultiTargetSpec (frozen, slots): daftar target (nama item, jumlah salinan yang dibutuhkan).
# - Class MultiTargetEstimator: menerima GachaSimulator dan MultiTargetSpec; method
#   success_probability(pulls: int, trials: int) -> tuple[float, float, float] berisi
#   (estimasi, batas bawah, batas atas) dengan interval kepercayaan 95%.
# - Pakai interval Wilson (fungsi dipakai bersama core/estimator.py; letakkan di satu tempat saja,
#   jangan disalin).
#
# Jangan: mengklaim hasil eksak. Selalu kembalikan rentang.
