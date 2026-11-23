from __future__ import annotations

import tkinter as tk
from collections.abc import Mapping, Sequence
from tkinter import ttk

from matplotlib.axes import Axes
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from core.simulator import SimulationResult
from ui.theme import Palette

_MARKER_LEVELS = (0.5, 0.9, 0.99)
_MAX_BINS = 60


def build_cumulative_figure(
    curve: Sequence[float], markers: Mapping[str, int | None], palette: Palette
) -> Figure:
    figure = _new_figure(palette)
    axes = figure.add_subplot(111)
    axes.plot(range(1, len(curve) + 1), list(curve), color=palette.accent, linewidth=2)
    for level in _MARKER_LEVELS:
        axes.axhline(level, color=palette.grid, linewidth=1, linestyle="--")
        axes.annotate(
            f"{level:.0%}",
            xy=(0.01, level),
            xycoords=("axes fraction", "data"),
            color=palette.muted,
            fontsize=8,
            va="bottom",
        )
    for label, pull in markers.items():
        if pull is None:
            continue
        axes.axvline(pull, color=palette.muted, linewidth=1, linestyle=":")
        axes.annotate(
            f"{label}: {pull}",
            xy=(pull, 0.02),
            color=palette.text,
            fontsize=8,
            rotation=90,
        )
    _finish_axes(
        axes,
        palette,
        title="Cumulative success chance",
        xlabel="Pulls",
        ylabel="Chance",
    )
    axes.set_ylim(0.0, 1.05)
    figure.tight_layout()
    return figure


def build_histogram_figure(result: SimulationResult, palette: Palette) -> Figure:
    figure = _new_figure(palette)
    axes = figure.add_subplot(111)
    bins = min(_MAX_BINS, max(1, result.max_pulls))
    axes.hist(
        result.samples,
        bins=bins,
        range=(1, result.max_pulls + 1),
        color=palette.accent,
        edgecolor=palette.surface,
    )
    _finish_axes(
        axes,
        palette,
        title="Simulation results",
        xlabel="Pulls",
        ylabel="Trials",
    )
    axes.set_xlim(1, result.max_pulls + 1)
    figure.tight_layout()
    return figure


class FigureFrame(ttk.Frame):
    """Wraps a single matplotlib Figure inside a Tk widget."""

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master)
        self._canvas: FigureCanvasTkAgg | None = None

    def set_figure(self, figure: Figure) -> None:
        if self._canvas is None:
            self._canvas = FigureCanvasTkAgg(figure, master=self)
            self._canvas.get_tk_widget().pack(fill="both", expand=True)
        else:
            self._canvas.figure = figure
        self._canvas.draw()


def _new_figure(palette: Palette) -> Figure:
    figure = Figure(figsize=(6.4, 3.6), dpi=100)
    figure.patch.set_facecolor(palette.background)
    return figure


def _finish_axes(axes: Axes, palette: Palette, title: str, xlabel: str, ylabel: str) -> None:
    axes.set_facecolor(palette.surface)
    axes.set_title(title, color=palette.text)
    axes.set_xlabel(xlabel, color=palette.text)
    axes.set_ylabel(ylabel, color=palette.text)
    axes.tick_params(colors=palette.muted)
    axes.grid(True, color=palette.grid, linewidth=0.5, alpha=0.6)
    for spine in axes.spines.values():
        spine.set_color(palette.grid)
