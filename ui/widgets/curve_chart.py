# Cumulative probability chart. Phase 3.
#
# Class `CurveChart(ttk.Frame)`:
#   - Embeds a matplotlib `Figure` using `FigureCanvasTkAgg` (backend `TkAgg`).
#   - `update_curve(self, cumulative: Sequence[float], budget_pulls: int | None,
#                   markers: Mapping[str, int]) -> None`
#         Plots probability of success versus number of pulls. Draws horizontal guide lines or
#         markers at 50%, 90% and 99% and a vertical line at the user's budget.
#   - Optional second series for the simulated curve so the user can see both.
#
# Rules:
#   - Create the `Figure` once and update its data on later calls; do not create a new figure
#     per update (memory growth).
#   - Do not import `pyplot`; use `matplotlib.figure.Figure` directly to avoid global state.
#   - Axis labels and tick formatting should be readable; percentages on the y axis.
#   - matplotlib is imported only in this file so the rest of the UI works without it.
