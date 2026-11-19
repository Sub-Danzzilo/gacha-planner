# Top-up packages and cheapest-purchase planning. Phase 2.
#
# Class `TopUpPackage` (frozen dataclass):
#   - `price: Money`                       real money
#   - `base_amount: int`                   game currency received
#   - `bonus_amount: int = 0`
#   - `first_time_only: bool = False`      may be bought at most once
#   - property `total_amount -> int`
#
# Class `TopUpPlanner`:
#   - `__init__(self, packages: Sequence[TopUpPackage], converter: CurrencyConverter)`
#
#   - `cheapest_purchase(self, needed: int, display_code: str) -> PurchasePlan`
#         Find the cheapest multiset of packages whose total game currency is at least
#         `needed`. Overshooting is allowed. Prices are compared after conversion to
#         `display_code`.
#         Algorithm: dynamic programming over game-currency amount from 0 to
#         `needed + max_total_amount`, a bounded knapsack where `first_time_only` packages can be
#         used once and all others any number of times. Reconstruct the chosen packages from
#         parent pointers. Use `Decimal` for costs, `int` for amounts.
#         If `needed <= 0`, return an empty plan with zero cost.
#
# Class `PurchasePlan` (frozen dataclass):
#   - `packages: tuple[tuple[TopUpPackage, int], ...]`   package and count
#   - `total_cost: Money`
#   - `total_game_currency: int`
#   - `wasted: int`                        total received minus needed
#
# Edge cases to handle and test:
#   - no packages available
#   - a cheaper-per-unit package that overshoots versus a smaller exact fit
#   - first-time bonus package used once, then regular packages
