"""Domain errors that have no exact standard-library counterpart."""


class GachaPlannerError(Exception):
    """Base class for gacha-planner domain errors."""


class MissingExchangeRateError(GachaPlannerError):
    """No manual exchange rate exists for the requested currency pair."""


class StorageError(GachaPlannerError):
    """A profile cannot be read, is corrupt, or uses an unsupported schema version."""
