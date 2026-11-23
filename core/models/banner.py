from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from core.models.currency import CurrencyKind, CurrencyMismatchError, Money
from core.models.item import Item
from core.models.pity import PullRule


@dataclass(frozen=True, slots=True)
class RateTier:
    """One rarity class on a banner, for example "5-star"."""

    name: str
    rule: PullRule

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Tier name cannot be empty")


@dataclass(frozen=True, slots=True)
class Banner:
    """Container for banner data. A banner never computes any probability."""

    name: str
    tiers: tuple[RateTier, ...]
    items: tuple[Item, ...]
    cost_per_pull: Money
    ends_on: date | None = None

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if not self.name.strip():
            raise ValueError("Banner name cannot be empty")
        if not self.tiers:
            raise ValueError("A banner needs at least one tier")
        tier_names = [tier.name for tier in self.tiers]
        if len(set(tier_names)) != len(tier_names):
            raise ValueError("Tier names must be unique within a banner")
        known = set(tier_names)
        for item in self.items:
            if item.tier_name not in known:
                raise ValueError(
                    f"Item {item.name!r} uses a tier that is not on the banner: {item.tier_name!r}"
                )
        if self.cost_per_pull.currency.kind is not CurrencyKind.GAME:
            raise ValueError("Pull cost must be in game currency")
        if self.cost_per_pull.amount <= 0:
            raise ValueError("Pull cost must be greater than 0")

    def tier(self, name: str) -> RateTier:
        for tier in self.tiers:
            if tier.name == name:
                return tier
        raise KeyError(f"Tier {name!r} does not exist on banner {self.name!r}")

    def items_for_tier(self, tier_name: str) -> tuple[Item, ...]:
        return tuple(item for item in self.items if item.tier_name == tier_name)

    def pulls_affordable(self, balance: Money) -> int:
        if balance.currency.code != self.cost_per_pull.currency.code:
            raise CurrencyMismatchError(
                f"Balance is in {balance.currency.code}, pull cost is in "
                f"{self.cost_per_pull.currency.code}; convert first"
            )
        return int(balance.amount // self.cost_per_pull.amount)
