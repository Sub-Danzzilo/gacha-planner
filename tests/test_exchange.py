from decimal import Decimal
from typing import cast

import pytest

from core.errors import MissingExchangeRateError
from core.exchange import CurrencyConverter, ExchangeRate, ManualRateProvider
from core.models.currency import Currency, CurrencyKind, CurrencyMismatchError, Money

USD = Currency(code="USD", name="Dolar", kind=CurrencyKind.REAL, decimals=2)
IDR = Currency(code="IDR", name="Rupiah", kind=CurrencyKind.REAL)
DIAMOND = Currency(code="DIAMOND", name="Diamond", kind=CurrencyKind.GAME)
GEM = Currency(code="GEM", name="Gem", kind=CurrencyKind.GAME)


def test_explicit_rate_and_implicit_inverse() -> None:
    provider = ManualRateProvider([ExchangeRate("USD", "IDR", Decimal("16000"))])
    assert provider.rate("USD", "IDR") == Decimal("16000")
    assert provider.rate("IDR", "USD") == Decimal(1) / Decimal("16000")


def test_identity_rate_is_one() -> None:
    provider = ManualRateProvider()
    assert provider.rate("USD", "USD") == Decimal(1)


def test_missing_pair_raises() -> None:
    provider = ManualRateProvider()
    with pytest.raises(MissingExchangeRateError):
        provider.rate("USD", "IDR")


def test_set_rates_replaces_existing_book() -> None:
    provider = ManualRateProvider([ExchangeRate("USD", "IDR", Decimal("16000"))])
    provider.set_rates([ExchangeRate("USD", "IDR", Decimal("17000"))])
    assert provider.rate("USD", "IDR") == Decimal("17000")
    assert provider.rates() == {("USD", "IDR"): Decimal("17000")}


def test_convert_rounds_to_currency_decimals() -> None:
    provider = ManualRateProvider([ExchangeRate("USD", "IDR", Decimal("16000"))])
    converter = CurrencyConverter(provider)
    converted = converter.convert(Money(Decimal("10"), USD), IDR)
    assert converted == Money(Decimal("160000"), IDR)


def test_round_half_up_for_display_values() -> None:
    provider = ManualRateProvider([ExchangeRate("IDR", "USD", Decimal("1.005"))])
    converter = CurrencyConverter(provider)
    money = Money(Decimal("1"), IDR)
    assert converter.convert(money, USD).amount == Decimal("1.01")
    assert converter.exact(money, USD).amount == Decimal("1.005")


def test_game_currency_conversion_uses_manual_ratio() -> None:
    provider = ManualRateProvider([ExchangeRate("DIAMOND", "GEM", Decimal("2"))])
    converter = CurrencyConverter(provider)
    assert converter.convert(Money(Decimal("10"), DIAMOND), GEM) == Money(Decimal("20"), GEM)


def test_mixing_real_and_game_raises() -> None:
    converter = CurrencyConverter(
        ManualRateProvider([ExchangeRate("USD", "DIAMOND", Decimal("1"))])
    )
    with pytest.raises(CurrencyMismatchError):
        converter.convert(Money(Decimal("1"), USD), DIAMOND)


def test_exchange_rate_rejects_float() -> None:
    with pytest.raises(TypeError):
        ExchangeRate("USD", "IDR", cast(Decimal, 16000.0))


def test_set_rate_rejects_non_positive_rate() -> None:
    provider = ManualRateProvider()
    with pytest.raises(ValueError):
        provider.set_rate("USD", "IDR", Decimal("0"))
    with pytest.raises(ValueError):
        provider.set_rate("USD", "IDR", Decimal("-1"))


def test_identity_conversion_keeps_amount() -> None:
    converter = CurrencyConverter(ManualRateProvider())
    assert converter.convert(Money(Decimal("3.456"), USD), USD) == Money(Decimal("3.46"), USD)
