from __future__ import annotations

import random

_ADJECTIVES: tuple[str, ...] = (
    "Blue",
    "Golden",
    "Silver",
    "Silent",
    "Dark",
    "Bright",
    "Soft",
    "Sharp",
    "Warm",
    "Cold",
    "Sweet",
    "Noble",
    "Graceful",
    "Swift",
    "Calm",
    "Grand",
    "Little",
    "High",
    "Low",
    "Clear",
)

_NOUNS: tuple[str, ...] = (
    "Moon",
    "Star",
    "Sun",
    "Wind",
    "Water",
    "Fire",
    "Earth",
    "Rain",
    "Snow",
    "Cloud",
    "Dusk",
    "Dawn",
    "Mist",
    "Wave",
    "Island",
    "Valley",
    "Peak",
    "Forest",
    "Flower",
    "Shore",
)


class RandomNameGenerator:
    """Placeholder item names for players who do not want to type their own."""

    def __init__(self, rng: random.Random) -> None:
        self._rng = rng

    def generate(self, taken: set[str]) -> str:
        available = [
            f"{adjective} {noun}"
            for adjective in _ADJECTIVES
            for noun in _NOUNS
            if f"{adjective} {noun}" not in taken
        ]
        if not available:
            raise ValueError("All name combinations are taken; add a name manually")
        return self._rng.choice(available)
