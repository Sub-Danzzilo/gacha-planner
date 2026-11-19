# Monte Carlo simulation. Phase 1.
#
# Class `GachaSimulator`:
#   - `__init__(self, banner: Banner, rng: random.Random)`
#
#   - `simulate_once(self, starting_pity: int = 0) -> int`
#         Pull until the target is obtained and return the number of pulls used. Use
#         `banner.rate_curve.rate_at(pity)` per pull and `rng.random()` for the roll. Add a
#         safety cap (default 100_000 pulls) that raises `InvalidBannerError` so a broken curve
#         cannot loop forever.
#
#   - `run(self, trials: int, max_pulls: int = 2000, starting_pity: int = 0) -> PullDistribution`
#         Run `trials` independent simulations and return `PullDistribution.from_samples(...)`.
#         `trials` must be positive. Samples above `max_pulls` count toward `tail_mass`.
#
#   - `simulate_budget(self, pulls: int, trials: int, starting_pity: int = 0) -> float`
#         Fraction of trials that obtain the target within `pulls` pulls.
#
# Phase 2: honor `Banner.guarantee` with the same state model the calculator uses.
#
# Rules:
#   - Accept an optional `progress_callback: Callable[[int, int], None] | None` in `run` so the
#     UI worker can report progress. Call it at most about 100 times per run.
#   - The simulator must not import Tkinter or touch threads. Threading is handled in
#     `ui/workers.py`.
#   - A test must show the simulated distribution matches `ProbabilityCalculator` within a
#     stated tolerance for a fixed seed and a large trial count.
