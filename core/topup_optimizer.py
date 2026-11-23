from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal

from core.models.currency import Money
from core.models.topup import TopUpPackage


@dataclass(frozen=True, slots=True)
class TopUpPlan:
    purchases: tuple[tuple[TopUpPackage, int], ...]
    total_price: Money
    total_received: int
    surplus: int


class TopUpOptimizer:
    """Cheapest combination of top-up packages that covers the required game currency.

    Overshooting is allowed: a large package that is cheaper per unit still wins even when it
    exceeds ``required_amount``.
    """

    def __init__(self, packages: Sequence[TopUpPackage]) -> None:
        if not packages:
            raise ValueError("At least one top-up package is required")
        price_codes = {package.price.currency.code for package in packages}
        if len(price_codes) != 1:
            raise ValueError("All package prices must use the same currency")
        grant_codes = {package.grants.code for package in packages}
        if len(grant_codes) != 1:
            raise ValueError("All packages must grant the same game currency")
        self._packages = tuple(packages)
        self._price_currency = packages[0].price.currency

    def cheapest_plan(
        self, required_amount: int, first_purchase_available: bool = True
    ) -> TopUpPlan:
        if required_amount <= 0:
            return TopUpPlan((), Money(Decimal(0), self._price_currency), 0, 0)

        limit = required_amount + max(package.first_purchase_total for package in self._packages)
        best_cost: list[Decimal | None] = [None] * (limit + 1)
        best_cost[0] = Decimal(0)
        previous: list[tuple[int, int] | None] = [None] * (limit + 1)

        for amount in range(limit + 1):
            current_cost = best_cost[amount]
            if current_cost is None:
                continue
            for index, package in enumerate(self._packages):
                following = amount + package.total_amount
                if following > limit:
                    continue
                candidate = current_cost + package.price.amount
                existing = best_cost[following]
                if existing is None or candidate < existing:
                    best_cost[following] = candidate
                    previous[following] = (amount, index)

        chosen = _Choice.empty()
        for amount in range(required_amount, limit + 1):
            cost = best_cost[amount]
            if cost is not None:
                chosen = chosen.prefer(cost, amount, None, required_amount)
        if first_purchase_available:
            for index, package in enumerate(self._packages):
                if package.first_purchase_bonus <= 0:
                    continue
                for amount in range(required_amount, limit + 1):
                    before = amount - package.first_purchase_total
                    if before < 0:
                        continue
                    base_cost = best_cost[before]
                    if base_cost is None:
                        continue
                    chosen = chosen.prefer(
                        base_cost + package.price.amount, amount, index, required_amount
                    )

        if chosen.cost is None or chosen.amount is None:
            raise ValueError("No combination of packages can reach the required amount")

        return self._build_plan(chosen, previous, required_amount)

    def _build_plan(
        self,
        chosen: _Choice,
        previous: Sequence[tuple[int, int] | None],
        required_amount: int,
    ) -> TopUpPlan:
        assert chosen.cost is not None
        assert chosen.amount is not None
        counts: dict[int, int] = {}
        cursor = chosen.amount
        if chosen.first_index is not None:
            counts[chosen.first_index] = 1
            cursor -= self._packages[chosen.first_index].first_purchase_total
        while cursor > 0:
            step = previous[cursor]
            assert step is not None
            before, index = step
            counts[index] = counts.get(index, 0) + 1
            cursor = before
        purchases = tuple((self._packages[index], counts[index]) for index in sorted(counts))
        return TopUpPlan(
            purchases=purchases,
            total_price=Money(chosen.cost, self._price_currency),
            total_received=chosen.amount,
            surplus=chosen.amount - required_amount,
        )


@dataclass(frozen=True, slots=True)
class _Choice:
    cost: Decimal | None = None
    amount: int | None = None
    first_index: int | None = None

    @classmethod
    def empty(cls) -> _Choice:
        return cls()

    def prefer(
        self,
        cost: Decimal,
        amount: int,
        first_index: int | None,
        required_amount: int,
    ) -> _Choice:
        if self.cost is None or self.amount is None:
            return _Choice(cost, amount, first_index)
        cheaper = cost < self.cost
        same_price_smaller_surplus = (
            cost == self.cost and amount - required_amount < self.amount - required_amount
        )
        if cheaper or same_price_smaller_surplus:
            return _Choice(cost, amount, first_index)
        return self
