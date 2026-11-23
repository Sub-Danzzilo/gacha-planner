from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Item:
    """One item obtainable from a banner.

    ``image_path`` is stored relative to the profile folder so profiles stay movable. Images are
    loaded only by the UI.
    """

    name: str
    tier_name: str
    is_featured: bool = False
    image_path: Path | None = None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Item name cannot be empty")
