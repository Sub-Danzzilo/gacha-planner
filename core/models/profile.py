from __future__ import annotations

from dataclasses import dataclass, field

from core.budget import IncomeSource
from core.exchange import ExchangeRate
from core.models.banner import Banner
from core.models.currency import Currency, Money
from core.models.topup import TopUpPackage


@dataclass
class GameProfile:
    """One profile equals one game owned by the player; the unit stored in and loaded from JSON.

    Not frozen because the player edits the profile step by step.
    """

    name: str
    currencies: tuple[Currency, ...] = ()
    balances: dict[str, Money] = field(default_factory=dict)
    banners: tuple[Banner, ...] = ()
    topup_packages: tuple[TopUpPackage, ...] = ()
    exchange_rates: tuple[ExchangeRate, ...] = ()
    incomes: tuple[IncomeSource, ...] = ()
    display_currency_code: str = ""

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Profile name cannot be empty")
        self._validate_references()

    def currency(self, code: str) -> Currency:
        for currency in self.currencies:
            if currency.code == code:
                return currency
        raise ValueError(f"Currency {code!r} is not in profile {self.name!r}")

    def banner(self, name: str) -> Banner:
        for banner in self.banners:
            if banner.name == name:
                return banner
        raise KeyError(f"Banner {name!r} is not in profile {self.name!r}")

    def _validate_references(self) -> None:
        known = {currency.code for currency in self.currencies}
        if len(known) != len(self.currencies):
            raise ValueError("Currency codes must be unique within a profile")

        referenced: list[tuple[str, str]] = []
        referenced.extend((f"balance {code}", code) for code in self.balances)
        referenced.extend(
            (f"top-up package {index}", package.price.currency.code)
            for index, package in enumerate(self.topup_packages)
        )
        referenced.extend(
            (f"top-up package {index}", package.grants.code)
            for index, package in enumerate(self.topup_packages)
        )
        referenced.extend(
            (f"exchange rate {index}", rate.source_code)
            for index, rate in enumerate(self.exchange_rates)
        )
        referenced.extend(
            (f"exchange rate {index}", rate.target_code)
            for index, rate in enumerate(self.exchange_rates)
        )
        referenced.extend(
            (f"income {source.name}", source.currency_code) for source in self.incomes
        )
        referenced.extend(
            (f"banner {banner.name}", banner.cost_per_pull.currency.code) for banner in self.banners
        )
        if self.display_currency_code:
            referenced.append(("display currency", self.display_currency_code))

        for field_name, code in referenced:
            if code not in known:
                raise ValueError(f"{field_name} refers to an unknown currency: {code!r}")
