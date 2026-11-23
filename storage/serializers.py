from __future__ import annotations

from collections.abc import Mapping
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from core.budget import IncomePeriod, IncomeSource
from core.errors import StorageError
from core.exchange import ExchangeRate
from core.models.banner import Banner, RateTier
from core.models.currency import Currency, CurrencyKind, Money
from core.models.item import Item
from core.models.pity import FeaturedGuarantee, PityConfig, PullRule
from core.models.profile import GameProfile
from core.models.topup import TopUpPackage

SCHEMA_VERSION = 1


class ProfileSerializer:
    """Converts GameProfile to and from JSON-compatible dictionaries."""

    def to_dict(self, profile: GameProfile) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "name": profile.name,
            "display_currency_code": profile.display_currency_code,
            "currencies": [self._currency_to_dict(currency) for currency in profile.currencies],
            "balances": {code: str(money.amount) for code, money in profile.balances.items()},
            "banners": [self._banner_to_dict(banner) for banner in profile.banners],
            "topup_packages": [
                {
                    "price": self._money_to_dict(package.price),
                    "grants": package.grants.code,
                    "base_amount": package.base_amount,
                    "bonus_amount": package.bonus_amount,
                    "first_purchase_bonus": package.first_purchase_bonus,
                }
                for package in profile.topup_packages
            ],
            "exchange_rates": [
                {
                    "source_code": exchange_rate.source_code,
                    "target_code": exchange_rate.target_code,
                    "rate": str(exchange_rate.rate),
                }
                for exchange_rate in profile.exchange_rates
            ],
            "incomes": [
                {
                    "name": source.name,
                    "currency_code": source.currency_code,
                    "amount": source.amount,
                    "period": source.period.value,
                    "first_credit": source.first_credit.isoformat(),
                }
                for source in profile.incomes
            ],
        }

    def from_dict(self, data: Mapping[str, Any]) -> GameProfile:
        version = data.get("schema_version")
        if version != SCHEMA_VERSION:
            raise StorageError(
                f"Unsupported profile schema version: {version!r} (supported: {SCHEMA_VERSION})"
            )
        currencies = tuple(
            self._currency_from_dict(item, f"currencies[{index}]")
            for index, item in enumerate(_sequence(_required(data, "currencies"), "currencies"))
        )
        known = {currency.code: currency for currency in currencies}

        balances: dict[str, Money] = {}
        for code, amount in _mapping(_required(data, "balances"), "balances").items():
            if code not in known:
                raise StorageError(f"balances.{code} refers to an unknown currency")
            balances[code] = Money(_decimal(amount, f"balances.{code}"), known[code])

        banners = tuple(
            self._banner_from_dict(item, f"banners[{index}]", known)
            for index, item in enumerate(_sequence(_required(data, "banners"), "banners"))
        )
        packages = tuple(
            self._package_from_dict(item, f"topup_packages[{index}]", known)
            for index, item in enumerate(
                _sequence(_required(data, "topup_packages"), "topup_packages")
            )
        )
        exchange_rates = tuple(
            self._exchange_rate_from_dict(item, f"exchange_rates[{index}]")
            for index, item in enumerate(
                _sequence(_required(data, "exchange_rates"), "exchange_rates")
            )
        )
        incomes = tuple(
            self._income_from_dict(item, f"incomes[{index}]", known)
            for index, item in enumerate(_sequence(_required(data, "incomes"), "incomes"))
        )

        profile = GameProfile(
            name=_text(data.get("name"), "name"),
            currencies=currencies,
            balances=balances,
            banners=banners,
            topup_packages=packages,
            exchange_rates=exchange_rates,
            incomes=incomes,
            display_currency_code=_text(
                _required(data, "display_currency_code"), "display_currency_code"
            ),
        )
        return profile

    @staticmethod
    def _currency_to_dict(currency: Currency) -> dict[str, Any]:
        return {
            "code": currency.code,
            "name": currency.name,
            "kind": currency.kind.value,
            "decimals": currency.decimals,
        }

    @staticmethod
    def _currency_from_dict(data: Any, field: str) -> Currency:
        entry = _mapping(data, field)
        kind_text = _text(entry.get("kind"), f"{field}.kind")
        try:
            kind = CurrencyKind(kind_text)
        except ValueError as exc:
            raise StorageError(f"{field}.kind is not a known kind: {kind_text!r}") from exc
        try:
            return Currency(
                code=_text(entry.get("code"), f"{field}.code"),
                name=_text(entry.get("name"), f"{field}.name"),
                kind=kind,
                decimals=_integer(entry.get("decimals", 0), f"{field}.decimals"),
            )
        except ValueError as exc:
            raise StorageError(f"{field}: {exc}") from exc

    @staticmethod
    def _money_to_dict(money: Money) -> dict[str, Any]:
        return {"amount": str(money.amount), "currency_code": money.currency.code}

    @staticmethod
    def _money_from_dict(data: Any, field: str, currencies: Mapping[str, Currency]) -> Money:
        entry = _mapping(data, field)
        code = _text(entry.get("currency_code"), f"{field}.currency_code")
        if code not in currencies:
            raise StorageError(f"{field}.currency_code refers to an unknown currency: {code!r}")
        return Money(_decimal(entry.get("amount"), f"{field}.amount"), currencies[code])

    def _banner_to_dict(self, banner: Banner) -> dict[str, Any]:
        return {
            "name": banner.name,
            "cost_per_pull": self._money_to_dict(banner.cost_per_pull),
            "ends_on": None if banner.ends_on is None else banner.ends_on.isoformat(),
            "tiers": [
                {"name": tier.name, "rule": self._rule_to_dict(tier.rule)} for tier in banner.tiers
            ],
            "items": [
                {
                    "name": item.name,
                    "tier_name": item.tier_name,
                    "is_featured": item.is_featured,
                    "image_path": None if item.image_path is None else item.image_path.as_posix(),
                }
                for item in banner.items
            ],
        }

    def _banner_from_dict(
        self, data: Any, field: str, currencies: Mapping[str, Currency]
    ) -> Banner:
        entry = _mapping(data, field)
        tiers = tuple(
            self._tier_from_dict(item, f"{field}.tiers[{index}]")
            for index, item in enumerate(_sequence(entry.get("tiers"), f"{field}.tiers"))
        )
        items = tuple(
            self._item_from_dict(item, f"{field}.items[{index}]")
            for index, item in enumerate(_sequence(entry.get("items"), f"{field}.items"))
        )
        ends_on_text = entry.get("ends_on")
        ends_on = None if ends_on_text is None else _date(ends_on_text, f"{field}.ends_on")
        try:
            return Banner(
                name=_text(entry.get("name"), f"{field}.name"),
                tiers=tiers,
                items=items,
                cost_per_pull=self._money_from_dict(
                    entry.get("cost_per_pull"), f"{field}.cost_per_pull", currencies
                ),
                ends_on=ends_on,
            )
        except ValueError as exc:
            raise StorageError(f"{field}: {exc}") from exc

    @staticmethod
    def _tier_from_dict(data: Any, field: str) -> RateTier:
        entry = _mapping(data, field)
        rule_data = _mapping(entry.get("rule"), f"{field}.rule")
        try:
            return RateTier(
                name=_text(entry.get("name"), f"{field}.name"),
                rule=_rule_from_dict(rule_data, f"{field}.rule"),
            )
        except ValueError as exc:
            raise StorageError(f"{field}: {exc}") from exc

    @staticmethod
    def _item_from_dict(data: Any, field: str) -> Item:
        entry = _mapping(data, field)
        image_path_text = entry.get("image_path")
        try:
            return Item(
                name=_text(entry.get("name"), f"{field}.name"),
                tier_name=_text(entry.get("tier_name"), f"{field}.tier_name"),
                is_featured=_boolean(entry.get("is_featured", False), f"{field}.is_featured"),
                image_path=None
                if image_path_text is None
                else Path(_text(image_path_text, f"{field}.image_path")),
            )
        except ValueError as exc:
            raise StorageError(f"{field}: {exc}") from exc

    @staticmethod
    def _rule_to_dict(rule: PullRule) -> dict[str, Any]:
        pity = rule.pity
        guarantee = rule.guarantee
        return {
            "base_rate": rule.base_rate,
            "pity": None
            if pity is None
            else {
                "hard_pity": pity.hard_pity,
                "soft_pity_start": pity.soft_pity_start,
                "soft_pity_step": pity.soft_pity_step,
            },
            "guarantee": None
            if guarantee is None
            else {
                "win_chance": guarantee.win_chance,
                "guaranteed_after_loss": guarantee.guaranteed_after_loss,
            },
        }

    @staticmethod
    def _package_from_dict(
        data: Any, field: str, currencies: Mapping[str, Currency]
    ) -> TopUpPackage:
        entry = _mapping(data, field)
        grants_code = _text(entry.get("grants"), f"{field}.grants")
        if grants_code not in currencies:
            raise StorageError(f"{field}.grants refers to an unknown currency: {grants_code!r}")
        try:
            return TopUpPackage(
                price=ProfileSerializer._money_from_dict(
                    entry.get("price"), f"{field}.price", currencies
                ),
                grants=currencies[grants_code],
                base_amount=_integer(entry.get("base_amount"), f"{field}.base_amount"),
                bonus_amount=_integer(entry.get("bonus_amount", 0), f"{field}.bonus_amount"),
                first_purchase_bonus=_integer(
                    entry.get("first_purchase_bonus", 0), f"{field}.first_purchase_bonus"
                ),
            )
        except ValueError as exc:
            raise StorageError(f"{field}: {exc}") from exc

    @staticmethod
    def _exchange_rate_from_dict(data: Any, field: str) -> ExchangeRate:
        entry = _mapping(data, field)
        try:
            return ExchangeRate(
                source_code=_text(entry.get("source_code"), f"{field}.source_code"),
                target_code=_text(entry.get("target_code"), f"{field}.target_code"),
                rate=_decimal(entry.get("rate"), f"{field}.rate"),
            )
        except ValueError as exc:
            raise StorageError(f"{field}: {exc}") from exc

    @staticmethod
    def _income_from_dict(
        data: Any, field: str, currencies: Mapping[str, Currency]
    ) -> IncomeSource:
        entry = _mapping(data, field)
        currency_code = _text(entry.get("currency_code"), f"{field}.currency_code")
        if currency_code not in currencies:
            raise StorageError(
                f"{field}.currency_code refers to an unknown currency: {currency_code!r}"
            )
        period_text = _text(entry.get("period"), f"{field}.period")
        try:
            period = IncomePeriod(period_text)
        except ValueError as exc:
            raise StorageError(f"{field}.period is not a known period: {period_text!r}") from exc
        try:
            return IncomeSource(
                name=_text(entry.get("name"), f"{field}.name"),
                currency_code=currency_code,
                amount=_integer(entry.get("amount"), f"{field}.amount"),
                period=period,
                first_credit=_date(entry.get("first_credit"), f"{field}.first_credit"),
            )
        except ValueError as exc:
            raise StorageError(f"{field}: {exc}") from exc


