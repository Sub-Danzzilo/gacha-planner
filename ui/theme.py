from __future__ import annotations

import enum
import tkinter as tk
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

    style.configure(".", background=palette.background, foreground=palette.text)
    style.configure("TFrame", background=palette.background)
    style.configure("TLabel", background=palette.background, foreground=palette.text)
    style.configure("TSeparator", background=palette.grid)
    style.configure("TLabelframe", background=palette.background, foreground=palette.text)
    style.configure("TLabelframe.Label", background=palette.background, foreground=palette.text)
    style.configure("TButton", background=palette.surface, foreground=palette.text)
    style.map(
        "TButton",
        background=[("active", palette.accent)],
        foreground=[("active", palette.surface)],
    )
    style.configure(
        "TEntry", fieldbackground=palette.surface, foreground=palette.text, insertcolor=palette.text
    )
    style.configure(
        "TCombobox",
        fieldbackground=palette.surface,
        foreground=palette.text,
        background=palette.surface,
    )
    style.configure("TCheckbutton", background=palette.background, foreground=palette.text)
    style.map(
        "TCheckbutton",
        background=[("active", palette.background)],
        foreground=[("active", palette.text)],
    )
    style.configure("TNotebook", background=palette.background, borderwidth=0)
    style.configure("TNotebook.Tab", background=palette.surface, foreground=palette.text)
    style.map(
        "TNotebook.Tab",
        background=[("selected", palette.accent)],
        foreground=[("selected", palette.surface)],
    )
    style.configure(
        "Treeview",
        background=palette.surface,
        fieldbackground=palette.surface,
        foreground=palette.text,
    )
    style.configure("Treeview.Heading", background=palette.background, foreground=palette.text)
    style.configure("Horizontal.TProgressbar", background=palette.accent)
