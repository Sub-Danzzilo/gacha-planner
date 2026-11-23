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

Phases 1-5 are implemented. `pytest`, `mypy .`, `ruff check .` and `ruff format --check .` pass.

Implemented:

- `core/models/`: `Currency`/`CurrencyKind`/`Money`, `Item`, `PityConfig`/`FeaturedGuarantee`/`PityState`/`PullRule`, `RateTier`/`Banner`, `TopUpPackage`, `GameProfile`, `PullRecord`/`PullLog`
- `core/calculators/`: the `PullCalculator` contract, `SimpleCalculator` (closed form), `PityCalculator` (forward DP over `(pity, guaranteed)`), `MultiTargetEstimator` (simulation plus a Wilson interval)
- `core/`: `GachaSimulator`, `RateEstimator`, `BudgetPlanner`, `TopUpOptimizer`, `ManualRateProvider`/`CurrencyConverter`, `RandomNameGenerator`, domain errors
- `services/planner_service.py`: the single entry point from the UI into the domain
- `storage/`: JSON profile serializer and an atomic profile repository
- `ui/`: Tkinter app shell, text parsing, background worker, theme and chart helpers, four views
- `tests/`: unit tests for `core/`, `storage/` and `services/`

Not implemented yet; do not describe these as existing features:

- pull-log persistence and a pull-log screen (`core/models/pull_log.py` and `core/estimator.py` exist, but `GameProfile` has no field for logs)
- a Monte Carlo panel in the UI (`ui/tasks.py` and `build_histogram_figure` exist, but no view uses them)
- item images in the banner form (`ui/widgets/item_card.py` exists but is not wired)

## Language

Everything in this repository is English: UI labels, dialog text, messages, identifiers, comments, docstrings, test names and test data. Do not add Indonesian text anywhere.

Numbers use English formatting everywhere: `.` for decimals and `,` for thousands, for example `16,000.50`. Input parsing rules live only in `ui/parsing.py`.

## Tech stack

- Python 3.11+
- Standard library for everything in `core/` and `storage/`
- Tkinter / ttk for the UI
- matplotlib for charts, Pillow for item images
- pytest for tests, mypy for static typing, ruff for linting and formatting

Runtime dependencies are declared in `requirements.txt`; matplotlib and Pillow are also optional extras (`[charts]`, `[images]`) and part of `[dev]`. Do not add a dependency without a clear reason; say why instead of adding it silently.

## Architecture and layering

```text
core/      Pure domain logic. Stdlib only. No I/O, no Tkinter, no JSON.
services/  Orchestration for the UI. Imports core. Never imported by core.
storage/   Persistence. Imports core. Never imported by core.
ui/        Tkinter. Imports core, services and storage. Never imported by them.
tests/     Mirrors core/, storage/ and services/. UI is not unit tested.
```

Rules:

1. `core/` must not import from `storage/`, `services/` or `ui/`. Check the import list of each file when in doubt.
2. `services/` may import `core/` only. The UI never computes probabilities or currency math itself.
3. Views in `ui/views/` contain no business logic. They collect text, convert it with `ui/parsing.py`, call a service or an `App` callback, and render plain data. There are no presenter classes: `ui/parsing.py` is the only place that turns user text into typed values.
4. Long computations must not run on the Tkinter main thread. Use `BackgroundTask` from `ui/tasks.py`; the module is currently unused because no screen runs a long task yet.
5. No global mutable state and no singletons. Dependencies are passed in through constructors.
6. Randomness inside `core/` is always injected as a `random.Random` instance so results are reproducible in tests. The UI may create its own instance for cosmetic purposes (random item names).
7. Exceptions: `ValueError` (or a subclass such as `InputError`, `CurrencyMismatchError`) for invalid arguments or data, raised from validation in dataclasses and calculators; `core/errors.py` for cross-module domain failures (`MissingExchangeRateError`, `StorageError`). Never raise bare `Exception`.
8. `Money` accepts `Decimal` only (`int` and `float` raise `TypeError`). Ordering comparisons between different currencies raise `CurrencyMismatchError`; equality stays structural.

## Domain vocabulary

Use the names the code uses:

- **Pull**: one attempt on a banner.
- **Banner**: a pool of items with tiers, each tier carrying a `PullRule`, plus a pull cost and an optional deadline.
- **RateTier**: one rarity class on a banner (for example "5-star").
- **PullRule**: base rate plus optional `PityConfig` and `FeaturedGuarantee`. `PullRule.effective_rate(pity_count)` is the chance for a single pull.
- **Pity counter**: consecutive failed pulls since the last hit, so the next pull is pull number `pity_count + 1`. Hard pity `H` is certain on pull `H`; soft pity raises the rate by `soft_pity_step` starting at pull `soft_pity_start`.
- **PityState**: the player's starting `pity_count` and `guaranteed_featured`.
- **FeaturedGuarantee** (the 50/50): `win_chance` for the featured item and `guaranteed_after_loss`.
- **Target**: the item (or set of items and copies) the player wants.
- **Currency**: game currency (diamonds, tickets, coins) or real currency with an ISO-like code.
- **Top-up package**: a purchasable bundle of game currency priced in real money, with optional regular and first-purchase bonuses.
- **Calculator**: `SimpleCalculator` for a flat rate, `PityCalculator` for pity and guarantee, `MultiTargetEstimator` for several targets.

