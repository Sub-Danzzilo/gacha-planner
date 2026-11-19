# Pull history records. Phase 4.
#
# Classes:
#   - `PullRecord` (frozen dataclass): `pull_number: int`, `tier_name: str`,
#         `item_name: str | None`, `timestamp: datetime | None`
#   - `PullLog`
#         Ordered collection of records for one banner. Methods:
#           `add(record)`, `extend(records)`, `__len__`, `__iter__`
#           `count_for_tier(tier_name) -> int`
#           `pulls_between_successes(tier_name) -> list[int]`
#         Reject a pull number that is not exactly one more than the last stored one.
#
# Also provide parsing from a simple CSV text format (`pull_number,tier,item`) as a
# classmethod `PullLog.from_csv_text(text: str)`; the file reading itself stays in storage or UI.
