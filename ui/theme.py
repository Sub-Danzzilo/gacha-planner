from __future__ import annotations

import enum
import tkinter as tk
from collections.abc import Iterator
from dataclasses import dataclass
from tkinter import ttk


class Theme(enum.Enum):
    LIGHT = "light"
    DARK = "dark"


@dataclass(frozen=True, slots=True)
class Palette:
    background: str
    surface: str
    text: str
    muted: str
    accent: str
    grid: str


LIGHT_PALETTE = Palette(
    background="#f4f4f2",
    surface="#ffffff",
    text="#1f1f1f",
    muted="#5c5c5c",
    accent="#2f6f9f",
    grid="#d8d8d8",
)

DARK_PALETTE = Palette(
    background="#1f1f1f",
    surface="#2b2b2b",
    text="#ececec",
    muted="#a9a9a9",
    accent="#7fb8e6",
    grid="#3d3d3d",
)

_PALETTES = {Theme.LIGHT: LIGHT_PALETTE, Theme.DARK: DARK_PALETTE}


def palette_for(theme: Theme) -> Palette:
    return _PALETTES[theme]


def apply_theme(root: tk.Tk, theme: Theme) -> None:
    palette = palette_for(theme)
    style = ttk.Style(root)
    style.theme_use("clam")
    root.configure(background=palette.background)
    _style_combobox_popdowns(root, palette)

    style.configure(
        ".",
        background=palette.background,
        foreground=palette.text,
        bordercolor=palette.grid,
        lightcolor=palette.surface,
        darkcolor=palette.surface,
        troughcolor=palette.background,
        selectbackground=palette.accent,
        selectforeground=palette.surface,
    )

    style.configure("TFrame", background=palette.background)
    style.configure("TLabel", background=palette.background, foreground=palette.text)
    style.configure("TSeparator", background=palette.grid)
    style.configure("TLabelframe", background=palette.background, bordercolor=palette.grid)
    style.configure("TLabelframe.Label", background=palette.background, foreground=palette.text)

    style.configure("TButton", background=palette.surface, foreground=palette.text)
    style.map(
        "TButton",
        background=[
            ("pressed", palette.accent),
            ("active", palette.accent),
            ("disabled", palette.background),
        ],
        foreground=[
            ("pressed", palette.surface),
            ("active", palette.surface),
            ("disabled", palette.muted),
        ],
        bordercolor=[("pressed", palette.accent), ("active", palette.accent)],
        lightcolor=[("pressed", palette.accent), ("active", palette.accent)],
        darkcolor=[("pressed", palette.accent), ("active", palette.accent)],
    )

    style.configure(
        "TEntry",
        fieldbackground=palette.surface,
        foreground=palette.text,
        insertcolor=palette.text,
    )
    style.map(
        "TEntry",
        fieldbackground=[("readonly", palette.background), ("disabled", palette.background)],
        foreground=[("disabled", palette.muted)],
        bordercolor=[("focus", palette.accent)],
        lightcolor=[("focus", palette.accent)],
        darkcolor=[("focus", palette.accent)],
        selectbackground=[("!focus", palette.accent)],
        selectforeground=[("!focus", palette.surface)],
    )

    style.configure(
        "TCombobox",
        fieldbackground=palette.surface,
        foreground=palette.text,
        background=palette.surface,
        arrowcolor=palette.text,
    )
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", palette.surface), ("disabled", palette.background)],
        foreground=[("readonly", palette.text), ("disabled", palette.muted)],
        background=[
            ("pressed", palette.accent),
            ("active", palette.surface),
            ("disabled", palette.background),
        ],
        arrowcolor=[("pressed", palette.surface), ("active", palette.accent)],
        bordercolor=[("focus", palette.accent)],
        lightcolor=[("focus", palette.accent)],
        darkcolor=[("focus", palette.accent)],
    )
    style.configure(
        "ComboboxPopdownFrame",
        background=palette.surface,
        bordercolor=palette.grid,
    )

    style.configure(
        "TCheckbutton",
        background=palette.background,
        foreground=palette.text,
        indicatorbackground=palette.surface,
        indicatorforeground=palette.text,
    )
    style.map(
        "TCheckbutton",
        background=[("active", palette.background)],
        foreground=[("active", palette.text), ("disabled", palette.muted)],
        indicatorbackground=[
            ("selected", palette.accent),
            ("disabled", palette.background),
        ],
        indicatorforeground=[("selected", palette.surface), ("disabled", palette.muted)],
    )

    style.configure("TNotebook", background=palette.background, borderwidth=0)
    style.configure("TNotebook.Tab", background=palette.background, foreground=palette.muted)
    style.map(
        "TNotebook.Tab",
        background=[("selected", palette.accent), ("active", palette.surface)],
        foreground=[("selected", palette.surface), ("active", palette.text)],
    )

    style.configure(
        "Treeview",
        background=palette.surface,
        fieldbackground=palette.surface,
        foreground=palette.text,
    )
    style.map(
        "Treeview",
        background=[("selected", palette.accent)],
        foreground=[("selected", palette.surface)],
    )
    style.configure(
        "Treeview.Heading",
        background=palette.background,
        foreground=palette.text,
        bordercolor=palette.grid,
    )
    style.map(
        "Treeview.Heading",
        background=[("active", palette.surface)],
        foreground=[("active", palette.text)],
        bordercolor=[("active", palette.accent)],
    )

    style.configure(
        "TScrollbar",
        background=palette.surface,
        troughcolor=palette.background,
        arrowcolor=palette.text,
        bordercolor=palette.grid,
    )
    style.map(
        "TScrollbar",
        background=[("pressed", palette.accent), ("active", palette.surface)],
        arrowcolor=[("pressed", palette.surface), ("active", palette.accent)],
    )

    style.configure("Horizontal.TProgressbar", background=palette.accent)


def _style_combobox_popdowns(root: tk.Misc, palette: Palette) -> None:
    """The dropdown list of a combobox is a plain listbox, so it only reads the option database."""
    root.option_add("*TCombobox*Listbox.background", palette.surface)
    root.option_add("*TCombobox*Listbox.foreground", palette.text)
    root.option_add("*TCombobox*Listbox.selectBackground", palette.accent)
    root.option_add("*TCombobox*Listbox.selectForeground", palette.surface)
    root.option_add("*TCombobox*Listbox.borderWidth", 0)
    for widget in _descendants(root):
        if isinstance(widget, ttk.Combobox):
            _recolor_popdown_list(widget, palette)


def _descendants(widget: tk.Misc) -> Iterator[tk.Misc]:
    for child in widget.winfo_children():
        yield child
        yield from _descendants(child)


def _recolor_popdown_list(combobox: ttk.Combobox, palette: Palette) -> None:
    """A popdown list is created the first time the combobox is posted and keeps its colors."""
    listbox = f"{combobox}.popdown.f.l"
    if not combobox.tk.call("winfo", "exists", listbox):
        return
    combobox.tk.call(
        listbox,
        "configure",
        "-background",
        palette.surface,
        "-foreground",
        palette.text,
        "-selectbackground",
        palette.accent,
        "-selectforeground",
        palette.surface,
    )
