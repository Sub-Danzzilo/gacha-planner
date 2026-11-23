from __future__ import annotations

import enum
from dataclasses import dataclass
from decimal import Decimal


class CurrencyKind(enum.Enum):
    GAME = "game"
    REAL = "real"


class CurrencyMismatchError(ValueError):
    """An operation between two values in different currencies."""


@dataclass(frozen=True, slots=True)
class Currency:
    """A game currency (DIAMOND) or a real currency (IDR, USD)."""

    code: str
    name: str
    kind: CurrencyKind
    decimals: int = 0

    def __post_init__(self) -> None:
        if not self.code or self.code != self.code.upper():
            raise ValueError(f"Currency code must be uppercase and non-empty: {self.code!r}")
        if not self.name.strip():
            raise ValueError("Currency name cannot be empty")
        if self.decimals < 0:
            raise ValueError("Decimals cannot be negative")


@dataclass(frozen=True, slots=True)
class Money:
    """An amount in a single currency.

    Negative values are only valid as a difference, not as a balance. Ordering comparisons
    (``<``, ``<=``, ``>``, ``>=``) between two different currencies raise
    ``CurrencyMismatchError``.
    """

    amount: Decimal
    currency: Currency

    def __post_init__(self) -> None:
        if not isinstance(self.amount, Decimal):
            raise TypeError("Use Decimal, not float or int, for money amounts")

    def __add__(self, other: Money) -> Money:
        if not isinstance(other, Money):
            return NotImplemented
        self._require_same_currency(other)
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: Money) -> Money:
        if not isinstance(other, Money):
            return NotImplemented
        self._require_same_currency(other)
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, factor: int | Decimal) -> Money:
        return Money(self.amount * self._strict_decimal(factor), self.currency)

    def __rmul__(self, factor: int | Decimal) -> Money:
        return self * factor

    def __neg__(self) -> Money:
        return Money(-self.amount, self.currency)

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        self._require_same_currency(other)
        return self.amount < other.amount

    def __le__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        self._require_same_currency(other)
        return self.amount <= other.amount

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        self._require_same_currency(other)
        return self.amount > other.amount

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        self._require_same_currency(other)
        return self.amount >= other.amount

    def _same_currency(self, other: Money) -> bool:
        return self.currency.code == other.currency.code

    def _require_same_currency(self, other: Money) -> None:
        if not self._same_currency(other):
            raise CurrencyMismatchError(
                f"{self.currency.code} cannot be combined directly with {other.currency.code}"
            )

    @staticmethod
    def _strict_decimal(factor: int | Decimal) -> Decimal:
        if isinstance(factor, float):
            raise TypeError("Use Decimal, not float, when multiplying money")
        return Decimal(factor)
