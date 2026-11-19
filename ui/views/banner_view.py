# Banner input form. Phase 1.
#
# Class `BannerView(ttk.Frame)`:
#   - Fields: banner name, target tier name, base rate (percent), pity type selector
#     (none, hard pity only, soft pity), soft pity start, soft pity step, hard pity,
#     pull cost, cost currency (combobox filled from the currency list), starting pity.
#   - A small table (ttk.Treeview) for items: name, tier, featured flag, plus buttons to add,
#     edit and remove. A "generate random name" button fills the name field using the
#     presenter, which uses `ItemNameGenerator`.
#   - Show only the pity fields relevant to the selected pity type.
#   - Display validation messages next to the fields the presenter names.
#
# Rules:
#   - No parsing and no domain validation here; collect strings and pass them to
#     `BannerPresenter`.
#   - Phase 2 adds fields for the 50/50 guarantee (featured share, carry-over).
#   - Phase 5 adds an image picker per item.