## Numeric conventions

- Money and currency amounts: `decimal.Decimal`. Never `float`, never `int`.
- Probabilities: `float` in `[0.0, 1.0]`, validated at construction.
- User-facing percentages are converted at the UI boundary; `core/` only sees probabilities.
- Pull counts are `int`.

## Coding conventions

- Full type hints on every function, method and attribute. The project must pass `mypy --strict`.
- Prefer `@dataclass(frozen=True, slots=True)` for value objects. Use plain classes for objects with behavior and state.
- Use `Protocol` or `abc.ABC` only where there is more than one implementation or a documented extension point (`PullCalculator`, `ExchangeRateProvider`).
- Public classes and functions get a short docstring only if the name and signature do not already explain them.
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
- invent features beyond what the request and this file describe
- mix languages: user-facing text and code text are English only

If a request is ambiguous, pick the simplest reasonable reading and mention the choice in your final message.

## Phases

Phase 1, MVP: single target, flat rate or pity curve, currency, price per pull, success probability.

- `core/errors.py`, `core/models/` (currency, item, pity, banner), `core/calculators/` (`base`, `simple`, `pity_dp`), `core/simulator.py`
- `storage/serializers.py`, `storage/profile_repository.py`
- `ui/app.py`, `ui/parsing.py`, `ui/views/banner_view.py`, `ui/views/currency_view.py`, `ui/views/result_view.py`
- `main.py`, tests for all of the above

Phase 2, planner: 50/50 guarantee, starting pity, real-money currencies, manual exchange rates, top-up packages, income and deadline planning.

- `core/exchange.py`, `core/topup_optimizer.py`, `core/budget.py`, `core/naming.py`, `core/models/profile.py`, `core/models/topup.py`
- `services/planner_service.py`, `ui/views/budget_view.py`

Phase 3, insight: charts, multiple copies, multiple targets.

- `core/calculators/multi_target.py`, `ui/charts.py`

Phase 4, data: pull log and rate estimation for games that hide their rates.

- `core/models/pull_log.py`, `core/estimator.py`
- Persistence and a screen are not built yet; if you add them, follow the storage and layering rules.

Phase 5, polish: item images, optional animation, dark mode.

- `ui/widgets/item_card.py`, `ui/theme.py`, chart palettes from `ui/theme.py`

A phase is done when its code is implemented, typed, tested and the quality commands below pass.

## Commands

```bash
pip install -e ".[dev]"
pytest
mypy .
ruff check .
ruff format --check .
python main.py
```

Run `pytest`, `mypy .`, `ruff check .` and `ruff format --check .` before reporting a task as finished. Report the actual result, including failures.

## Testing

- Every `core/` module with behavior has a matching `tests/test_<module>.py`. Pure data and exception modules are covered through their users (`core/calculators/base.py` through its subclasses, `core/errors.py` through exchange and storage).
- Test behavior, not implementation details.
- Use small hand-computable cases (for example rate 0.5 over 2 pulls gives 0.75) in addition to larger ones.
- The simulator and the calculator must agree. A test compares the simulated distribution against the exact one with a fixed seed and a stated tolerance.
- Tests must not touch the real `data/` directory. Use `tmp_path`.
- Tests are English like the rest of the code, including test data strings.

## Git and commit messages

The user commits; the agent does not. Unless the user asks for it, never run `git add`,
`git commit` or `git push`. Every change you make is reported to the user with a commit message
they can paste, together with the files that message covers.

A commit message:

- is English, imperative, one line, at most 72 characters, in the `type: subject` form the history
  uses (`feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `build:`, `chore:`)
- says why the change was made, not only what moved
- is split by concern only when the working tree really holds unrelated changes; one message for
  the whole tree is the default

Keep the message alone inside a fenced `text` block, because the user copies it straight into
`git commit -m`. List the target files below the block as plain text, never inside it: specific
paths, a pattern such as `core/**`, or `all files`. Report it in this shape:

```text
refactor(core): split the domain into models and calculators
```

Files: `core/models/` (all), `core/calculators/` (all), `tests/test_pity.py`.

## Markdown files

Every Markdown file you create or edit must pass markdownlint before you report the task as
finished:

```bash
npx markdownlint-cli2 AGENTS.md path/to/other.md
```

Fix what it reports. Only when a warning cannot be fixed without rewriting unrelated content may
you disable that single rule in `.markdownlint.jsonc`, with a comment that says why. Never delete
the config, and never disable a rule you did not actually hit.

## Things not to do

- Do not call any network service. Exchange rates are manual in this project. The provider interface exists so an API provider can be added later, but do not write one.
- Do not store anything in `data/profiles/` from code in tests or examples.
- Do not reformat or rewrite files unrelated to the current task.
- Do not change the layering rules or conventions in this file. If you believe they should change, say so in your final message.

## Final message format

When you finish a task, reply with: what you implemented, which files changed, which commands you ran and their results, and any decisions you made where instructions were ambiguous. Keep it short and factual.
