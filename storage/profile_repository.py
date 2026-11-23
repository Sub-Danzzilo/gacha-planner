from __future__ import annotations

import json
import os
import re
import tempfile
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from core.errors import StorageError
from core.models.profile import GameProfile
from storage.serializers import ProfileSerializer

_NAME_PATTERN = re.compile(r"[A-Za-z0-9_-]{1,64}")


class ProfileRepository:
    """Stores one profile per JSON file inside a single directory."""

    def __init__(self, directory: Path, serializer: ProfileSerializer) -> None:
        self._directory = directory
        self._serializer = serializer

    def list_profiles(self) -> list[str]:
        if not self._directory.is_dir():
            return []
        return sorted(path.stem for path in self._directory.glob("*.json"))

    def load(self, name: str) -> GameProfile:
        path = self._path(name)
        try:
            raw = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise StorageError(f"Profile {name!r} could not be read: {exc}") from exc
        try:
            data: Any = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise StorageError(f"Profile {name!r} is not valid JSON: {exc}") from exc
        if not isinstance(data, Mapping):
            raise StorageError(f"Profile {name!r} must be a JSON object")
        return self._serializer.from_dict(data)

    def save(self, profile: GameProfile) -> None:
        path = self._path(profile.name)
        try:
            text = json.dumps(self._serializer.to_dict(profile), ensure_ascii=False, indent=2)
        except (TypeError, ValueError) as exc:
            raise StorageError(f"Profile {profile.name!r} could not be serialized: {exc}") from exc

        try:
            self._directory.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise StorageError(
                f"Profile directory {self._directory} could not be created: {exc}"
            ) from exc

        temporary: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                "w", encoding="utf-8", dir=self._directory, delete=False, suffix=".tmp"
            ) as handle:
                handle.write(text)
                handle.flush()
                os.fsync(handle.fileno())
                temporary = Path(handle.name)
            os.replace(temporary, path)
        except OSError as exc:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
            raise StorageError(f"Profile {profile.name!r} could not be saved: {exc}") from exc

    def delete(self, name: str) -> None:
        path = self._path(name)
        try:
            path.unlink()
        except OSError as exc:
            raise StorageError(f"Profile {name!r} could not be deleted: {exc}") from exc

    def exists(self, name: str) -> bool:
        return self._path(name).is_file()

    def _path(self, name: str) -> Path:
        if not _NAME_PATTERN.fullmatch(name):
            raise StorageError(
                f"Invalid profile name: {name!r} (only letters, digits, '-' and '_')"
            )
        return self._directory / f"{name}.json"
