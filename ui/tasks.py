from __future__ import annotations

import queue
import threading
import tkinter as tk
from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, TypeVar, cast

T = TypeVar("T")

_POLL_MS = 50


@dataclass(frozen=True, slots=True)
class _Progress:
    done: int
    total: int


class BackgroundTask(Generic[T]):
    """Runs heavy work on a background thread and hands results back to the Tk event loop.

    Only one task is active per instance: calling ``start`` while a task is running cancels
    watching the old one. ``cancel`` stops watching; work already running still finishes on the
    background thread and its result is discarded.
    """

    def __init__(self, widget: tk.Misc) -> None:
        self._widget = widget
        self._messages: queue.Queue[tuple[int, str, object]] = queue.Queue()
        self._generation = 0

    def start(
        self,
        work: Callable[[Callable[[int, int], None]], T],
        on_progress: Callable[[int, int], None],
        on_done: Callable[[T], None],
        on_error: Callable[[Exception], None],
    ) -> None:
        self._generation += 1
        generation = self._generation

        def report(done: int, total: int) -> None:
            self._messages.put((generation, "progress", _Progress(done, total)))

        def runner() -> None:
            try:
                result = work(report)
            except Exception as exc:
                self._messages.put((generation, "error", exc))
            else:
                self._messages.put((generation, "done", result))

        threading.Thread(target=runner, daemon=True).start()
        self._widget.after(_POLL_MS, lambda: self._poll(generation, on_progress, on_done, on_error))

    def cancel(self) -> None:
        self._generation += 1

    def _poll(
        self,
        generation: int,
        on_progress: Callable[[int, int], None],
        on_done: Callable[[T], None],
        on_error: Callable[[Exception], None],
    ) -> None:
        finished = False
        while not finished:
            try:
                source, kind, payload = self._messages.get_nowait()
            except queue.Empty:
                break
            if source != generation or generation != self._generation:
                continue
            if kind == "progress":
                progress = cast(_Progress, payload)
                on_progress(progress.done, progress.total)
            elif kind == "done":
                on_done(cast(T, payload))
                finished = True
            else:
                on_error(cast(Exception, payload))
                finished = True
        if not finished and generation == self._generation:
            self._widget.after(
                _POLL_MS, lambda: self._poll(generation, on_progress, on_done, on_error)
            )
