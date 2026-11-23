import random

import pytest

from core.naming import RandomNameGenerator


def test_generated_name_is_not_taken() -> None:
    generator = RandomNameGenerator(random.Random(3))
    name = generator.generate({"Blue Moon"})
    assert name != "Blue Moon"
    assert " " in name


def test_names_vary_across_calls_with_taken_updated() -> None:
    generator = RandomNameGenerator(random.Random(11))
    taken: set[str] = set()
    first = generator.generate(taken)
    taken.add(first)
    second = generator.generate(taken)
    assert second != first


def test_exhausted_combinations_raise(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("core.naming._ADJECTIVES", ("Silent",))
    monkeypatch.setattr("core.naming._NOUNS", ("Echo",))
    generator = RandomNameGenerator(random.Random(1))
    with pytest.raises(ValueError):
        generator.generate({"Silent Echo"})
