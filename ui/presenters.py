# Presenters: the glue between views and the domain. Phase 1 (more in later phases).
#
# Presenters hold UI state and call `core/` and `storage/`. Views never import `core/`
# calculation classes; they only receive the plain data presenters give them.
#
# Classes:
#   - `BannerPresenter`
#         Receives raw form input (strings) from `BannerView`, validates and converts it
#         (percentages to probabilities, strings to Decimal), builds a `Banner`, and reports
#         validation problems as a list of field-level messages for the view to display.
#   - `CurrencyPresenter`
#         Manages the list of currencies and balances entered by the user.
#   - `ResultsPresenter`
#         Runs the calculator for the current banner and budget and produces a `ResultsViewModel`
#         (frozen dataclass): chance with the current budget, pulls for 50%, 90% and 99%,
#         expected pulls, and a note when the distribution was truncated. Starts a Monte Carlo
#         run through `BackgroundTask` when the user asks for simulation, and exposes progress.
#   - `ProfilePresenter`
#         Wraps `ProfileRepository` for load, save, list and delete; reports `StorageError`
#         messages to the view.
#   - Phase 2: `PlannerPresenter` for income, deadline and top-up planning.
#   - Phase 4: `PullLogPresenter` for the log and rate estimation.
#
# Rules:
#   - Parsing user text (comma decimals such as "1,3", percent signs, blank fields) happens
#     here, in one small private parser class `InputParser`, not scattered across views.
#   - Presenters expose methods and callbacks; they do not create widgets.
#   - If this file grows beyond roughly 400 lines, split it into `ui/presenters/` with one file
#     per presenter and keep the same public names.
