# Currencies and balances. Phase 1 (real-currency behavior used from phase 2).
#
# Classes and enums:
#   - `CurrencyKind(enum.Enum)`: `GAME`, `REAL`
#   - `Currency` (frozen dataclass): `name: str`, `kind: CurrencyKind`, `code: str | None`
#         `code` (for example "USD", "IDR") is required when `kind` is `REAL` and must be None
#         for `GAME`. Equality is by name and code.
#   - `Money` (frozen dataclass): `amount: Decimal`, `currency: Currency`
#         Supports `+`, `-`, comparison and multiplication by an int or Decimal. Operations on
#         two different currencies raise `InvalidCurrencyError`; never convert implicitly.
#         Negative amounts are allowed only for differences; document this on the class.
#   - `Wallet`
#         Holds balances per currency. `balance(currency) -> Money`, `add(Money)`,
#         `spend(Money) -> None` (raises if insufficient), `total_in(currency, converter)`
#         is NOT here; conversion lives in `core/exchange.py` (phase 2).
#
# Rules:
#   - All amounts are `Decimal`. Reject `float` input with a `TypeError`.
#   - Do not hard-code any currency names or exchange rates in this module.
