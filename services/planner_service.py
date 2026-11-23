from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import ROUND_CEILING, Decimal

from core.budget import BudgetHorizon, BudgetPlanner
from core.calculators.base import PullCalculator
from core.calculators.pity_dp import PityCalculator
from core.calculators.simple import SimpleCalculator
from core.exchange import CurrencyConverter
from core.models.banner import Banner
from core.models.currency import Money
from core.models.pity import PityState, PullRule
from core.models.profile import GameProfile
from core.topup_optimizer import TopUpOptimizer

_TARGET_CONFIDENCE = 0.9


@dataclass(frozen=True, slots=True)
class PlanReport:
    total_pulls: int
    success_probability: float
    pulls_for_50: int | None
    pulls_for_90: int | None
    pulls_for_99: int | None
    expected_pulls: float
    real_money_cost: Money | None = None


@dataclass(frozen=True, slots=True)
class DeadlineProjection:
    pulls: int
    success_probability: float
    target_pulls: int
    required_daily_income: Money


class PlannerService:
    """The single entry point from the UI into core logic."""

    def __init__(self, converter: CurrencyConverter) -> None:
        self._converter = converter

    def calculator_for(self, rule: PullRule) -> PullCalculator:
        """Pick a calculator: the closed form only when there is no pity and no guarantee."""
        if rule.pity is None and rule.guarantee is None:
            return SimpleCalculator(rule.base_rate)
        return PityCalculator(rule)

    def plan(
        self,
        profile: GameProfile,
        banner_name: str,
        tier_name: str,
        state: PityState,
    ) -> PlanReport:
        banner = profile.banner(banner_name)
        calculator = self.calculator_for(banner.tier(tier_name).rule)
        balance = self._balance(profile, banner)
        pulls = banner.pulls_affordable(balance)
        pulls_for_90 = calculator.pulls_for_confidence(_TARGET_CONFIDENCE, state)
        return PlanReport(
            total_pulls=pulls,
            success_probability=calculator.success_probability(pulls, state),
            pulls_for_50=calculator.pulls_for_confidence(0.5, state),
            pulls_for_90=pulls_for_90,
            pulls_for_99=calculator.pulls_for_confidence(0.99, state),
            expected_pulls=calculator.expected_pulls(state),
            real_money_cost=self._topup_cost(profile, banner, balance, pulls_for_90),
        )

    def plan_by_deadline(
        self,
        profile: GameProfile,
        banner_name: str,
        tier_name: str,
        state: PityState,
        today: date,
        deadline: date,
    ) -> DeadlineProjection:
        banner = profile.banner(banner_name)
        calculator = self.calculator_for(banner.tier(tier_name).rule)
        planner = BudgetPlanner(
            banner,
            self._converter,
            {currency.code: currency for currency in profile.currencies},
        )
        horizon = BudgetHorizon(today, deadline)
        pulls = planner.projected_pulls(profile.balances, profile.incomes, horizon)
        target = calculator.pulls_for_confidence(_TARGET_CONFIDENCE, state)
        target_pulls = pulls if target is None else target
        daily = planner.required_daily_income(
            target_pulls, profile.balances, profile.incomes, horizon
        )
        return DeadlineProjection(
            pulls=pulls,
            success_probability=calculator.success_probability(pulls, state),
            target_pulls=target_pulls,
            required_daily_income=Money(daily, banner.cost_per_pull.currency),
        )

    def success_curve(
        self,
        profile: GameProfile,
        banner_name: str,
        tier_name: str,
        state: PityState,
        max_pulls: int = 200,
    ) -> list[float]:
        banner = profile.banner(banner_name)
        return self.calculator_for(banner.tier(tier_name).rule).cumulative_curve(max_pulls, state)

    def _balance(self, profile: GameProfile, banner: Banner) -> Money:
        cost_currency = banner.cost_per_pull.currency
        balance = profile.balances.get(cost_currency.code)
        if balance is None:
            return Money(Decimal(0), cost_currency)
        return self._converter.convert(balance, cost_currency)

    def _topup_cost(
        self, profile: GameProfile, banner: Banner, balance: Money, target_pulls: int | None
    ) -> Money | None:
        """Cheapest top-up cost to reach the target pulls, when the profile has packages."""
        if target_pulls is None or not profile.topup_packages or not profile.display_currency_code:
            return None
        needed = banner.cost_per_pull.amount * target_pulls - balance.amount
        if needed <= 0:
            return None
        required = int(needed.to_integral_value(rounding=ROUND_CEILING))
        plan = TopUpOptimizer(profile.topup_packages).cheapest_plan(required)
        display = profile.currency(profile.display_currency_code)
        return self._converter.convert(plan.total_price, display)
