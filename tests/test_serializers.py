import json
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest

from core.budget import IncomePeriod, IncomeSource
from core.errors import StorageError
from core.exchange import ExchangeRate
from core.models.banner import Banner, RateTier
from core.models.currency import Currency, CurrencyKind, Money
from core.models.item import Item
from core.models.pity import FeaturedGuarantee, PityConfig, PullRule
from core.models.profile import GameProfile
from core.models.topup import TopUpPackage
from storage.profile_repository import ProfileRepository
from storage.serializers import ProfileSerializer

DIAMOND = Currency(code="DIAMOND", name="Diamond", kind=CurrencyKind.GAME)
USD = Currency(code="USD", name="Dolar", kind=CurrencyKind.REAL, decimals=2)
IDR = Currency(code="IDR", name="Rupiah", kind=CurrencyKind.REAL)


def _profile() -> GameProfile:
    banner = Banner(
        name="Test banner",
        tiers=(
            RateTier(
                name="5-star",
                rule=PullRule(
                    base_rate=0.013,
                    pity=PityConfig(hard_pity=90, soft_pity_start=74, soft_pity_step=0.06),
                    guarantee=FeaturedGuarantee(win_chance=0.5),
                ),
            ),
        ),
        items=(
            Item(
                name="Sword",
                tier_name="5-star",
                is_featured=True,
                image_path=Path("images/sword.png"),
            ),
        ),
        cost_per_pull=Money(Decimal("160"), DIAMOND),
        ends_on=date(2026, 12, 31),
    )
    return GameProfile(
        name="Test_Profile",
        currencies=(DIAMOND, USD, IDR),
        balances={
            "DIAMOND": Money(Decimal("16000"), DIAMOND),
            "USD": Money(Decimal("12.34"), USD),
        },
        banners=(banner,),
        topup_packages=(
            TopUpPackage(
                price=Money(Decimal("4.99"), USD),
                grants=DIAMOND,
                base_amount=300,
                bonus_amount=30,
                first_purchase_bonus=60,
            ),
        ),
        exchange_rates=(ExchangeRate("USD", "IDR", Decimal("16000")),),
        incomes=(
            IncomeSource(
                name="Daily",
                currency_code="DIAMOND",
                amount=60,
                period=IncomePeriod.DAILY,
                first_credit=date(2026, 1, 1),
            ),
        ),
        display_currency_code="USD",
    )


def _repository(directory: Path) -> ProfileRepository:
    return ProfileRepository(directory, ProfileSerializer())


def test_round_trip_keeps_profile(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    profile = _profile()
    repository.save(profile)
    loaded = repository.load("Test_Profile")
    assert loaded == profile
    assert str(loaded.balances["USD"].amount) == "12.34"


def test_unknown_schema_version_is_rejected(tmp_path: Path) -> None:
    (tmp_path / "lama.json").write_text(
        json.dumps({"schema_version": 2, "name": "lama"}), encoding="utf-8"
    )
    with pytest.raises(StorageError):
        _repository(tmp_path).load("lama")


def test_missing_field_names_the_field(tmp_path: Path) -> None:
    data = ProfileSerializer().to_dict(_profile())
    del data["name"]
    (tmp_path / "broken.json").write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(StorageError, match="name"):
        _repository(tmp_path).load("broken")


def test_missing_top_level_field_is_rejected(tmp_path: Path) -> None:
    data = ProfileSerializer().to_dict(_profile())
    del data["balances"]
    (tmp_path / "broken.json").write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(StorageError, match="balances"):
        _repository(tmp_path).load("broken")


def test_wrongly_typed_field_names_the_path(tmp_path: Path) -> None:
    data: dict[str, Any] = ProfileSerializer().to_dict(_profile())
    data["banners"][0]["cost_per_pull"]["amount"] = 160
    (tmp_path / "broken.json").write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(StorageError, match="amount"):
        _repository(tmp_path).load("broken")


def test_repository_lifecycle(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    assert repository.list_profiles() == []
    repository.save(_profile())
    assert repository.list_profiles() == ["Test_Profile"]
    assert repository.exists("Test_Profile")
    repository.delete("Test_Profile")
    assert not repository.exists("Test_Profile")
    with pytest.raises(StorageError):
        repository.delete("Test_Profile")


@pytest.mark.parametrize("name", ["../evil", "name/profile", "", "pro fil"])
def test_bad_profile_names_are_rejected(tmp_path: Path, name: str) -> None:
    with pytest.raises(StorageError):
        _repository(tmp_path).exists(name)


def test_failed_save_keeps_previous_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repository = _repository(tmp_path)
    repository.save(_profile())

    def broken_dumps(*args: object, **kwargs: object) -> str:
        raise TypeError("cannot be serialized")

    monkeypatch.setattr("storage.profile_repository.json.dumps", broken_dumps)
    with pytest.raises(StorageError):
        repository.save(_profile())
    monkeypatch.undo()

    assert repository.load("Test_Profile") == _profile()
    assert list(tmp_path.glob("*.tmp")) == []
