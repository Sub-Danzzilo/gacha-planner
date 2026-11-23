from __future__ import annotations

import abc
from collections.abc import Iterable
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from core.errors import MissingExchangeRateError
from core.models.currency import Currency, CurrencyMismatchError, Money


@dataclass(frozen=True, slots=True)
class ExchangeRate:
    """One manual rate: ``rate`` units of ``target_code`` per one unit of ``source_code``."""

    source_code: str
    target_code: str
    rate: Decimal

    def __post_init__(self) -> None:
        for code in (self.source_code, self.target_code):
            if not code or code != code.upper():
                raise ValueError(f"Currency code must be uppercase and non-empty: {code!r}")
        if not isinstance(self.rate, Decimal):
            raise TypeError("Rate must be Decimal, not float or int")
        if self.source_code == self.target_code:
            raise ValueError("A rate for identical currencies is not needed")
        if self.rate <= 0:
            raise ValueError("Rate must be greater than 0")


class ExchangeRateProvider(abc.ABC):
    """Extension point for rate sources. This project only uses manual rates."""

    @abc.abstractmethod
    def rate(self, source_code: str, target_code: str) -> Decimal:
        """Units of ``target_code`` per one unit of ``source_code``."""


class ManualRateProvider(ExchangeRateProvider):
    """Rates entered by the player. Their inverse is available automatically."""

    def __init__(self, rates: Iterable[ExchangeRate] = ()) -> None:
        self._rates: dict[tuple[str, str], Decimal] = {}
        for exchange_rate in rates:
            self.set_rate(exchange_rate.source_code, exchange_rate.target_code, exchange_rate.rate)

    def set_rate(self, source_code: str, target_code: str, rate: Decimal) -> None:
        if not isinstance(rate, Decimal):
            raise TypeError("Rate must be Decimal, not float or int")
        if rate <= 0:
            raise ValueError("Rate must be greater than 0")
        self._rates[(source_code, target_code)] = rate

    def set_rates(self, rates: Iterable[ExchangeRate]) -> None:
        """Replace every rate, for example after another profile is loaded."""
        self._rates.clear()
        for exchange_rate in rates:
            self.set_rate(exchange_rate.source_code, exchange_rate.target_code, exchange_rate.rate)

    def rates(self) -> dict[tuple[str, str], Decimal]:
        return dict(self._rates)

    def rate(self, source_code: str, target_code: str) -> Decimal:
        if source_code == target_code:
            return Decimal(1)
        explicit = self._rates.get((source_code, target_code))
        if explicit is not None:
            return explicit
        inverse = self._rates.get((target_code, source_code))
        if inverse is not None:
            return Decimal(1) / inverse
        raise MissingExchangeRateError(f"No manual rate for {source_code} -> {target_code}")


class CurrencyConverter:
    """Converts values between currencies using manual rates.

    Conversion is only allowed between two currencies of the same kind (game to game, or real to
    real); bridging the two kinds is the job of top-up packages, not of rates.
    """

    def __init__(self, provider: ExchangeRateProvider) -> None:
        self._provider = provider

    def convert(self, money: Money, target: Currency) -> Money:
        """Value rounded to ``target`` decimals for display."""
        exact = self.exact(money, target)
        return Money(
            exact.amount.quantize(Decimal(1).scaleb(-target.decimals), rounding=ROUND_HALF_UP),
            target,
        )

    def exact(self, money: Money, target: Currency) -> Money:
        """Full-precision value, for further calculation."""
        if money.currency.kind is not target.kind:
            raise CurrencyMismatchError(
                f"Cannot convert {money.currency.code} ({money.currency.kind.value}) to "
                f"{target.code} ({target.kind.value}) through an exchange rate"
            )
        return Money(money.amount * self._provider.rate(money.currency.code, target.code), target)
