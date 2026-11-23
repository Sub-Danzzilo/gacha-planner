from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class PullRecord:
    """One pull recorded by the player."""

    banner_name: str
    tier_name: str
    item_name: str | None
    pulled_at: datetime
    was_featured: bool | None = None


class PullLog:
    """An ordered collection of pulls; records are never changed once added."""

    def __init__(self, records: Iterable[PullRecord] = ()) -> None:
        self._records: list[PullRecord] = []
        self.extend(records)

    def add(self, record: PullRecord) -> None:
        self._records.append(record)

    def extend(self, records: Iterable[PullRecord]) -> None:
        for record in records:
            self.add(record)

    def __len__(self) -> int:
        return len(self._records)

    def __iter__(self) -> Iterator[PullRecord]:
        return iter(self._records)

    def total(self) -> int:
        return len(self._records)

    def hits(self, tier_name: str) -> int:
        return sum(1 for record in self._records if record.tier_name == tier_name)

    def for_banner(self, banner_name: str) -> PullLog:
        return PullLog(record for record in self._records if record.banner_name == banner_name)
