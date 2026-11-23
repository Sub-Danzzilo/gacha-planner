from pathlib import Path

import pytest

from core.models.item import Item


def test_item_defaults() -> None:
    item = Item(name="Sword", tier_name="5-star")
    assert item.is_featured is False
    assert item.image_path is None


def test_item_keeps_relative_image_path() -> None:
    item = Item(name="Sword", tier_name="5-star", image_path=Path("images/sword.png"))
    assert item.image_path == Path("images/sword.png")


def test_item_rejects_blank_name() -> None:
    with pytest.raises(ValueError):
        Item(name="   ", tier_name="5-star")
