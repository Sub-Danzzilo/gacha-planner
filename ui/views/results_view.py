# Results display. Phase 1 (chart added in phase 3).
#
# Class `ResultsView(ttk.Frame)`:
#   - Inputs: budget in pulls or in currency (the presenter converts), starting pity,
#     "Calculate" and "Run simulation" buttons, trial count field.
#   - Outputs rendered from a `ResultsViewModel`:
#         chance of success with the budget, pulls for 50%, 90% and 99% confidence,
#         expected pulls, and a warning label when the distribution was truncated.
#   - A progress bar tied to the background simulation, with a cancel button.
#   - Phase 2: also show total real-money cost for each figure in the user's display currency.
#   - Phase 3: embed `CurveChart` below the numbers.
#
# Rules:
#   - Format numbers in one place (a small private formatter class in this file): percentages
#     with one or two decimals, pull counts as integers, money with the currency code.
#   - The view disables inputs while a task runs and re-enables them in the done and error
#     callbacks.
