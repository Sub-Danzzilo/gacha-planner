from __future__ import annotations

import tkinter as tk
from collections.abc import Callable, Sequence
from tkinter import ttk

from core.models.banner import Banner, RateTier
from core.models.currency import Currency, Money
from core.models.item import Item
from core.models.pity import PityConfig, PullRule
from ui.parsing import InputError, parse_decimal, parse_percent, parse_positive_int

_PADDING = 8
_PITY_NONE = "No pity"
_PITY_HARD = "Hard pity"
_PITY_SOFT = "Soft pity"
_COLUMN_WIDTH = 22


class BannerView(ttk.Frame):
    """Banner input form; every text conversion goes through ui/parsing.py."""

    def __init__(
        self,
        master: tk.Misc,
        on_submit: Callable[[Banner], None],
        on_error: Callable[[str], None],
        currencies: Callable[[], Sequence[Currency]],
        on_random_name: Callable[[], str],
    ) -> None:
        super().__init__(master, padding=_PADDING)
        self._on_submit = on_submit
        self._on_error = on_error
        self._currencies = currencies
        self._on_random_name = on_random_name
        self._items: list[tuple[str, bool]] = []

        self._banner_name = tk.StringVar()
        self._tier = tk.StringVar(value="5-star")
        self._rate = tk.StringVar(value="1.3")
        self._pity_kind = tk.StringVar(value=_PITY_NONE)
        self._soft_start = tk.StringVar(value="74")
        self._soft_step = tk.StringVar(value="6")
        self._hard_pity = tk.StringVar(value="90")
        self._cost = tk.StringVar(value="160")
        self._currency = tk.StringVar()
        self._item_name = tk.StringVar()
        self._item_featured = tk.BooleanVar(value=False)

        self._banner_names = tk.StringVar(value="No banners saved yet")
        self._soft_row: ttk.Frame
        self._soft_step_row: ttk.Frame
        self._hard_row: ttk.Frame
        self._item_tree: ttk.Treeview
        self._currency_box: ttk.Combobox
        self._build()

    def refresh_currencies(self) -> None:
        codes = [currency.code for currency in self._currencies()]
        self._currency_box.configure(values=codes)
        if codes and not self._currency.get():
            self._currency.set(codes[0])

    def show_banners(self, names: Sequence[str]) -> None:
        if names:
            self._banner_names.set("Saved: " + ", ".join(names))
        else:
            self._banner_names.set("No banners saved yet")

    def _build(self) -> None:
        ttk.Label(self, text="Banner name").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Entry(self, textvariable=self._banner_name, width=_COLUMN_WIDTH).grid(
            row=0, column=1, sticky="we", pady=2
        )

        ttk.Label(self, text="Tier name").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Entry(self, textvariable=self._tier, width=_COLUMN_WIDTH).grid(
            row=1, column=1, sticky="we", pady=2
        )

        ttk.Label(self, text="Base rate (%)").grid(row=2, column=0, sticky="w", pady=2)
        ttk.Entry(self, textvariable=self._rate, width=_COLUMN_WIDTH).grid(
            row=2, column=1, sticky="we", pady=2
        )

        ttk.Label(self, text="Pity type").grid(row=3, column=0, sticky="w", pady=2)
        pity_box = ttk.Combobox(
            self,
            textvariable=self._pity_kind,
            values=(_PITY_NONE, _PITY_HARD, _PITY_SOFT),
            state="readonly",
            width=_COLUMN_WIDTH - 2,
        )
        pity_box.grid(row=3, column=1, sticky="we", pady=2)
        pity_box.bind("<<ComboboxSelected>>", lambda _event: self._refresh_pity_rows())

        self._soft_row = self._build_field_row(
            row=4, label="Soft pity starts at pull", variable=self._soft_start
        )
        self._soft_step_row = self._build_field_row(
            row=5, label="Soft pity step (%)", variable=self._soft_step
        )
        self._hard_row = self._build_field_row(
            row=6, label="Hard pity (pull)", variable=self._hard_pity
        )

        ttk.Label(self, text="Cost per pull").grid(row=7, column=0, sticky="w", pady=2)
        ttk.Entry(self, textvariable=self._cost, width=_COLUMN_WIDTH).grid(
            row=7, column=1, sticky="we", pady=2
        )

        ttk.Label(self, text="Cost currency").grid(row=8, column=0, sticky="w", pady=2)
        self._currency_box = ttk.Combobox(
            self, textvariable=self._currency, state="readonly", width=_COLUMN_WIDTH - 2
        )
        self._currency_box.grid(row=8, column=1, sticky="we", pady=2)

        ttk.Label(self, textvariable=self._banner_names, wraplength=360).grid(
            row=9, column=0, columnspan=2, sticky="w", pady=(8, 2)
        )

        items_frame = ttk.LabelFrame(self, text="Items in this tier", padding=_PADDING)
        items_frame.grid(row=10, column=0, columnspan=2, sticky="nsew", pady=(8, 2))

        ttk.Label(items_frame, text="Item name").grid(row=0, column=0, sticky="w")
        ttk.Entry(items_frame, textvariable=self._item_name, width=_COLUMN_WIDTH).grid(
            row=0, column=1, sticky="we", padx=4
        )
        ttk.Checkbutton(items_frame, text="Featured", variable=self._item_featured).grid(
            row=0, column=2, sticky="w"
        )
        ttk.Button(items_frame, text="Random name", command=self._fill_random_name).grid(
            row=0, column=3, padx=4
        )
        ttk.Button(items_frame, text="Add item", command=self._add_item).grid(
            row=0, column=4, padx=4
        )

        self._item_tree = ttk.Treeview(
            items_frame, columns=("featured",), show="tree headings", height=6
        )
        self._item_tree.heading("#0", text="Item")
        self._item_tree.heading("featured", text="Featured")
        self._item_tree.column("featured", width=80, anchor="center")
        self._item_tree.grid(row=1, column=0, columnspan=5, sticky="nsew", pady=6)

        ttk.Button(items_frame, text="Remove selected item", command=self._remove_item).grid(
            row=2, column=0, columnspan=2, sticky="w"
        )

        ttk.Button(self, text="Save banner", command=self._submit).grid(
            row=11, column=0, columnspan=2, sticky="e", pady=(10, 0)
        )

        self.columnconfigure(1, weight=1)
        self.rowconfigure(10, weight=1)
        items_frame.columnconfigure(1, weight=1)
        items_frame.rowconfigure(1, weight=1)
        self._refresh_pity_rows()

    def _build_field_row(self, row: int, label: str, variable: tk.StringVar) -> ttk.Frame:
        container = ttk.Frame(self)
        container.grid(row=row, column=0, columnspan=2, sticky="we")
        ttk.Label(container, text=label).grid(row=0, column=0, sticky="w", pady=2)
        ttk.Entry(container, textvariable=variable, width=_COLUMN_WIDTH).grid(
            row=0, column=1, sticky="we", pady=2
        )
        container.columnconfigure(1, weight=1)
        return container

    def _refresh_pity_rows(self) -> None:
        kind = self._pity_kind.get()
        for row in (self._soft_row, self._soft_step_row):
            if kind == _PITY_SOFT:
                row.grid()
            else:
                row.grid_remove()
        if kind == _PITY_NONE:
            self._hard_row.grid_remove()
        else:
            self._hard_row.grid()

    def _fill_random_name(self) -> None:
        self._item_name.set(self._on_random_name())

    def _add_item(self) -> None:
        name = self._item_name.get().strip()
        if not name:
            self._on_error("Item name cannot be empty")
            return
        if any(existing == name for existing, _ in self._items):
            self._on_error(f"Item {name!r} is already in the list")
            return
        self._items.append((name, self._item_featured.get()))
        self._item_name.set("")
        self._refresh_item_tree()

    def _remove_item(self) -> None:
        selected = self._item_tree.selection()
        if not selected:
            self._on_error("Select an item to remove first")
            return
        del self._items[int(selected[0])]
        self._refresh_item_tree()

    def _refresh_item_tree(self) -> None:
        self._item_tree.delete(*self._item_tree.get_children())
        for index, (name, featured) in enumerate(self._items):
            self._item_tree.insert(
                "", "end", iid=str(index), text=name, values=("yes" if featured else "no",)
            )

    def _submit(self) -> None:
        try:
            banner = self._build_banner()
        except ValueError as exc:
            self._on_error(str(exc))
            return
        self._on_submit(banner)
        self._banner_name.set("")
        self._items.clear()
        self._refresh_item_tree()

    def _build_banner(self) -> Banner:
        name = self._banner_name.get().strip()
        if not name:
            raise InputError("Banner name cannot be empty")
        tier_name = self._tier.get().strip()
        if not tier_name:
            raise InputError("Tier name cannot be empty")
        base_rate = parse_percent(self._rate.get())
        currency = self._selected_currency()
        items = tuple(
            Item(name=item_name, tier_name=tier_name, is_featured=featured)
            for item_name, featured in self._items
        )
        return Banner(
            name=name,
            tiers=(RateTier(name=tier_name, rule=PullRule(base_rate, self._build_pity())),),
            items=items,
            cost_per_pull=Money(parse_decimal(self._cost.get()), currency),
        )

    def _build_pity(self) -> PityConfig | None:
        kind = self._pity_kind.get()
        if kind == _PITY_NONE:
            return None
        hard_pity = parse_positive_int(self._hard_pity.get())
        if kind == _PITY_HARD:
            return PityConfig(hard_pity=hard_pity)
        return PityConfig(
            hard_pity=hard_pity,
            soft_pity_start=parse_positive_int(self._soft_start.get()),
            soft_pity_step=parse_percent(self._soft_step.get()),
        )

    def _selected_currency(self) -> Currency:
        code = self._currency.get()
        for currency in self._currencies():
            if currency.code == code:
                return currency
        raise InputError("Select a cost currency first")
