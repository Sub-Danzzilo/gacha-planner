# Pull history and rate estimation. Phase 4.
#
# Class `PullLogView(ttk.Frame)`:
#   - A table of recorded pulls (number, tier, item) with add-one, paste-many (CSV text) and
#     clear actions.
#   - A section that shows the estimated rate for a chosen tier with its interval, and buttons
#     to use the lower, estimated or upper value to fill the banner form and recompute.
#   - Show the sample size next to every estimate, and show a clear notice when the sample is
#     small.
#
# Rules:
#   - Parsing and estimation go through `PullLogPresenter`. No statistics in the view.
