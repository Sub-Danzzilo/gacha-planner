from __future__ import annotations

import tkinter as tk
from collections.abc import Callable, Mapping, Sequence
from tkinter import ttk

from services.planner_service import PlanReport
from ui.charts import FigureFrame, build_cumulative_figure
from ui.parsing import format_money, format_percent
from ui.theme import Palette

_PADDING = 8
_EMPTY = "-"


class ResultView(ttk.Frame):
    """Shows a PlanReport and the cumulative chance chart."""

    def __init__(self, master: tk.Misc, palette: Callable[[], Palette]) -> None:
        super().__init__(master, padding=_PADDING)
        self._palette = palette
        self._labels: dict[str, ttk.Label] = {}
        for key in ("total", "chance", "p50", "p90", "p99", "expected", "money"):
            label = ttk.Label(self, text=_EMPTY)
            label.pack(anchor="w", pady=1)
            self._labels[key] = label
        self._chart = FigureFrame(self)
        self._chart.pack(fill="both", expand=True, pady=(10, 0))
        self.clear()

    def show(self, report: PlanReport) -> None:
        self._labels["total"].configure(text=f"Pulls you can buy: {report.total_pulls}")
        self._labels["chance"].configure(
            text=f"Success chance: {format_percent(report.success_probability)}"
        )
        self._labels["p50"].configure(
            text=f"Pulls for 50% confidence: {_pulls_text(report.pulls_for_50)}"
        )
        self._labels["p90"].configure(
            text=f"Pulls for 90% confidence: {_pulls_text(report.pulls_for_90)}"
        )
        self._labels["p99"].configure(
            text=f"Pulls for 99% confidence: {_pulls_text(report.pulls_for_99)}"
        )
        self._labels["expected"].configure(
            text=f"Average pulls to the first target: {report.expected_pulls:.1f}"
        )
        cost = (
            "not calculated"
            if report.real_money_cost is None
            else format_money(report.real_money_cost)
        )
        self._labels["money"].configure(text=f"Estimated top-up cost for 90%: {cost}")

    def show_curve(self, curve: Sequence[float], markers: Mapping[str, int | None]) -> None:
        self._chart.set_figure(build_cumulative_figure(curve, markers, self._palette()))

    def clear(self) -> None:
        self._labels["total"].configure(text="Pulls you can buy: -")
        self._labels["chance"].configure(text="Success chance: -")
        self._labels["p50"].configure(text="Pulls for 50% confidence: -")
        self._labels["p90"].configure(text="Pulls for 90% confidence: -")
        self._labels["p99"].configure(text="Pulls for 99% confidence: -")
        self._labels["expected"].configure(text="Average pulls to the first target: -")
        self._labels["money"].configure(text="Estimated top-up cost for 90%: -")


def _pulls_text(pulls: int | None) -> str:
    return "more than 2000 pulls" if pulls is None else f"{pulls} pulls"
