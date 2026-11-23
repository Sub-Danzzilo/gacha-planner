from __future__ import annotations

import re
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

from core.models.currency import Money

_THOUSANDS = re.compile(r"\d{1,3}(?:,\d{3})+")


class InputError(ValueError):
    """Invalid input text; the message is ready to be shown to the user."""


def describe_error(exc: BaseException) -> str:
    """A message that can be displayed directly, including for KeyError wrapping text."""
    if isinstance(exc, KeyError) and exc.args:
        return str(exc.args[0])
    return str(exc)


def parse_percent(text: str) -> float:
    """A percentage with a comma or dot decimal separator, e.g. "1.3" or "1,3", becomes 0.013."""
    cleaned = text.strip().replace("%", "").replace(" ", "")
    if not cleaned:
        raise InputError("Percentage cannot be empty")
    if cleaned.count(",") > 1 or cleaned.count(".") > 1:
        raise InputError(f"Invalid percentage: {text!r}")
    normalized = cleaned.replace(",", ".")
    try:
        value = Decimal(normalized)
    except InvalidOperation as exc:
        raise InputError(f"Invalid percentage: {text!r}") from exc
    if not value.is_finite():
        raise InputError(f"Invalid percentage: {text!r}")
    if value < 0 or value > 100:
        raise InputError("Percentage must be between 0 and 100")
    return float(value / Decimal(100))


def parse_decimal(text: str) -> Decimal:
    """Non-negative amount: "." marks decimals and "," groups thousands in threes.

    Accepted: "16000", "16,000.50", "1.3". Rejected as invalid or ambiguous: "16.000,50",
    "1,3", "1.2.3".
    """
    cleaned = text.strip().replace(" ", "")
    if not cleaned:
        raise InputError("Amount cannot be empty")
    if cleaned[0] in "+-":
        raise InputError("Amount cannot be negative")

    if "." in cleaned:
        whole, _, fraction = cleaned.partition(".")
        if "." in fraction:
            raise InputError(f"Invalid amount: {text!r} (more than one decimal point)")
        if "," in whole and not _THOUSANDS.fullmatch(whole):
            raise InputError(f"Invalid thousands grouping: {text!r}")
        digits = whole.replace(",", "")
        if not digits.isdigit() or (fraction and not fraction.isdigit()):
            raise InputError(f"Invalid amount: {text!r}")
        return Decimal(f"{digits}.{fraction or '0'}")

    if "," in cleaned:
        if not _THOUSANDS.fullmatch(cleaned):
            raise InputError(f"Ambiguous amount: {text!r}. Use '.' for decimals.")
        return Decimal(cleaned.replace(",", ""))

    if not cleaned.isdigit():
        raise InputError(f"Invalid amount: {text!r}")
    return Decimal(cleaned)


def parse_positive_int(text: str) -> int:
    value = parse_non_negative_int(text)
    if value == 0:
        raise InputError("Number must be greater than 0")
    return value


def parse_non_negative_int(text: str) -> int:
    cleaned = text.strip().replace(" ", "")
    if not cleaned:
        raise InputError("Number cannot be empty")
    if "," in cleaned:
        if not _THOUSANDS.fullmatch(cleaned):
            raise InputError(f"Invalid number: {text!r}")
        cleaned = cleaned.replace(",", "")
    if not cleaned.isdigit():
        raise InputError(f"Invalid number: {text!r}")
    return int(cleaned)


def format_percent(value: float) -> str:
    return f"{value * 100:.2f}%"


def format_money(money: Money) -> str:
    decimals = money.currency.decimals
    quantized = money.amount.quantize(Decimal(1).scaleb(-decimals), rounding=ROUND_HALF_UP)
    return f"{quantized:,.{decimals}f} {money.currency.code}"
