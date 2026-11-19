# Resource planning over time. Phase 2.
#
# Class `ResourcePlanner`:
#   - `__init__(self, banner: Banner, calculator: ProbabilityCalculator)`
#
#   - `project_balance(self, plan: IncomePlan, today: date, deadline: date) -> int`
#         Pulls obtainable by `deadline` from current balance plus income. Include today and
#         the deadline day consistently and document the choice.
#
#   - `success_by_deadline(self, plan: IncomePlan, today: date, deadline: date,
#                          starting_pity: int = 0) -> float`
#
#   - `required_daily_income(self, target_pulls: int, plan: IncomePlan, today: date,
#                            deadline: date) -> Decimal`
#         Extra game currency per day needed to reach `target_pulls`; zero if already enough.
#
#   - `shortfall(self, target_pulls: int, plan: IncomePlan, today: date, deadline: date) -> int`
#
# Class `IncomePlan` (frozen dataclass):
#   - `balances: Wallet`                       current holdings per currency
#   - `daily_income: Mapping[Currency, Decimal]`
#   - `weekly_income: Mapping[Currency, Decimal]`
#   - `one_time_income: Mapping[date, Mapping[Currency, Decimal]]`   events and rewards
#
# Rules:
#   - Convert everything to the banner's cost currency using explicit conversion rules from the
#     currency module; two different game currencies are only combinable through a user-defined
#     ratio, never guessed.
#   - Dates come from arguments. Never call `date.today()` inside this module.
