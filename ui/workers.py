# Background work for the Tkinter UI. Phase 1.
#
# Tkinter widgets must only be touched from the main thread. This module runs slow
# computations elsewhere and hands results back safely.
#
# Class `BackgroundTask[T]` (generic):
#   - `__init__(self, root: tk.Misc, work: Callable[[ProgressReporter], T],
#               on_done: Callable[[T], None], on_error: Callable[[Exception], None],
#               on_progress: Callable[[int, int], None] | None = None)`
#   - `start(self) -> None`      runs `work` in a `threading.Thread` (daemon)
#   - `cancel(self) -> None`     sets a flag that `work` can check through the reporter
#
# Class `ProgressReporter`:
#   - `report(self, done: int, total: int) -> None`
#   - `cancelled -> bool`
#
# Mechanism: the worker thread puts messages into a `queue.Queue`; the main thread polls it with
# `root.after(50, ...)` and invokes the callbacks. Do not call widget methods from the worker
# thread. Stop polling once the task is finished or cancelled.
#
# Only one task per presenter should run at a time; starting a new one cancels the previous.
