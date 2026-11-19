# Item image and name card. Phase 5.
#
# Class `ItemCard(ttk.Frame)`:
#   - Shows a thumbnail (Pillow image resized to a fixed size) and the item name, with a visual
#     difference for featured items.
#   - Loads images lazily from `Item.image_path`; if the path is missing or unreadable, show a
#     neutral placeholder and do not crash.
#
# Rules:
#   - Keep a reference to every `ImageTk.PhotoImage` on the widget instance. Tkinter drops
#     images that are only referenced locally.
#   - Pillow is imported only here.
#   - Cache resized images per path to avoid reloading on every redraw.
