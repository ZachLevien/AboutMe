# CLAUDE.md

Guidance for Claude Code when working in the **gmail-bulk-delete** repository.

## What this is

A command-line utility that bulk-deletes old Gmail messages by date (default:
older than 2 years), while **always preserving** mail that is **starred**,
marked **important**, or carrying **any custom/user label**.

Safety-first by design: it is a **dry run** unless `--execute` is passed, and it
**moves to Trash** (recoverable ~30 days) unless `--permanent` is given.

## Project layout

```
gmail_bulk_delete/
  __init__.py     # version
  filters.py      # PURE logic: duration parsing, cutoff dates, query building, keep/delete rules
  auth.py         # OAuth2 flow + Gmail service construction (scopes, token cache)
  client.py       # GmailClient: list ids, batch label lookup, trash / permanent delete
  cli.py          # argparse entry point; ties everything together
tests/
  test_filters.py # unit tests for the pure logic (no network)
pyproject.toml    # packaging + console script `gmail-bulk-delete`
requirements.txt
```

## Architecture / data flow

1. `cli.py` resolves the cutoff date (`--older-than` or `--before`) and builds a
   Gmail search query via `filters.build_query`.
2. `auth.get_service` returns an authorized Gmail API client (scope depends on
   `--permanent`).
3. `client.GmailClient.iter_message_ids` pages through all matching message ids.
4. Unless `--no-verify`, `client.partition_deletable` re-fetches each message's
   labels and applies `filters.should_delete` as a **client-side safety net**.
5. Survivors are trashed (`batchModify` adding `TRASH`) or permanently deleted
   (`batchDelete`), 1000 ids per batch.

**Two-layer keep rule** is the core safety invariant: starred / important /
user-labelled mail is excluded *both* by the search query
(`-is:starred -is:important -has:userlabels`) *and* by the per-message re-check.
Don't remove either layer without good reason.

## Key design decisions

- **Pure logic lives in `filters.py`** so it's testable without network/auth.
  Keep new date/query/keep logic there and unit-test it.
- **Trash by default, permanent only on request.** `--permanent` needs the
  broad `https://mail.google.com/` scope; trashing needs only `gmail.modify`.
  Changing scope invalidates the cached token (handled in `auth.get_service`).
- **Dry run by default.** Any change to deletion behavior must preserve the
  "nothing happens without `--execute`" guarantee.
- **Month/year date math clamps** to the last valid day (see
  `filters._shift_months`); don't swap in naive `timedelta` for those units.

## Commands

```bash
# Setup
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Tests (fast, no network)
pytest

# Run (dry run by default)
gmail-bulk-delete --older-than 2y
gmail-bulk-delete --older-than 2y --execute
python -m gmail_bulk_delete.cli --help
```

Requires `credentials.json` (OAuth desktop client) in the working dir; see
README for how to create it. `credentials.json` and `token.json` are gitignored
and must **never** be committed.

## Conventions

- Python 3.9+, type hints, `from __future__ import annotations`.
- Stdlib-only for core logic (`argparse`, not click); Google libs only in
  `auth.py` / `client.py`.
- Keep CLI output terse and explicit about what will/did happen.

## When making changes

- Run `pytest` before committing.
- If you touch filtering, query building, or date math, add/adjust tests in
  `tests/test_filters.py`.
- Be conservative with anything that deletes: prefer additional confirmation or
  dry-run visibility over silent broader deletion.
