from __future__ import annotations

import tkinter as tk
from collections.abc import Callable, Sequence
from datetime import date
from tkinter import ttk

from core.budget import IncomePeriod, IncomeSource
from core.models.banner import Banner
from core.models.currency import Money
from core.models.pity import PityState
from ui.parsing import (
    describe_error,
    format_money,
    format_percent,
    parse_non_negative_int,
    parse_positive_int,
)

_PADDING = 8
_PERIOD_LABELS: dict[str, IncomePeriod] = {
    "Daily": IncomePeriod.DAILY,
    "Weekly": IncomePeriod.WEEKLY,
    "Monthly": IncomePeriod.MONTHLY,
}


class BudgetView(ttk.Frame):
    """Recurring income and banner deadline form, plus its projection."""

    def __init__(
        self,
        master: tk.Misc,
        on_calculate: Callable[[str, str, PityState, date], None],
        on_error: Callable[[str], None],
    ) -> None:
        super().__init__(master, padding=_PADDING)
        self._on_calculate = on_calculate
        self._on_error = on_error
        self._banners: dict[str, Banner] = {}
        self._incomes: list[IncomeSource] = []

        self._banner = tk.StringVar()
        self._tier = tk.StringVar()
        self._pity = tk.StringVar(value="0")
        self._deadline = tk.StringVar()

        self._income_name = tk.StringVar()
        self._income_currency = tk.StringVar()
        self._income_amount = tk.StringVar()
        self._income_period = tk.StringVar(value="Daily")
        self._income_date = tk.StringVar()

        self._projection = tk.StringVar(value="No projection yet")
        self._build()

    def set_banners(self, banners: Sequence[Banner]) -> None:
        self._banners = {banner.name: banner for banner in banners}
        names = list(self._banners)
        self._banner_box.configure(values=names)
        if names and self._banner.get() not in names:
            self._banner.set(names[0])
        self._refresh_tiers()

    def set_currency_codes(self, codes: Sequence[str]) -> None:
        self._income_currency_box.configure(values=list(codes))
        if codes and self._income_currency.get() not in codes:
            self._income_currency.set(codes[0])

    def get_incomes(self) -> list[IncomeSource]:
        return list(self._incomes)

    def get_deadline(self) -> date | None:
        text = self._deadline.get().strip()
        if not text:
            return None
        try:
            return date.fromisoformat(text)
        except ValueError:
            return None

    def show(self, pulls: int, success_probability: float, daily_income: Money) -> None:
        self._projection.set(
            f"At the deadline: {pulls} pulls, success chance "
            f"{format_percent(success_probability)}. Extra income needed: "
            f"{format_money(daily_income)} per day."
        )

    def _build(self) -> None:
        selection = ttk.LabelFrame(self, text="Banner and deadline", padding=_PADDING)
        selection.pack(fill="x", pady=(0, _PADDING))

        ttk.Label(selection, text="Banner").grid(row=0, column=0, sticky="w")
        self._banner_box = ttk.Combobox(
            selection, textvariable=self._banner, state="readonly", width=22
        )
        self._banner_box.grid(row=0, column=1, padx=4)
        self._banner_box.bind("<<ComboboxSelected>>", lambda _event: self._refresh_tiers())

        ttk.Label(selection, text="Tier").grid(row=0, column=2, sticky="w")
        self._tier_box = ttk.Combobox(
            selection, textvariable=self._tier, state="readonly", width=16
        )
        self._tier_box.grid(row=0, column=3, padx=4)

        ttk.Label(selection, text="Current pity").grid(row=0, column=4, sticky="w")
        ttk.Entry(selection, textvariable=self._pity, width=6).grid(row=0, column=5, padx=4)

        ttk.Label(selection, text="Deadline (YYYY-MM-DD)").grid(row=0, column=6, sticky="w")
        ttk.Entry(selection, textvariable=self._deadline, width=14).grid(row=0, column=7, padx=4)

        income_frame = ttk.LabelFrame(self, text="Recurring income", padding=_PADDING)
        income_frame.pack(fill="both", expand=True, pady=(0, _PADDING))

        form = ttk.Frame(income_frame)
        form.pack(fill="x")
        ttk.Label(form, text="Name").grid(row=0, column=0, sticky="w")
        ttk.Entry(form, textvariable=self._income_name, width=18).grid(row=0, column=1, padx=4)
        ttk.Label(form, text="Currency").grid(row=0, column=2, sticky="w")
        self._income_currency_box = ttk.Combobox(
            form, textvariable=self._income_currency, state="readonly", width=10
        )
        self._income_currency_box.grid(row=0, column=3, padx=4)
        ttk.Label(form, text="Amount").grid(row=0, column=4, sticky="w")
        ttk.Entry(form, textvariable=self._income_amount, width=10).grid(row=0, column=5, padx=4)
        ttk.Label(form, text="Period").grid(row=0, column=6, sticky="w")
        ttk.Combobox(
            form,
            textvariable=self._income_period,
            values=tuple(_PERIOD_LABELS),
            state="readonly",
            width=10,
        ).grid(row=0, column=7, padx=4)
        ttk.Label(form, text="First credit").grid(row=0, column=8, sticky="w")
        ttk.Entry(form, textvariable=self._income_date, width=12).grid(row=0, column=9, padx=4)
        ttk.Button(form, text="Add income", command=self._add_income).grid(
            row=0, column=10, padx=(8, 0)
        )

        self._income_tree = ttk.Treeview(
            income_frame,
            columns=("currency", "amount", "period", "first"),
            show="tree headings",
            height=6,
        )
        self._income_tree.heading("#0", text="Name")
        for column, title, width in (
            ("currency", "Currency", 100),
            ("amount", "Amount", 100),
            ("period", "Period", 100),
            ("first", "First credit", 120),
        ):
            self._income_tree.heading(column, text=title)
            self._income_tree.column(column, width=width, anchor="w")
        self._income_tree.pack(fill="both", expand=True, pady=6)

        ttk.Button(income_frame, text="Remove selected income", command=self._remove_income).pack(
            anchor="w"
        )

        ttk.Label(self, textvariable=self._projection, wraplength=760).pack(
            fill="x", pady=(0, _PADDING)
        )
        ttk.Button(self, text="Project deadline", command=self._calculate).pack(anchor="e")

    def _refresh_tiers(self) -> None:
        banner = self._banners.get(self._banner.get())
        tiers = [] if banner is None else [tier.name for tier in banner.tiers]
        self._tier_box.configure(values=tiers)
        if tiers and self._tier.get() not in tiers:
            self._tier.set(tiers[0])

    def _add_income(self) -> None:
        try:
            source = IncomeSource(
                name=self._income_name.get().strip(),
                currency_code=self._income_currency.get(),
                amount=parse_positive_int(self._income_amount.get()),
                period=_PERIOD_LABELS[self._income_period.get()],
                first_credit=date.fromisoformat(self._income_date.get().strip()),
            )
        except (ValueError, KeyError) as exc:
            self._on_error(describe_error(exc))
            return
        self._incomes.append(source)
        self._income_tree.insert(
            "",
            "end",
            iid=str(len(self._incomes) - 1),
            text=source.name,
            values=(
                source.currency_code,
                source.amount,
                source.period.value,
                source.first_credit.isoformat(),
            ),
        )
        self._income_name.set("")
        self._income_amount.set("")

    def _remove_income(self) -> None:
        selected = self._income_tree.selection()
        if not selected:
            self._on_error("Select an income to remove first")
            return
        del self._incomes[int(selected[0])]
        self._income_tree.delete(*self._income_tree.get_children())
        for index, source in enumerate(self._incomes):
            self._income_tree.insert(
                "",
                "end",
                iid=str(index),
                text=source.name,
                values=(
                    source.currency_code,
                    source.amount,
                    source.period.value,
                    source.first_credit.isoformat(),
                ),
            )

    def _calculate(self) -> None:
        deadline = self.get_deadline()
        if deadline is None:
            self._on_error("Enter the deadline as YYYY-MM-DD")
            return
        banner_name = self._banner.get()
        tier_name = self._tier.get()
        if banner_name not in self._banners or not tier_name:
            self._on_error("Select a banner and a tier first")
            return
        try:
            state = PityState(pity_count=parse_non_negative_int(self._pity.get()))
        except ValueError as exc:
            self._on_error(describe_error(exc))
            return
        self._on_calculate(banner_name, tier_name, state, deadline)
