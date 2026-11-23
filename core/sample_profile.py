"""A filled-in profile so a new player can see what a complete setup looks like."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from core.exchange import ExchangeRate
from core.models.banner import Banner, RateTier
from core.models.currency import Currency, CurrencyKind, Money
from core.models.item import Item
from core.models.pity import FeaturedGuarantee, PityConfig, PullRule
from core.models.profile import GameProfile
from core.models.topup import TopUpPackage

SAMPLE_PROFILE_NAME = "example"

DIAMOND = Currency(code="DIAMOND", name="Diamond", kind=CurrencyKind.GAME)
TICKET = Currency(code="TICKET", name="Featured ticket", kind=CurrencyKind.GAME)
USD = Currency(code="USD", name="US dollar", kind=CurrencyKind.REAL, decimals=2)

_DIAMOND_PER_PULL = Decimal(160)


def build_sample_profile(today: date) -> GameProfile:
    """Two banners, three currencies, three top-up packages and one manual rate."""
    return GameProfile(
        name=SAMPLE_PROFILE_NAME,
        currencies=(DIAMOND, TICKET, USD),
        balances={
            "DIAMOND": Money(Decimal(4800), DIAMOND),
            "TICKET": Money(Decimal(12), TICKET),
        },
        banners=(_festival_banner(today), _ticket_banner(today)),
        topup_packages=_packages(),
        exchange_rates=(
            ExchangeRate(source_code="TICKET", target_code="DIAMOND", rate=_DIAMOND_PER_PULL),
        ),
        display_currency_code="USD",
    )


def _festival_banner(today: date) -> Banner:
    return Banner(
        name="Starlight Festival",
        tiers=(
            RateTier(
                name="5-star",
                rule=PullRule(
                    base_rate=0.006,
                    pity=PityConfig(hard_pity=90, soft_pity_start=74, soft_pity_step=0.06),
                    guarantee=FeaturedGuarantee(win_chance=0.5),
                ),
            ),
            RateTier(name="4-star", rule=PullRule(base_rate=0.051)),
        ),
        items=(
            Item(name="Astral Blade", tier_name="5-star", is_featured=True),
            Item(name="Moonlit Catalyst", tier_name="5-star"),
            Item(name="Starlight Bow", tier_name="4-star"),
        ),
        cost_per_pull=Money(_DIAMOND_PER_PULL, DIAMOND),
        ends_on=today + timedelta(days=21),
    )


def _ticket_banner(today: date) -> Banner:
    return Banner(
        name="Ticket Showcase",
        tiers=(RateTier(name="5-star", rule=PullRule(base_rate=0.02)),),
        items=(Item(name="Sunforged Lance", tier_name="5-star", is_featured=True),),
        cost_per_pull=Money(Decimal(1), TICKET),
        ends_on=today + timedelta(days=7),
    )


def _packages() -> tuple[TopUpPackage, ...]:
    return (
        TopUpPackage(
            price=Money(Decimal("19.99"), USD),
            grants=DIAMOND,
            base_amount=1090,
            bonus_amount=110,
        ),
        TopUpPackage(
            price=Money(Decimal("49.99"), USD),
            grants=DIAMOND,
            base_amount=3280,
            bonus_amount=600,
        ),
        TopUpPackage(
            price=Money(Decimal("99.99"), USD),
            grants=DIAMOND,
            base_amount=6480,
            bonus_amount=1600,
            first_purchase_bonus=6480,
        ),
    )
