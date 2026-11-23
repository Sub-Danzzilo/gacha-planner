from datetime import date
from decimal import Decimal

import pytest

from core.budget import IncomePeriod, IncomeSource
from core.calculators.pity_dp import PityCalculator
from core.calculators.simple import SimpleCalculator
from core.exchange import CurrencyConverter, ManualRateProvider
from core.models.banner import Banner, RateTier
from core.models.currency import Currency, CurrencyKind, Money
from core.models.pity import PityConfig, PityState, PullRule
from core.models.profile import GameProfile
from core.models.topup import TopUpPackage
from services.planner_service import PlannerService

DIAMOND = Currency(code="DIAMOND", name="Diamond", kind=CurrencyKind.GAME)
USD = Currency(code="USD", name="Dolar", kind=CurrencyKind.REAL, decimals=2)
INITIAL = PityState()


def _banner(pity: PityConfig | None = None) -> Banner:
    return Banner(
        name="Test banner",
        tiers=(RateTier(name="5-star", rule=PullRule(base_rate=0.5, pity=pity)),),
        items=(),
        cost_per_pull=Money(Decimal("160"), DIAMOND),
    )


def _profile(
    balance: str = "16000",
    packages: tuple[TopUpPackage, ...] = (),
    incomes: tuple[IncomeSource, ...] = (),
    pity: PityConfig | None = None,
) -> GameProfile:
    return GameProfile(
        name="Test",
        currencies=(DIAMOND, USD),
        balances={"DIAMOND": Money(Decimal(balance), DIAMOND)},
        banners=(_banner(pity),),
        topup_packages=packages,
        incomes=incomes,
        display_currency_code="USD",
    )


def _service() -> PlannerService:
    return PlannerService(CurrencyConverter(ManualRateProvider()))


def test_plan_with_current_balance() -> None:
    report = _service().plan(_profile(), "Test banner", "5-star", INITIAL)
    assert report.total_pulls == 100
    assert report.success_probability == pytest.approx(1.0)
    assert report.pulls_for_50 == 1
    assert report.pulls_for_90 == 4
    assert report.pulls_for_99 == 7
    assert report.expected_pulls == pytest.approx(2.0)


def test_calculator_choice_depends_on_pity() -> None:
    service = _service()
    assert isinstance(service.calculator_for(PullRule(base_rate=0.5)), SimpleCalculator)
    assert isinstance(
        service.calculator_for(PullRule(base_rate=0.5, pity=PityConfig(hard_pity=90))),
        PityCalculator,
    )


def test_real_money_cost_uses_cheapest_topup_for_ninety_percent() -> None:
    package = TopUpPackage(price=Money(Decimal("5"), USD), grants=DIAMOND, base_amount=60)
    report = _service().plan(
        _profile(balance="0", packages=(package,)), "Test banner", "5-star", INITIAL
    )
    assert report.pulls_for_90 == 4
    assert report.real_money_cost == Money(Decimal("55.00"), USD)


def test_real_money_cost_is_none_without_packages() -> None:
    report = _service().plan(_profile(balance="0"), "Test banner", "5-star", INITIAL)
    assert report.real_money_cost is None


def test_plan_by_deadline_projects_pulls_and_daily_income() -> None:
    income = IncomeSource(
        name="Daily",
        currency_code="DIAMOND",
        amount=100,
        period=IncomePeriod.DAILY,
        first_credit=date(2026, 1, 1),
    )
    projection = _service().plan_by_deadline(
        _profile(balance="0", incomes=(income,)),
        "Test banner",
        "5-star",
        INITIAL,
        today=date(2026, 1, 1),
        deadline=date(2026, 1, 11),
    )
    assert projection.pulls == 6
    assert projection.target_pulls == 4
    assert projection.success_probability == pytest.approx(1.0 - 0.5**6)
    assert projection.required_daily_income == Money(Decimal("0"), DIAMOND)


def test_plan_by_deadline_reports_required_daily_income() -> None:
    projection = _service().plan_by_deadline(
        _profile(balance="0"),
        "Test banner",
        "5-star",
        INITIAL,
        today=date(2026, 1, 1),
        deadline=date(2026, 1, 11),
    )
    assert projection.pulls == 0
    assert projection.required_daily_income == Money(Decimal("64"), DIAMOND)


def test_plan_by_deadline_rejects_past_deadline() -> None:
    with pytest.raises(ValueError):
        _service().plan_by_deadline(
            _profile(),
            "Test banner",
            "5-star",
            INITIAL,
            today=date(2026, 1, 11),
            deadline=date(2026, 1, 11),
        )


def test_unknown_banner_raises() -> None:
    with pytest.raises(KeyError):
        _service().plan(_profile(), "Other banner", "5-star", INITIAL)
