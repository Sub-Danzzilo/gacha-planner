from __future__ import annotations

import random
import tkinter as tk
from datetime import date
from decimal import Decimal
from tkinter import messagebox, simpledialog, ttk

from core.errors import StorageError
from core.exchange import ExchangeRate, ManualRateProvider
from core.models.banner import Banner
from core.models.currency import Currency, CurrencyKind, Money
from core.models.pity import PityState
from core.models.profile import GameProfile
from core.models.topup import TopUpPackage
from core.naming import RandomNameGenerator
from services.planner_service import PlannerService, PlanReport
from storage.profile_repository import ProfileRepository
from ui.parsing import describe_error
from ui.theme import Palette, Theme, apply_theme, palette_for
from ui.views.banner_view import BannerView
from ui.views.budget_view import BudgetView
from ui.views.currency_view import CurrencyView
from ui.views.result_view import ResultView

_TITLE = "Gacha Planner"
_UNSAVED_NAME = "untitled"
_DEFAULT_CURVE_PULLS = 200
_MARKER_MARGIN = 10


def _curve_horizon(markers: dict[str, int | None]) -> int:
    """Long enough to hold the 99% marker so the chart does not cut it off."""
    reachable = [pull for pull in markers.values() if pull is not None]
    if not reachable:
        return _DEFAULT_CURVE_PULLS
    return max(_DEFAULT_CURVE_PULLS, max(reachable) + _MARKER_MARGIN)


