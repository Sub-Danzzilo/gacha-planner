from datetime import date
from decimal import Decimal

from core.exchange import CurrencyConverter, ManualRateProvider
from core.models.pity import PityState
from core.models.profile import GameProfile
from core.sample_profile import build_sample_profile
from services.planner_service import PlannerService

TODAY = date(2026, 1, 1)


def _service(profile: GameProfile) -> PlannerService:
    return PlannerService(CurrencyConverter(ManualRateProvider(profile.exchange_rates)))


def test_sample_profile_has_data_for_every_screen() -> None:
    profile = build_sample_profile(TODAY)
    assert len(profile.currencies) == 3
    assert len(profile.banners) == 2
    assert profile.topup_packages
    assert profile.exchange_rates
    assert profile.display_currency_code == "USD"


def test_sample_profile_plans_every_tier() -> None:
    profile = build_sample_profile(TODAY)
    service = _service(profile)
    for banner in profile.banners:
        for tier in banner.tiers:
            report = service.plan(profile, banner.name, tier.name, PityState())
            assert 0.0 <= report.success_probability <= 1.0
            assert report.total_pulls >= 0


def test_sample_profile_prices_the_ninety_percent_target() -> None:
    profile = build_sample_profile(TODAY)
    report = _service(profile).plan(profile, "Starlight Festival", "5-star", PityState())
    assert report.pulls_for_90 is not None
    assert report.real_money_cost is not None
    assert report.real_money_cost.amount > Decimal(0)


def test_sample_profile_supports_the_deadline_projection() -> None:
    profile = build_sample_profile(TODAY)
    banner = profile.banner("Starlight Festival")
    assert banner.ends_on is not None
    projection = _service(profile).plan_by_deadline(
        profile, banner.name, "5-star", PityState(), TODAY, banner.ends_on
    )
    assert projection.pulls == 42
    assert projection.success_probability < 1.0
