# Reading and writing game profiles on disk. Phase 1.
#
# Class `ProfileRepository`:
#   - `__init__(self, directory: Path, serializer: ProfileSerializer)`
#   - `list_profiles(self) -> list[str]`            profile names found in the directory
#   - `load(self, name: str) -> GameProfile`
#   - `save(self, profile: GameProfile) -> None`
#   - `delete(self, name: str) -> None`
#   - `exists(self, name: str) -> bool`
#
# Rules:
#   - One JSON file per profile, named from a sanitized profile name (letters, digits, dash,
#     underscore). Reject names that would escape the directory.
#   - Write atomically: write to a temporary file in the same directory, then `os.replace`.
#   - Create the directory if it does not exist.
#   - Wrap `OSError` and `json.JSONDecodeError` in `StorageError`; keep the original exception
#     as the cause.
#   - UTF-8 with `ensure_ascii=False` and indentation of 2 so files are readable and diffable.
#   - Tests use `tmp_path`; never touch the real `data/profiles/` directory.