def _rule_from_dict(data: Mapping[str, Any], field: str) -> PullRule:
    pity_data = data.get("pity")
    pity = None
    if pity_data is not None:
        entry = _mapping(pity_data, f"{field}.pity")
        hard_pity = entry.get("hard_pity")
        soft_pity_start = entry.get("soft_pity_start")
        pity = PityConfig(
            hard_pity=None if hard_pity is None else _integer(hard_pity, f"{field}.pity.hard_pity"),
            soft_pity_start=None
            if soft_pity_start is None
            else _integer(soft_pity_start, f"{field}.pity.soft_pity_start"),
            soft_pity_step=_real(entry.get("soft_pity_step", 0.0), f"{field}.pity.soft_pity_step"),
        )
    guarantee_data = data.get("guarantee")
    guarantee = None
    if guarantee_data is not None:
        entry = _mapping(guarantee_data, f"{field}.guarantee")
        guarantee = FeaturedGuarantee(
            win_chance=_real(entry.get("win_chance"), f"{field}.guarantee.win_chance"),
            guaranteed_after_loss=_boolean(
                entry.get("guaranteed_after_loss", True),
                f"{field}.guarantee.guaranteed_after_loss",
            ),
        )
    return PullRule(
        base_rate=_real(data.get("base_rate"), f"{field}.base_rate"),
        pity=pity,
        guarantee=guarantee,
    )


def _required(entry: Mapping[str, Any], key: str) -> Any:
    if key not in entry:
        raise StorageError(f"Field {key!r} is missing from the profile")
    return entry[key]


def _mapping(value: Any, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise StorageError(f"{field} must be a JSON object")
    return value


def _sequence(value: Any, field: str) -> list[Any]:
    if not isinstance(value, list):
        raise StorageError(f"{field} must be a JSON array")
    return value


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str):
        raise StorageError(f"{field} must be a string")
    return value


def _integer(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise StorageError(f"{field} must be an integer")
    return value


def _boolean(value: Any, field: str) -> bool:
    if not isinstance(value, bool):
        raise StorageError(f"{field} must be a boolean")
    return value


def _real(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise StorageError(f"{field} must be a number")
    return float(value)


def _decimal(value: Any, field: str) -> Decimal:
    text = _text(value, field)
    try:
        return Decimal(text)
    except InvalidOperation as exc:
        raise StorageError(f"{field} is not a decimal number: {text!r}") from exc


def _date(value: Any, field: str) -> date:
    text = _text(value, field)
    try:
        return date.fromisoformat(text)
    except ValueError as exc:
        raise StorageError(f"{field} is not an ISO date (YYYY-MM-DD): {text!r}") from exc
