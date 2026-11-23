from datetime import date
from decimal import Decimal

import pytest

from core.budget import IncomePeriod, IncomeSource
from core.exchange import ExchangeRate
from core.models.banner import Banner, RateTier
from core.models.currency import Currency, CurrencyKind, Money
from core.models.pity import PullRule
from core.models.profile import GameProfile
from core.models.topup import TopUpPackage

DIAMOND = Currency(code="DIAMOND", name="Diamond", kind=CurrencyKind.GAME)
USD = Currency(code="USD", name="Dolar", kind=CurrencyKind.REAL, decimals=2)


def _banner() -> Banner:
    return Banner(
        name="Test banner",
        tiers=(RateTier(name="5-star", rule=PullRule(base_rate=0.6)),),
        items=(),
        cost_per_pull=Money(Decimal("160"), DIAMOND),
    )


def _complete_profile() -> GameProfile:
    return GameProfile(
        name="Genshin",
        currencies=(DIAMOND, USD),
        balances={"DIAMOND": Money(Decimal("16000"), DIAMOND)},
        banners=(_banner(),),
        topup_packages=(
            TopUpPackage(price=Money(Decimal("5"), USD), grants=DIAMOND, base_amount=300),
        ),
        exchange_rates=(
            ExchangeRate(source_code="USD", target_code="DIAMOND", rate=Decimal("60")),
        ),
        incomes=(
            IncomeSource(
                name="Event",
                currency_code="DIAMOND",
                amount=100,
                period=IncomePeriod.DAILY,
                first_credit=date(2026, 1, 1),
            ),
        ),
        display_currency_code="USD",
    )


def test_profile_accepts_consistent_references() -> None:
    profile = _complete_profile()
    assert profile.currency("USD").code == "USD"
    assert profile.banner("Test banner").name == "Test banner"


def test_profile_rejects_balance_with_unknown_currency() -> None:
    with pytest.raises(ValueError):
        GameProfile(
            name="Broken",
            currencies=(DIAMOND,),
            balances={"GOLD": Money(Decimal("1"), DIAMOND)},
        )


def test_profile_rejects_unknown_display_currency() -> None:
    with pytest.raises(ValueError):
        GameProfile(name="Broken", currencies=(DIAMOND,), display_currency_code="USD")


def test_profile_rejects_duplicate_currency_codes() -> None:
    with pytest.raises(ValueError):
        GameProfile(name="Broken", currencies=(DIAMOND, DIAMOND))


def test_profile_rejects_blank_name() -> None:
    with pytest.raises(ValueError):
        GameProfile(name="  ")


def test_profile_lookup_errors() -> None:
    profile = _complete_profile()
    with pytest.raises(ValueError):
        profile.currency("EUR")
    with pytest.raises(KeyError):
        profile.banner("Not There")
