from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from decimal import Decimal
from tkinter import ttk

from core.exchange import ExchangeRate
from core.models.currency import Currency, CurrencyKind, Money
from core.models.profile import GameProfile
from core.models.topup import TopUpPackage
from ui.parsing import (
    describe_error,
    format_money,
    parse_decimal,
    parse_non_negative_int,
    parse_positive_int,
)

_PADDING = 8
_KIND_GAME = "Game"
_KIND_REAL = "Real money"


def _kind_label(kind: CurrencyKind) -> str:
    return _KIND_GAME if kind is CurrencyKind.GAME else _KIND_REAL


class CurrencyView(ttk.Frame):
    """Currency, balance, top-up package and manual rate tables and forms."""

    def __init__(
        self,
        master: tk.Misc,
        on_currency: Callable[[Currency, Decimal], None],
        on_package: Callable[[TopUpPackage], None],
        on_rate: Callable[[ExchangeRate], None],
        on_error: Callable[[str], None],
    ) -> None:
        super().__init__(master, padding=_PADDING)
        self._on_currency = on_currency
        self._on_package = on_package
        self._on_rate = on_rate
        self._on_error = on_error

        self._code = tk.StringVar()
        self._currency_name = tk.StringVar()
        self._kind = tk.StringVar(value=_KIND_GAME)
        self._decimals = tk.StringVar(value="0")
        self._balance = tk.StringVar(value="0")

        self._price = tk.StringVar(value="0")
        self._price_currency = tk.StringVar()
        self._grant_currency = tk.StringVar()
        self._base_amount = tk.StringVar(value="0")
        self._bonus_amount = tk.StringVar(value="0")
        self._first_bonus = tk.StringVar(value="0")

        self._rate_source = tk.StringVar()
        self._rate_target = tk.StringVar()
        self._rate_value = tk.StringVar(value="1")
        self._known: tuple[Currency, ...] = ()

        self._build()

    def show(self, profile: GameProfile) -> None:
        self._known = profile.currencies
        self._currency_tree.delete(*self._currency_tree.get_children())
        for currency in profile.currencies:
            balance = profile.balances.get(currency.code)
            self._currency_tree.insert(
                "",
                "end",
                values=(
                    currency.code,
                    currency.name,
                    _kind_label(currency.kind),
                    currency.decimals,
                    "" if balance is None else format_money(balance),
                ),
            )

        self._package_tree.delete(*self._package_tree.get_children())
        for package in profile.topup_packages:
            self._package_tree.insert(
                "",
                "end",
                values=(
                    format_money(package.price),
                    package.grants.code,
                    package.total_amount,
                    package.first_purchase_bonus,
                ),
            )

        self._rate_tree.delete(*self._rate_tree.get_children())
        for exchange_rate in profile.exchange_rates:
            self._rate_tree.insert(
                "",
                "end",
                values=(
                    exchange_rate.source_code,
                    exchange_rate.target_code,
                    str(exchange_rate.rate),
                ),
            )

        codes = [currency.code for currency in profile.currencies]
        for box in (
            self._price_currency_box,
            self._grant_currency_box,
            self._rate_source_box,
            self._rate_target_box,
        ):
            box.configure(values=codes)

    def _build(self) -> None:
        currency_frame = ttk.LabelFrame(self, text="Currencies and balances", padding=_PADDING)
        currency_frame.pack(fill="both", expand=True, pady=(0, _PADDING))

        self._currency_tree = ttk.Treeview(
            currency_frame,
            columns=("code", "name", "kind", "decimals", "balance"),
            show="headings",
            height=5,
        )
        for column, title, width in (
            ("code", "Code", 90),
            ("name", "Name", 160),
            ("kind", "Kind", 100),
            ("decimals", "Decimals", 80),
            ("balance", "Balance", 140),
        ):
            self._currency_tree.heading(column, text=title)
            self._currency_tree.column(column, width=width, anchor="w")
        self._currency_tree.pack(fill="both", expand=True)

        form = ttk.Frame(currency_frame)
        form.pack(fill="x", pady=(6, 0))
        ttk.Label(form, text="Code").grid(row=0, column=0, sticky="w")
        ttk.Entry(form, textvariable=self._code, width=12).grid(row=0, column=1, padx=4)
        ttk.Label(form, text="Name").grid(row=0, column=2, sticky="w")
        ttk.Entry(form, textvariable=self._currency_name, width=18).grid(row=0, column=3, padx=4)
        ttk.Label(form, text="Kind").grid(row=0, column=4, sticky="w")
        ttk.Combobox(
            form,
            textvariable=self._kind,
            values=(_KIND_GAME, _KIND_REAL),
            state="readonly",
            width=10,
        ).grid(row=0, column=5, padx=4)
        ttk.Label(form, text="Decimals").grid(row=0, column=6, sticky="w")
        ttk.Entry(form, textvariable=self._decimals, width=4).grid(row=0, column=7, padx=4)
        ttk.Label(form, text="Balance").grid(row=0, column=8, sticky="w")
        ttk.Entry(form, textvariable=self._balance, width=14).grid(row=0, column=9, padx=4)
        ttk.Button(form, text="Save currency", command=self._submit_currency).grid(
            row=0, column=10, padx=(8, 0)
        )

        package_frame = ttk.LabelFrame(self, text="Top-up packages", padding=_PADDING)
        package_frame.pack(fill="both", expand=True, pady=(0, _PADDING))
        self._package_tree = ttk.Treeview(
            package_frame,
            columns=("price", "grants", "total", "first_bonus"),
            show="headings",
            height=4,
        )
        for column, title, width in (
            ("price", "Price", 140),
            ("grants", "Grants", 140),
            ("total", "Amount", 100),
            ("first_bonus", "First purchase bonus", 150),
        ):
            self._package_tree.heading(column, text=title)
            self._package_tree.column(column, width=width, anchor="w")
        self._package_tree.pack(fill="both", expand=True)

        package_form = ttk.Frame(package_frame)
        package_form.pack(fill="x", pady=(6, 0))
        ttk.Label(package_form, text="Price").grid(row=0, column=0, sticky="w")
        ttk.Entry(package_form, textvariable=self._price, width=12).grid(row=0, column=1, padx=4)
        self._price_currency_box = ttk.Combobox(
            package_form, textvariable=self._price_currency, state="readonly", width=10
        )
        self._price_currency_box.grid(row=0, column=2, padx=4)
        ttk.Label(package_form, text="Grants").grid(row=0, column=3, sticky="w")
        self._grant_currency_box = ttk.Combobox(
            package_form, textvariable=self._grant_currency, state="readonly", width=10
        )
        self._grant_currency_box.grid(row=0, column=4, padx=4)
        ttk.Label(package_form, text="Base amount").grid(row=0, column=5, sticky="w")
        ttk.Entry(package_form, textvariable=self._base_amount, width=8).grid(
            row=0, column=6, padx=4
        )
        ttk.Label(package_form, text="Bonus").grid(row=0, column=7, sticky="w")
        ttk.Entry(package_form, textvariable=self._bonus_amount, width=8).grid(
            row=0, column=8, padx=4
        )
        ttk.Label(package_form, text="First bonus").grid(row=0, column=9, sticky="w")
        ttk.Entry(package_form, textvariable=self._first_bonus, width=8).grid(
            row=0, column=10, padx=4
        )
        ttk.Button(package_form, text="Add package", command=self._submit_package).grid(
            row=0, column=11, padx=(8, 0)
        )

        rate_frame = ttk.LabelFrame(self, text="Manual exchange rates", padding=_PADDING)
        rate_frame.pack(fill="both", expand=True)
        self._rate_tree = ttk.Treeview(
            rate_frame, columns=("source", "target", "rate"), show="headings", height=4
        )
        for column, title, width in (
            ("source", "From", 120),
            ("target", "To", 120),
            ("rate", "Rate", 160),
        ):
            self._rate_tree.heading(column, text=title)
            self._rate_tree.column(column, width=width, anchor="w")
        self._rate_tree.pack(fill="both", expand=True)

        rate_form = ttk.Frame(rate_frame)
        rate_form.pack(fill="x", pady=(6, 0))
        ttk.Label(rate_form, text="From").grid(row=0, column=0, sticky="w")
        self._rate_source_box = ttk.Combobox(
            rate_form, textvariable=self._rate_source, state="readonly", width=10
        )
        self._rate_source_box.grid(row=0, column=1, padx=4)
        ttk.Label(rate_form, text="To").grid(row=0, column=2, sticky="w")
        self._rate_target_box = ttk.Combobox(
            rate_form, textvariable=self._rate_target, state="readonly", width=10
        )
        self._rate_target_box.grid(row=0, column=3, padx=4)
        ttk.Label(rate_form, text="Rate").grid(row=0, column=4, sticky="w")
        ttk.Entry(rate_form, textvariable=self._rate_value, width=14).grid(row=0, column=5, padx=4)
        ttk.Button(rate_form, text="Save rate", command=self._submit_rate).grid(
            row=0, column=6, padx=(8, 0)
        )

    def _submit_currency(self) -> None:
        try:
            currency = Currency(
                code=self._code.get().strip().upper(),
                name=self._currency_name.get().strip(),
                kind=CurrencyKind.GAME if self._kind.get() == _KIND_GAME else CurrencyKind.REAL,
                decimals=parse_non_negative_int(self._decimals.get()),
            )
            self._on_currency(currency, parse_decimal(self._balance.get()))
        except ValueError as exc:
            self._on_error(describe_error(exc))

    def _submit_package(self) -> None:
        try:
            package = TopUpPackage(
                price=Money(
                    parse_decimal(self._price.get()), self._currency(self._price_currency.get())
                ),
                grants=self._currency(self._grant_currency.get()),
                base_amount=parse_positive_int(self._base_amount.get()),
                bonus_amount=parse_non_negative_int(self._bonus_amount.get()),
                first_purchase_bonus=parse_non_negative_int(self._first_bonus.get()),
            )
        except ValueError as exc:
            self._on_error(describe_error(exc))
            return
        self._on_package(package)

    def _submit_rate(self) -> None:
        try:
            exchange_rate = ExchangeRate(
                source_code=self._rate_source.get(),
                target_code=self._rate_target.get(),
                rate=parse_decimal(self._rate_value.get()),
            )
        except ValueError as exc:
            self._on_error(describe_error(exc))
            return
        self._on_rate(exchange_rate)

    def _currency(self, code: str) -> Currency:
        for currency in self._known:
            if currency.code == code:
                return currency
        raise ValueError("Select a currency from the list first")
