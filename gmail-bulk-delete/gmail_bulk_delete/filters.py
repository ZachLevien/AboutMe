"""Pure helpers: duration parsing, cutoff dates, queries, keep/delete rules.

Everything here is side-effect free so it can be unit-tested without
touching the network or the Gmail API.
"""

from __future__ import annotations

import calendar
import re
from datetime import date

# Gmail system labels that mark a message as worth keeping.
PROTECTED_SYSTEM_LABELS: frozenset[str] = frozenset({"STARRED", "IMPORTANT"})

# System label ids that are never "user" labels even though the API reports
# type == "system". (Used when deciding what counts as a custom tag.)
_SYSTEM_LABEL_PREFIXES = ("CATEGORY_",)
_SYSTEM_LABEL_IDS: frozenset[str] = frozenset(
    {
        "INBOX",
        "SENT",
        "DRAFT",
        "SPAM",
        "TRASH",
        "UNREAD",
        "STARRED",
        "IMPORTANT",
        "CHAT",
    }
)

_DURATION_RE = re.compile(r"^\s*(\d+)\s*([dwmy])\s*$", re.IGNORECASE)

# Unit -> human label, for nice messages.
_UNIT_NAMES = {"d": "day", "w": "week", "m": "month", "y": "year"}


def parse_duration(text: str) -> tuple[int, str]:
    """Parse a duration like ``2y``, ``18m``, ``6w``, ``90d``.

    Returns a ``(amount, unit)`` tuple where unit is one of ``d w m y``.
    Raises ``ValueError`` for anything else.
    """
    match = _DURATION_RE.match(text or "")
    if not match:
        raise ValueError(
            f"invalid duration {text!r}; expected e.g. '2y', '18m', '6w', '90d'"
        )
    amount = int(match.group(1))
    unit = match.group(2).lower()
    if amount <= 0:
        raise ValueError("duration must be a positive number")
    return amount, unit


def subtract_period(start: date, amount: int, unit: str) -> date:
    """Return ``start`` minus ``amount`` units, using calendar-correct math.

    Day/week math is exact. Month/year math clamps to the last valid day of
    the target month (e.g. Mar 31 minus 1 month -> Feb 28/29).
    """
    if unit == "d":
        return _from_ordinal(start, -amount)
    if unit == "w":
        return _from_ordinal(start, -7 * amount)
    if unit == "m":
        return _shift_months(start, -amount)
    if unit == "y":
        return _shift_months(start, -12 * amount)
    raise ValueError(f"unknown unit {unit!r}")


def _from_ordinal(start: date, delta_days: int) -> date:
    return date.fromordinal(start.toordinal() + delta_days)


def _shift_months(start: date, delta_months: int) -> date:
    month_index = start.year * 12 + (start.month - 1) + delta_months
    year, month = divmod(month_index, 12)
    month += 1
    last_day = calendar.monthrange(year, month)[1]
    return date(year, month, min(start.day, last_day))


def cutoff_date(today: date, amount: int, unit: str) -> date:
    """Messages strictly *older* than the returned date are deletion candidates."""
    return subtract_period(today, amount, unit)


def describe_duration(amount: int, unit: str) -> str:
    name = _UNIT_NAMES[unit]
    plural = "" if amount == 1 else "s"
    return f"{amount} {name}{plural}"


def build_query(
    before: date,
    *,
    extra_query: str | None = None,
    include_spam_trash: bool = False,
) -> str:
    """Build the Gmail search query for deletion candidates.

    Excludes starred, important, and any user-labelled mail at the search
    layer so the server does the heavy lifting; client-side verification
    (see :func:`should_delete`) is still applied as a safety net.
    """
    parts = [
        f"before:{before:%Y/%m/%d}",
        "-is:starred",
        "-is:important",
        "-has:userlabels",
    ]
    if not include_spam_trash:
        parts += ["-in:spam", "-in:trash"]
    if extra_query:
        parts.append(f"({extra_query})")
    return " ".join(parts)


def should_delete(
    label_ids: list[str] | None,
    user_label_ids: set[str],
    protected_system_labels: frozenset[str] = PROTECTED_SYSTEM_LABELS,
) -> bool:
    """Return True only if a message is safe to delete.

    A message is kept (return False) when it is starred, important, or carries
    any user-created label.
    """
    labels = set(label_ids or [])
    if labels & protected_system_labels:
        return False
    if labels & user_label_ids:
        return False
    return True


def is_user_label(label: dict) -> bool:
    """Whether a Gmail label object represents a custom/user tag."""
    if label.get("type") != "user":
        return False
    label_id = label.get("id", "")
    if label_id in _SYSTEM_LABEL_IDS:
        return False
    if label_id.startswith(_SYSTEM_LABEL_PREFIXES):
        return False
    return True
