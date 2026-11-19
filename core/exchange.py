# Manual exchange rates. Phase 2.
#
# Rates are entered by the user. There is no network access in this project.
#
# Abstract class `ExchangeRateProvider` (abc.ABC):
#   - `rate(self, source: str, target: str) -> Decimal`
#         units of `target` per one unit of `source`; raises `MissingExchangeRateError`
# This interface exists as a documented extension point. Do not write an API-backed provider.
#
# Class `ManualRateProvider(ExchangeRateProvider)`:
#   - `set_rate(self, source: str, target: str, rate: Decimal) -> None`
#         rate must be positive. Also make the inverse available implicitly (1 / rate) unless the
#         user stored an explicit inverse.
#   - `rates(self) -> dict[tuple[str, str], Decimal]`    for saving and display
#   - Identity conversion (same code) returns Decimal(1) without being stored.
#
# Class `CurrencyConverter`:
#   - `__init__(self, provider: ExchangeRateProvider)`
#   - `convert(self, money: Money, target_code: str) -> Money`
#         only real currencies can be converted; game currencies raise `InvalidCurrencyError`.
#         Round to 2 decimal places using `ROUND_HALF_UP` for display values, but keep the
#         unrounded `Decimal` internally for further calculation.
#
# Notes:
#   - Each banner or game has its own price currency; one "display currency" chosen by the
#     user is used to present totals. The converter bridges the two.
