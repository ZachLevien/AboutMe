"""Unit tests for the pure filtering/date logic."""

from datetime import date

import pytest

from gmail_bulk_delete.filters import (
    build_query,
    cutoff_date,
    describe_duration,
    is_user_label,
    parse_duration,
    should_delete,
    subtract_period,
)


@pytest.mark.parametrize(
    "text,expected",
    [
        ("2y", (2, "y")),
        ("18m", (18, "m")),
        ("6w", (6, "w")),
        ("90d", (90, "d")),
        ("  3Y ", (3, "y")),
    ],
)
def test_parse_duration_ok(text, expected):
    assert parse_duration(text) == expected


@pytest.mark.parametrize("text", ["", "abc", "2", "y", "0d", "-1y", "2yy", "1.5y"])
def test_parse_duration_bad(text):
    with pytest.raises(ValueError):
        parse_duration(text)


def test_subtract_days_and_weeks():
    assert subtract_period(date(2026, 6, 7), 90, "d") == date(2026, 3, 9)
    assert subtract_period(date(2026, 6, 7), 1, "w") == date(2026, 5, 31)


def test_subtract_years_simple():
    assert subtract_period(date(2026, 6, 7), 2, "y") == date(2024, 6, 7)


def test_subtract_months_with_clamp():
    # Mar 31 minus 1 month -> Feb 28 (2026 not a leap year).
    assert subtract_period(date(2026, 3, 31), 1, "m") == date(2026, 2, 28)


def test_subtract_year_leap_day_clamp():
    # Feb 29 2024 minus 1 year -> Feb 28 2023.
    assert subtract_period(date(2024, 2, 29), 1, "y") == date(2023, 2, 28)


def test_cutoff_date():
    assert cutoff_date(date(2026, 6, 7), 2, "y") == date(2024, 6, 7)


def test_describe_duration():
    assert describe_duration(1, "y") == "1 year"
    assert describe_duration(2, "y") == "2 years"
    assert describe_duration(18, "m") == "18 months"


def test_build_query_default():
    q = build_query(date(2024, 6, 7))
    assert "before:2024/06/07" in q
    assert "-is:starred" in q
    assert "-is:important" in q
    assert "-has:userlabels" in q
    assert "-in:spam" in q
    assert "-in:trash" in q


def test_build_query_with_extra_and_spamtrash():
    q = build_query(
        date(2024, 1, 1),
        extra_query="from:foo@example.com",
        include_spam_trash=True,
    )
    assert "(from:foo@example.com)" in q
    assert "-in:spam" not in q
    assert "-in:trash" not in q


@pytest.mark.parametrize(
    "labels,expected",
    [
        (["INBOX", "UNREAD"], True),
        (["INBOX"], True),
        ([], True),
        (None, True),
        (["INBOX", "STARRED"], False),
        (["IMPORTANT"], False),
        (["INBOX", "Label_42"], False),  # user label id
    ],
)
def test_should_delete(labels, expected):
    user_labels = {"Label_42", "Label_7"}
    assert should_delete(labels, user_labels) is expected


@pytest.mark.parametrize(
    "label,expected",
    [
        ({"id": "Label_1", "type": "user", "name": "Receipts"}, True),
        ({"id": "INBOX", "type": "system"}, False),
        ({"id": "CATEGORY_PROMOTIONS", "type": "system"}, False),
        ({"id": "IMPORTANT", "type": "system"}, False),
        # Defensive: a system id mislabelled as "user" is still not a tag.
        ({"id": "STARRED", "type": "user"}, False),
    ],
)
def test_is_user_label(label, expected):
    assert is_user_label(label) is expected
