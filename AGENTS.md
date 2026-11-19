# AGENTS.md

Instructions for AI coding agents working on this repository. Read this file fully before touching any code.

## Project summary

Gacha Planner is a desktop tool (Python + Tkinter) that helps players of gacha games decide how many resources to prepare before pulling.

Players usually know a headline rate ("1.3% for the featured item") but not what it means in practice. This tool answers questions such as:

- How many pulls do I need to be 90% sure of getting the item?
- I can afford 80 pulls. What is my chance of success?
- What is the expected number of pulls, and how bad is a really unlucky run?
- How much real money does that correspond to?
- If the game does not publish its rate, what does my pull history suggest?

Everything is user-defined (items, rates, pity, currencies, prices). There are no per-game presets in the core.

## Current state

Every Python file in this repository currently contains only comment instructions describing what the file must contain. Your job is to replace those comments with a real implementation. Work in the phase order below. Do not implement a later phase's files while an earlier phase is incomplete.

When a file is implemented, delete the instruction comments that are now redundant. Keep only comments that explain why something is done, not what it does.

## Tech stack

- Python 3.11+
- Standard library for everything in `core/` and `storage/`
- Tkinter / ttk for the UI
- Pillow for item images (phase 5)
- matplotlib for charts (phase 3)
- pytest for tests, mypy for static typing, ruff for linting and formatting

Do not add a dependency without a clear reason. If you think one is needed, stop and say why in your final message instead of adding it silently.

## Architecture and layering

```
core/      Pure domain logic. Stdlib only. No I/O, no Tkinter, no JSON.
storage/   Persistence. Imports core. Never imported by core.
ui/        Tkinter. Imports core and storage. Never imported by them.
tests/     Mirrors core/ and storage/. UI is not unit tested.
```

Rules:

1. `core/` must not import from `storage/` or `ui/`. Enforce this by review; if you are unsure, check the import list of each file.
2. Views in `ui/views/` contain no business logic. They render state and forward user events to a presenter. Presenters in `ui/presenters.py` call `core/` and return plain data for the view.
3. Long computations (Monte Carlo, large DP) must not run on the Tkinter main thread. Use the worker helper in `ui/workers.py`.
4. No global mutable state and no singletons. Dependencies are passed in through constructors.
5. Randomness is always injected as a `random.Random` instance so results are reproducible in tests.

## Domain vocabulary

- **Pull**: one attempt on a banner.
- **Banner**: a pool of items with tier rates, a rate curve, a pity rule and an optional guarantee rule.
- **Tier**: a rarity class (for example 5-star, 4-star, common). Each tier has a rate.
- **Pity counter**: number of consecutive pulls since the last success for a tier.
- **Hard pity**: the pull number at which success is guaranteed (probability 1).
- **Soft pity**: the pull number from which the per-pull rate starts rising.
- **Rate curve**: function from pity counter to per-pull success probability.
- **Guarantee (50/50)**: when a top-tier success may be a non-featured item, and a loss may guarantee the featured item next time.
- **Target**: the item (or set of items and copies) the player wants.
- **Currency**: either a game currency (diamonds, tickets, coins) or a real currency (USD, IDR). Real currency has an ISO-like code.
- **Top-up package**: a purchasable bundle of game currency priced in real money, possibly with bonus and first-time-only flags.

## Numeric conventions

- Money and currency amounts: `decimal.Decimal`. Never `float`.
- Probabilities: `float` in `[0.0, 1.0]`, validated at construction.
- User-facing percentages are converted at the UI boundary; `core/` only sees probabilities.
- Pull counts are `int`.

## Coding conventions

- Full type hints on every function, method and attribute. The project must pass `mypy --strict`.
- Prefer `@dataclass(frozen=True, slots=True)` for value objects. Use plain classes for objects with behavior and state.
- Use `Protocol` or `abc.ABC` only where there is more than one implementation or a documented extension point (rate curves, exchange rate providers).
- Public classes and functions get a short docstring only if the name and signature do not already explain them.
- Raise specific exceptions from `core/errors.py`. Do not raise bare `Exception` or `ValueError` for domain failures.
- Keep functions short and single-purpose. Keep files focused on one concept.
- Names must be descriptive and domain-based. No `utils.py`, `helpers.py`, `manager.py` or `data` as a name.

## Style rules (read this twice)

The code should look like a careful human wrote it. Specifically, do not:

- add a comment above a line that restates the line
- add docstrings that repeat the function name
- write emoji in code, comments or messages
- create wrapper classes or abstract layers with a single trivial use
- add "just in case" parameters, flags or config options nobody asked for
- catch broad exceptions and swallow them
- leave `TODO` placeholders, `pass` bodies or `NotImplementedError` in finished code
- invent features beyond what the instruction comments and this file describe

If an instruction is ambiguous, pick the simplest reasonable reading and mention the choice in your final message.

## Phases

Phase 1, MVP: single target, flat rate or pity curve, currency, price per pull, success probability.

- `core/errors.py`, `core/distribution.py`, `core/rate_curve.py`, `core/items.py`, `core/banner.py`, `core/currency.py`, `core/calculator.py`, `core/simulator.py`
- `storage/serializers.py`, `storage/profile_repository.py`
- `ui/app.py`, `ui/presenters.py`, `ui/workers.py`, `ui/views/banner_view.py`, `ui/views/currency_view.py`, `ui/views/results_view.py`
- tests for all of the above

Phase 2, planner: 50/50 guarantee, starting pity, real-money currencies, manual exchange rates, top-up packages, income and deadline planning.

- `core/guarantee.py`, `core/exchange.py`, `core/topup.py`, `core/planner.py`, `ui/views/planner_view.py`

Phase 3, insight: charts, percentiles, multiple copies, multiple targets.

- `ui/widgets/curve_chart.py`, extensions to `core/calculator.py` and `core/distribution.py`

Phase 4, data: pull log and rate estimation for games that hide their rates.

- `core/pull_log.py`, `core/estimator.py`, `ui/views/pull_log_view.py`

Phase 5, polish: item images, optional animation, dark mode.

- `ui/widgets/item_card.py`

A phase is done when its code is implemented, typed, tested and the quality commands below pass.

## Commands

```
pip install -e ".[dev]"
pytest
mypy .
ruff check .
ruff format .
python main.py
```

Run `pytest`, `mypy .` and `ruff check .` before reporting a task as finished. Report the actual result, including failures.

## Testing

- Every `core/` module has a matching `tests/test_<module>.py`.
- Test behavior, not implementation details.
- Use small hand-computable cases (for example rate 0.5 over 2 pulls gives 0.75) in addition to larger ones.
- The simulator and the calculator must agree. A test compares the simulated distribution against the exact one with a fixed seed and a stated tolerance.
- Tests must not touch the real `data/` directory. Use `tmp_path`.

## Things not to do

- Do not call any network service. Exchange rates are manual in this project. The provider interface exists so an API provider can be added later, but do not write one.
- Do not store anything in `data/profiles/` from code in tests or examples.
- Do not reformat or rewrite files unrelated to the current task.
- Do not change the layering rules or conventions in this file. If you believe they should change, say so in your final message.

## Final message format

When you finish a task, reply with: what you implemented, which files changed, which commands you ran and their results, and any decisions you made where instructions were ambiguous. Keep it short and factual.
