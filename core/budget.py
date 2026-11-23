from __future__ import annotations

import calendar
import enum
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import ROUND_CEILING, Decimal

from core.exchange import CurrencyConverter
from core.models.banner import Banner
from core.models.currency import Currency, Money


class IncomePeriod(enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


@dataclass(frozen=True, slots=True)
class IncomeSource:
    """Recurring income that starts on ``first_credit``."""

    name: str
    currency_code: str
    amount: int
    period: IncomePeriod
    first_credit: date

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Income name cannot be empty")
        if not self.currency_code or self.currency_code != self.currency_code.upper():
            raise ValueError(
                f"Currency code must be uppercase and non-empty: {self.currency_code!r}"
            )
        if self.amount <= 0:
            raise ValueError("Income amount must be greater than 0")


@dataclass(frozen=True, slots=True)
class BudgetHorizon:
    today: date
    deadline: date


class BudgetPlanner:
    """Projects balance and reachable pulls up to a banner deadline.

    Credit rule: the counted range is ``(today, deadline]`` - today is not counted, the deadline
    day is. DAILY credits every day, WEEKLY every 7 days from ``first_credit``, MONTHLY on the same
    day of each month and on the month's last day when the month is shorter.
    """

    def __init__(
        self, banner: Banner, converter: CurrencyConverter, currencies: Mapping[str, Currency]
    ) -> None:
        self._banner = banner
        self._converter = converter
        self._currencies = dict(currencies)

    def credits_between(self, source: IncomeSource, today: date, deadline: date) -> int:
        if deadline <= today:
            return 0
        if source.period is IncomePeriod.DAILY:
            return (deadline - today).days * source.amount
        if source.period is IncomePeriod.WEEKLY:
            return self._weekly_credits(source, today, deadline)
        return self._monthly_credits(source, today, deadline)

    def projected_pulls(
        self,
        balances: Mapping[str, Money],
        incomes: Sequence[IncomeSource],
        horizon: BudgetHorizon,
    ) -> int:
        total = self._projected_currency(balances, incomes, horizon)
        return int(total // self._banner.cost_per_pull.amount)

    def required_daily_income(
        self,
        target_pulls: int,
        balances: Mapping[str, Money],
        incomes: Sequence[IncomeSource],
        horizon: BudgetHorizon,
    ) -> Decimal:
        if target_pulls < 0:
            raise ValueError("Target pull count cannot be negative")
        if horizon.deadline <= horizon.today:
            raise ValueError("Deadline must be after today to compute daily income")
        needed = self._banner.cost_per_pull.amount * target_pulls - self._projected_currency(
            balances, incomes, horizon
        )
        if needed <= 0:
            return Decimal(0)
        days = (horizon.deadline - horizon.today).days
        scale = Decimal(1).scaleb(-self._banner.cost_per_pull.currency.decimals)
        return (needed / days).quantize(scale, rounding=ROUND_CEILING)

    def _projected_currency(
        self,
        balances: Mapping[str, Money],
        incomes: Sequence[IncomeSource],
        horizon: BudgetHorizon,
    ) -> Decimal:
        target = self._banner.cost_per_pull.currency
        total = sum(
            (self._converter.exact(money, target).amount for money in balances.values()),
            Decimal(0),
        )
        for source in incomes:
            credited = self.credits_between(source, horizon.today, horizon.deadline)
            if credited == 0:
                continue
            income = Money(Decimal(credited), self._currency(source.currency_code))
            total += self._converter.exact(income, target).amount
        return total

    def _currency(self, code: str) -> Currency:
        try:
            return self._currencies[code]
        except KeyError:
            raise ValueError(f"Unknown currency {code!r} for BudgetPlanner") from None

    @staticmethod
    def _weekly_credits(source: IncomeSource, today: date, deadline: date) -> int:
        if source.first_credit > deadline:
            return 0
        if source.first_credit > today:
            start = source.first_credit
        else:
            weeks = (today - source.first_credit).days // 7 + 1
            start = source.first_credit + timedelta(days=weeks * 7)
        if start > deadline:
            return 0
        return ((deadline - start).days // 7 + 1) * source.amount

    @staticmethod
    def _monthly_credits(source: IncomeSource, today: date, deadline: date) -> int:
        count = 0
        cursor = date(source.first_credit.year, source.first_credit.month, 1)
        while cursor <= deadline:
            last_day = calendar.monthrange(cursor.year, cursor.month)[1]
            credit_day = cursor.replace(day=min(source.first_credit.day, last_day))
            if today < credit_day <= deadline:
                count += 1
            cursor = date(cursor.year + cursor.month // 12, cursor.month % 12 + 1, 1)
        return count * source.amount
