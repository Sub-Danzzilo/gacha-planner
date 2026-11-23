from __future__ import annotations

from dataclasses import dataclass

from core.models.currency import Currency, CurrencyKind, Money


@dataclass(frozen=True, slots=True)
class TopUpPackage:
    """A top-up bundle: real money exchanged for game currency, with optional bonuses."""

    price: Money
    grants: Currency
    base_amount: int
    bonus_amount: int = 0
    first_purchase_bonus: int = 0

    def __post_init__(self) -> None:
        if self.price.currency.kind is not CurrencyKind.REAL:
            raise ValueError("Top-up price must be real money")
        if self.price.amount <= 0:
            raise ValueError("Top-up price must be greater than 0")
        if self.grants.kind is not CurrencyKind.GAME:
            raise ValueError("A top-up package must grant game currency")
        if self.base_amount <= 0:
            raise ValueError("Top-up base amount must be greater than 0")
        if self.bonus_amount < 0 or self.first_purchase_bonus < 0:
            raise ValueError("Top-up bonuses cannot be negative")

    @property
    def total_amount(self) -> int:
        return self.base_amount + self.bonus_amount

    @property
    def first_purchase_total(self) -> int:
        return self.total_amount + self.first_purchase_bonus