class App(tk.Tk):
    """Main window: profile menu, view tabs, and profile persistence."""

    _banner_view: BannerView
    _currency_view: CurrencyView
    _budget_view: BudgetView
    _results_view: ResultView

    def __init__(
        self,
        repository: ProfileRepository,
        provider: ManualRateProvider,
        service: PlannerService,
    ) -> None:
        super().__init__()
        self._repository = repository
        self._provider = provider
        self._service = service
        self._profile = GameProfile(name=_UNSAVED_NAME)
        self._theme = Theme.LIGHT
        self._last_report: PlanReport | None = None
        self._last_curve: list[float] = []
        self._last_markers: dict[str, int | None] = {}
        self._dirty = False
        self._name_generator = RandomNameGenerator(random.Random())

        self.title(_TITLE)
        self.geometry("1020x780")
        self.minsize(940, 700)
        apply_theme(self, self._theme)
        self._build_menu()
        self._build_notebook()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._sync_provider()
        self._refresh()

    def show_error(self, message: str) -> None:
        messagebox.showerror(_TITLE, message, parent=self)

    def show_info(self, message: str) -> None:
        messagebox.showinfo(_TITLE, message, parent=self)

    def _build_menu(self) -> None:
        menubar = tk.Menu(self)
        profile_menu = tk.Menu(menubar, tearoff=False)
        profile_menu.add_command(label="New", command=self._new_profile)
        profile_menu.add_command(label="Open...", command=self._open_profile)
        profile_menu.add_command(label="Save", command=self._save_profile)
        profile_menu.add_command(label="Save as...", command=self._save_profile_as)
        profile_menu.add_separator()
        profile_menu.add_command(label="Quit", command=self._on_close)
        menubar.add_cascade(label="Profile", menu=profile_menu)

        view_menu = tk.Menu(menubar, tearoff=False)
        view_menu.add_command(label="Light", command=lambda: self._set_theme(Theme.LIGHT))
        view_menu.add_command(label="Dark", command=lambda: self._set_theme(Theme.DARK))
        menubar.add_cascade(label="View", menu=view_menu)
        self.configure(menu=menubar)

    def _build_notebook(self) -> None:
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=8, pady=8)

        self._banner_view = BannerView(
            notebook,
            on_submit=self._add_banner,
            on_error=self.show_error,
            currencies=lambda: self._profile.currencies,
            on_random_name=self._random_item_name,
        )
        self._currency_view = CurrencyView(
            notebook,
            on_currency=self._add_currency,
            on_package=self._add_package,
            on_rate=self._add_rate,
            on_error=self.show_error,
        )
        self._budget_view = BudgetView(
            notebook, on_calculate=self._calculate, on_error=self.show_error
        )
        self._results_view = ResultView(notebook, self._palette)

        notebook.add(self._banner_view, text="Banner")
        notebook.add(self._currency_view, text="Currency")
        notebook.add(self._budget_view, text="Planning")
        notebook.add(self._results_view, text="Results")

    def _palette(self) -> Palette:
        return palette_for(self._theme)

    def _random_item_name(self) -> str:
        taken = {item.name for banner in self._profile.banners for item in banner.items}
        return self._name_generator.generate(taken)

    def _add_banner(self, banner: Banner) -> None:
        remain = [other for other in self._profile.banners if other.name != banner.name]
        self._profile.banners = (*remain, banner)
        self._mark_dirty()
        self._refresh()
        self.show_info(f"Banner {banner.name!r} saved to the profile")

    def _add_currency(self, currency: Currency, balance: Decimal) -> None:
        remain = [other for other in self._profile.currencies if other.code != currency.code]
        self._profile.currencies = (*remain, currency)
        self._profile.balances[currency.code] = Money(balance, currency)
        if not self._profile.display_currency_code and currency.kind is CurrencyKind.REAL:
            self._profile.display_currency_code = currency.code
        self._mark_dirty()
        self._refresh()

    def _add_package(self, package: TopUpPackage) -> None:
        self._profile.topup_packages = (*self._profile.topup_packages, package)
        self._mark_dirty()
        self._refresh()

    def _add_rate(self, exchange_rate: ExchangeRate) -> None:
        pair = (exchange_rate.source_code, exchange_rate.target_code)
        remain = [
            other
            for other in self._profile.exchange_rates
            if (other.source_code, other.target_code) != pair
        ]
        self._profile.exchange_rates = (*remain, exchange_rate)
        self._sync_provider()
        self._mark_dirty()
        self._refresh()

    def _calculate(
        self, banner_name: str, tier_name: str, state: PityState, deadline: date
    ) -> None:
        self._profile.incomes = tuple(self._budget_view.get_incomes())
        try:
            report = self._service.plan(self._profile, banner_name, tier_name, state)
            projection = self._service.plan_by_deadline(
                self._profile, banner_name, tier_name, state, date.today(), deadline
            )
            markers: dict[str, int | None] = {
                "50%": report.pulls_for_50,
                "90%": report.pulls_for_90,
                "99%": report.pulls_for_99,
            }
            curve = self._service.success_curve(
                self._profile, banner_name, tier_name, state, _curve_horizon(markers)
            )
        except (ValueError, KeyError) as exc:
            self.show_error(describe_error(exc))
            return
        self._last_report = report
        self._last_curve = curve
        self._last_markers = markers
        self._results_view.show(report)
        self._results_view.show_curve(curve, markers)
        self._budget_view.show(
            projection.pulls,
            projection.success_probability,
            projection.required_daily_income,
        )

    def _sync_provider(self) -> None:
        self._provider.set_rates(self._profile.exchange_rates)

    def _refresh(self) -> None:
        self._banner_view.refresh_currencies()
        self._banner_view.show_banners([banner.name for banner in self._profile.banners])
        self._currency_view.show(self._profile)
        self._budget_view.set_banners(self._profile.banners)
        self._budget_view.set_currency_codes(
            [currency.code for currency in self._profile.currencies]
        )

    def _mark_dirty(self) -> None:
        self._dirty = True

    def _new_profile(self) -> None:
        if not self._confirm_discard():
            return
        self._profile = GameProfile(name=_UNSAVED_NAME)
        self._last_report = None
        self._last_curve = []
        self._last_markers = {}
        self._results_view.clear()
        self._sync_provider()
        self._dirty = False
        self._refresh()

    def _open_profile(self) -> None:
        if not self._confirm_discard():
            return
        name = simpledialog.askstring("Open profile", "Profile name:", parent=self)
        if not name:
            return
        try:
            profile = self._repository.load(name.strip())
        except StorageError as exc:
            self.show_error(str(exc))
            return
        self._profile = profile
        self._last_report = None
        self._last_curve = []
        self._last_markers = {}
        self._results_view.clear()
        self._sync_provider()
        self._dirty = False
        self._refresh()

    def _save_profile(self) -> None:
        if self._profile.name in ("", _UNSAVED_NAME):
            self._save_profile_as()
            return
        self._write_profile()

    def _save_profile_as(self) -> None:
        name = simpledialog.askstring(
            "Save profile", "Profile name:", parent=self, initialvalue=self._profile.name
        )
        if not name:
            return
        self._profile.name = name.strip()
        self._write_profile()

    def _write_profile(self) -> None:
        try:
            self._repository.save(self._profile)
        except (StorageError, ValueError) as exc:
            self.show_error(describe_error(exc))
            return
        self._dirty = False
        self._refresh()
        self.show_info(f"Profile {self._profile.name!r} saved")

    def _confirm_discard(self) -> bool:
        if not self._dirty:
            return True
        return messagebox.askyesno(_TITLE, "There are unsaved changes. Continue?", parent=self)

    def _set_theme(self, theme: Theme) -> None:
        self._theme = theme
        apply_theme(self, theme)
        if self._last_report is not None:
            self._results_view.show(self._last_report)
        if self._last_curve:
            self._results_view.show_curve(self._last_curve, self._last_markers)

    def _on_close(self) -> None:
        if self._confirm_discard():
            self.destroy()
