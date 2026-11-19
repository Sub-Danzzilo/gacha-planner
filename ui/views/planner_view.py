# Income, deadline and purchase planning. Phase 2.
#
# Class `PlannerView(ttk.Frame)`:
#   - Inputs: today's date (default from the presenter), banner deadline, daily income per
#     currency, weekly income per currency, one-time income rows (date, currency, amount).
#   - Outputs: projected pulls at the deadline, success chance at the deadline, shortfall in
#     pulls, extra income per day needed to reach a chosen target, and the cheapest top-up plan
#     (packages, counts, total cost in the display currency, wasted currency).
#   - Dates are entered as text in ISO format (YYYY-MM-DD); the presenter parses and reports
#     errors. Do not add a third-party date picker.
#
# Rules:
#   - Same split as the other views: no calculation here, only `PlannerPresenter` calls.
