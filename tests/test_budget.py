from datetime import date
from decimal import Decimal

import pytest

from core.budget import BudgetHorizon, BudgetPlanner, IncomePeriod, IncomeSource
from core.exchange import CurrencyConverter, ExchangeRate, ManualRateProvider
from core.models.banner import Banner, RateTier
from core.models.currency import Currency, CurrencyKind, Money
from core.models.pity import PullRule

DIAMOND = Currency(code="DIAMOND", name="Diamond", kind=CurrencyKind.GAME)
GEM = Currency(code="GEM", name="Gem", kind=CurrencyKind.GAME)


def _planner(rates: tuple[ExchangeRate, ...] = ()) -> BudgetPlanner:
    banner = Banner(
        name="Test",
        tiers=(RateTier(name="5-star", rule=PullRule(base_rate=0.6)),),
        items=(),
        cost_per_pull=Money(Decimal("160"), DIAMOND),
    )
    currencies = {currency.code: currency for currency in (DIAMOND, GEM)}
    return BudgetPlanner(banner, CurrencyConverter(ManualRateProvider(rates)), currencies)


def _source(period: IncomePeriod, amount: int, first: date) -> IncomeSource:
    return IncomeSource(
        name="Source", currency_code="DIAMOND", amount=amount, period=period, first_credit=first
    )


def test_daily_credits_skip_today_and_include_deadline() -> None:
    source = _source(IncomePeriod.DAILY, 10, date(2026, 1, 1))
    assert _planner().credits_between(source, date(2026, 1, 1), date(2026, 1, 11)) == 100


def test_deadline_equal_to_today_gives_zero() -> None:
    source = _source(IncomePeriod.DAILY, 10, date(2026, 1, 1))
    assert _planner().credits_between(source, date(2026, 1, 1), date(2026, 1, 1)) == 0


def test_weekly_credits_start_from_first_credit() -> None:
    source = _source(IncomePeriod.WEEKLY, 50, date(2026, 1, 5))
    assert _planner().credits_between(source, date(2026, 1, 1), date(2026, 1, 20)) == 150


def test_weekly_credits_skip_past_dates() -> None:
    source = _source(IncomePeriod.WEEKLY, 50, date(2026, 1, 5))
    assert _planner().credits_between(source, date(2026, 1, 10), date(2026, 1, 20)) == 100


def test_weekly_credit_after_deadline_gives_zero() -> None:
    source = _source(IncomePeriod.WEEKLY, 50, date(2026, 2, 1))
    assert _planner().credits_between(source, date(2026, 1, 1), date(2026, 1, 20)) == 0


def test_monthly_credit_uses_last_day_of_short_month() -> None:
    source = _source(IncomePeriod.MONTHLY, 20, date(2026, 1, 31))
    assert _planner().credits_between(source, date(2026, 1, 1), date(2026, 3, 31)) == 60


def test_monthly_credit_excludes_today() -> None:
    source = _source(IncomePeriod.MONTHLY, 20, date(2026, 1, 31))
    assert _planner().credits_between(source, date(2026, 1, 31), date(2026, 2, 28)) == 20


def test_projected_pulls_adds_balance_and_income() -> None:
    planner = _planner()
    balances = {"DIAMOND": Money(Decimal("4800"), DIAMOND)}
    incomes = [_source(IncomePeriod.DAILY, 100, date(2026, 1, 1))]
    horizon = BudgetHorizon(today=date(2026, 1, 1), deadline=date(2026, 1, 11))
    assert planner.projected_pulls(balances, incomes, horizon) == 36


def test_required_daily_income_hand_case() -> None:
    planner = _planner()
    balances = {"DIAMOND": Money(Decimal("4800"), DIAMOND)}
    incomes = [_source(IncomePeriod.DAILY, 100, date(2026, 1, 1))]
    horizon = BudgetHorizon(today=date(2026, 1, 1), deadline=date(2026, 1, 11))
    assert planner.required_daily_income(100, balances, incomes, horizon) == Decimal("1020")


def test_required_daily_income_is_zero_when_already_enough() -> None:
    planner = _planner()
    balances = {"DIAMOND": Money(Decimal("16000"), DIAMOND)}
    horizon = BudgetHorizon(today=date(2026, 1, 1), deadline=date(2026, 1, 11))
    assert planner.required_daily_income(50, balances, [], horizon) == Decimal(0)


def test_required_daily_income_rejects_past_deadline() -> None:
    planner = _planner()
    horizon = BudgetHorizon(today=date(2026, 1, 11), deadline=date(2026, 1, 1))
    with pytest.raises(ValueError):
        planner.required_daily_income(10, {}, [], horizon)


def test_income_in_other_game_currency_is_converted() -> None:
    planner = _planner((ExchangeRate("GEM", "DIAMOND", Decimal("0.5")),))
    incomes = [
        IncomeSource(
            name="Daily gems",
            currency_code="GEM",
            amount=100,
            period=IncomePeriod.DAILY,
            first_credit=date(2026, 1, 1),
        )
    ]
    horizon = BudgetHorizon(today=date(2026, 1, 1), deadline=date(2026, 1, 11))
    assert planner.projected_pulls({}, incomes, horizon) == 3
