# Currency and balance input. Phase 1.
#
# Class `CurrencyView(ttk.Frame)`:
#   - A table of currencies: name, kind (game or real), code (enabled only for real),
#     current balance.
#   - Add, edit and remove buttons. Removing a currency that a banner uses must ask the
#     presenter first and show its refusal message.
#   - Phase 2: a second section for top-up packages (price, price currency, amount, bonus,
#     first-time-only) and a small manual exchange-rate table (from, to, rate).
#
# Rules:
#   - Strings in, strings out. Parsing and validation live in `CurrencyPresenter`.
#   - Decimal input accepts both "." and "," as separators; the presenter handles it.
