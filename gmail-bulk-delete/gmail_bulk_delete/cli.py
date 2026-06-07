"""Command-line entry point for gmail-bulk-delete."""

from __future__ import annotations

import argparse
import sys
from datetime import date, datetime

from . import __version__
from .auth import SCOPE_PERMANENT, SCOPE_TRASH, get_service
from .client import GmailClient
from .filters import (
    build_query,
    cutoff_date,
    describe_duration,
    parse_duration,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gmail-bulk-delete",
        description=(
            "Bulk-delete old Gmail messages by date. Messages that are "
            "starred, marked important, or carry any custom label are always "
            "kept. Runs as a dry-run unless --execute is given."
        ),
    )
    parser.add_argument("--version", action="version", version=__version__)

    when = parser.add_mutually_exclusive_group()
    when.add_argument(
        "--older-than",
        default="2y",
        metavar="DURATION",
        help="delete mail older than this (e.g. 2y, 18m, 6w, 90d). Default: 2y.",
    )
    when.add_argument(
        "--before",
        metavar="YYYY-MM-DD",
        help="delete mail received strictly before this date (overrides --older-than).",
    )

    parser.add_argument(
        "--query",
        default=None,
        help="extra Gmail search terms to AND with the date filter "
        "(e.g. 'from:newsletters@example.com').",
    )
    parser.add_argument(
        "--include-spam-trash",
        action="store_true",
        help="also consider messages already in Spam/Trash.",
    )
    parser.add_argument(
        "--max",
        type=int,
        default=None,
        metavar="N",
        help="cap the number of candidate messages processed.",
    )

    parser.add_argument(
        "--permanent",
        action="store_true",
        help="permanently delete instead of moving to Trash (IRREVERSIBLE; "
        "requires broader OAuth scope).",
    )
    parser.add_argument(
        "--no-verify",
        action="store_true",
        help="skip the per-message label re-check before deleting (faster, "
        "trusts the search query alone).",
    )

    parser.add_argument(
        "--execute",
        action="store_true",
        help="actually delete. Without this the tool only reports what it would do.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="skip the interactive confirmation prompt (use with --execute).",
    )

    parser.add_argument(
        "--credentials",
        default="credentials.json",
        help="path to the OAuth client secrets file. Default: credentials.json.",
    )
    parser.add_argument(
        "--token",
        default="token.json",
        help="path to store/read the OAuth token. Default: token.json.",
    )
    return parser


def _resolve_cutoff(args, today: date) -> date:
    if args.before:
        try:
            return datetime.strptime(args.before, "%Y-%m-%d").date()
        except ValueError as exc:
            raise SystemExit(f"error: --before must be YYYY-MM-DD ({exc})")
    amount, unit = parse_duration(args.older_than)
    return cutoff_date(today, amount, unit)


def _progress(label: str):
    def _cb(done: int, total: int) -> None:
        print(f"\r  {label}: {done}/{total}", end="", flush=True)
        if done >= total:
            print()

    return _cb


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    today = date.today()
    try:
        before = _resolve_cutoff(args, today)
    except (ValueError, SystemExit) as exc:
        print(exc, file=sys.stderr)
        return 2

    query = build_query(
        before,
        extra_query=args.query,
        include_spam_trash=args.include_spam_trash,
    )

    mode = "PERMANENTLY DELETE" if args.permanent else "move to Trash"
    print(f"gmail-bulk-delete {__version__}")
    if args.before:
        print(f"Cutoff:  messages before {before:%Y-%m-%d}")
    else:
        amount, unit = parse_duration(args.older_than)
        print(
            f"Cutoff:  older than {describe_duration(amount, unit)} "
            f"(before {before:%Y-%m-%d})"
        )
    print(f"Action:  {mode}")
    print("Keeping: starred, important, and any custom-labelled mail")
    print(f"Query:   {query}\n")

    scopes = [SCOPE_PERMANENT] if args.permanent else [SCOPE_TRASH]
    try:
        service = get_service(args.credentials, args.token, scopes)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    client = GmailClient(service)

    print("Finding candidate messages...")
    candidate_ids = list(
        client.iter_message_ids(
            query,
            include_spam_trash=args.include_spam_trash,
            limit=args.max,
        )
    )
    print(f"  {len(candidate_ids)} candidate(s) matched the search.\n")

    if not candidate_ids:
        print("Nothing to do.")
        return 0

    if args.no_verify:
        deletable, kept = candidate_ids, []
    else:
        user_labels = client.user_label_ids()
        print("Verifying labels (safety re-check)...")
        deletable, kept = client.partition_deletable(
            candidate_ids, user_labels, on_progress=_progress("checked")
        )
        if kept:
            print(f"  {len(kept)} message(s) kept after re-check.")

    print(f"\n{len(deletable)} message(s) eligible to {mode}.")

    if not deletable:
        print("Nothing to delete.")
        return 0

    if not args.execute:
        print("\nDRY RUN — nothing was changed. Re-run with --execute to apply.")
        return 0

    if not args.yes:
        verb = "PERMANENTLY DELETE" if args.permanent else "move to Trash"
        answer = input(f"\n{verb} {len(deletable)} message(s)? Type 'yes' to confirm: ")
        if answer.strip().lower() != "yes":
            print("Aborted.")
            return 1

    print()
    action = client.delete_forever if args.permanent else client.trash
    count = action(deletable, on_progress=_progress("deleted"))

    done_word = "permanently deleted" if args.permanent else "moved to Trash"
    print(f"\nDone: {count} message(s) {done_word}.")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
