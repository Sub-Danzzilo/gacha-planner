# FASE 1 (biaya uang asli: FASE 2)
# Satu-satunya pintu masuk UI ke logika core. Merangkai model, kalkulator, kurs, dan budget.
#
# Yang dikerjakan:
# - Dataclass PlanReport (frozen, slots): total_pulls: int, success_probability: float,
#   pulls_for_50: int | None, pulls_for_90: int | None, pulls_for_99: int | None, expected_pulls: float.
#   Fase 2 menambah: real_money_cost: Money | None (dalam display currency profil).
# - Class PlannerService: menerima CurrencyConverter (dan di fase 2, TopUpOptimizer/BudgetPlanner).
#   Method plan(profile: GameProfile, banner_name: str, tier_name: str, state: PityState) -> PlanReport.
#   Langkah: saldo user -> dikonversi ke currency tarik banner -> jumlah pull (pembagian bulat ke bawah)
#   -> pilih kalkulator -> isi PlanReport.
# - Pemilihan kalkulator: SimpleCalculator jika rule tidak punya pity dan guarantee; selain itu PityCalculator.
#   Logika pemilihan ini hanya ada di sini, jangan ada di UI.
# - Fase 2: untuk pulls_for_90 (dan persentil lain), hitung kekurangan currency game dibanding saldo, minta
#   TopUpOptimizer rencana termurah, konversi harga ke display currency.
#
# Aturan khusus:
# - Method di sini hanya menerima dan mengembalikan tipe domain, bukan string dari form.
# - Error domain (kurs hilang, banner tidak ada) dilempar apa adanya; UI yang menerjemahkan ke pesan.
