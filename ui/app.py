# Root window and navigation. Phase 1.
#
# Class `App(tk.Tk)`:
#   - `__init__(self, profile_presenter, banner_presenter, currency_presenter, results_presenter)`
#         Receives presenters from `main.py`; does not construct domain objects itself.
#   - Sets title, minimum window size and a `ttk.Notebook` with one tab per view:
#         banner, currency, results (phase 1); planner (phase 2); pull log (phase 4).
#   - Builds a menu bar with: profile new, open, save, save as, quit.
#   - Shows storage and validation errors through a single `show_error(message: str)` method
#     using `messagebox`, so views do not each implement their own dialog code.
#   - Handles the window close event: ask to save when there are unsaved changes.
#
# Rules:
#   - Use ttk widgets and a consistent padding constant defined once at the top of the module.
#   - Keep this file about layout and wiring only.
#   - Dark mode is phase 5; structure colors through a small theme object only when that phase
#     starts, not before.
