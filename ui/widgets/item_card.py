from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import ttk

from PIL import Image, ImageTk

from core.models.item import Item

_THUMBNAIL_SIZE = (96, 96)
_PLACEHOLDER_COLOR = (128, 128, 128)


class ItemCard(ttk.Frame):
    """Item thumbnail and name; the image loads once when the card is first shown."""

    def __init__(
        self, master: tk.Misc, item: Item, size: tuple[int, int] = _THUMBNAIL_SIZE
    ) -> None:
        super().__init__(master, padding=4)
        self._item = item
        self._size = size
        self._photos: dict[Path, ImageTk.PhotoImage] = {}
        self._placeholder: ImageTk.PhotoImage | None = None
        self._loaded = False

        self._image = ttk.Label(self, compound="top", text=item.name, justify="center")
        if item.is_featured:
            self._image.configure(font=("TkDefaultFont", 10, "bold"))
        self._image.pack()
        self.bind("<Map>", self._on_map)

    def _on_map(self, _event: object) -> None:
        if self._loaded:
            return
        self._loaded = True
        self._image.configure(image=self._photo_for(self._item.image_path))

    def _photo_for(self, path: Path | None) -> ImageTk.PhotoImage:
        if path is None:
            return self._placeholder_photo()
        cached = self._photos.get(path)
        if cached is not None:
            return cached
        try:
            with Image.open(path) as image:
                photo = ImageTk.PhotoImage(image.convert("RGB").resize(self._size))
        except OSError:
            photo = self._placeholder_photo()
        self._photos[path] = photo
        return photo

    def _placeholder_photo(self) -> ImageTk.PhotoImage:
        if self._placeholder is None:
            self._placeholder = ImageTk.PhotoImage(Image.new("RGB", self._size, _PLACEHOLDER_COLOR))
        return self._placeholder
