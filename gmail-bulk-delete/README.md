# gmail-bulk-delete

A small command-line utility to **bulk-delete old Gmail messages by date**, while
**always keeping** messages that are:

- **starred**,
- marked **important**, or
- carrying **any custom (user-created) label**.

By default it moves matching mail to **Trash** (recoverable for ~30 days) and runs
as a **dry run** — it shows you exactly what it would do and changes nothing until
you pass `--execute`.

---

## How it works

1. Builds a Gmail search like
   `before:YYYY/MM/DD -is:starred -is:important -has:userlabels` so the server
   filters out anything you want to keep.
2. Re-checks every candidate message's labels client-side as a safety net
   (disable with `--no-verify`).
3. Moves the survivors to Trash, or — with `--permanent` — deletes them for good.

---

## Setup

### 1. Install

```bash
cd gmail-bulk-delete
python -m venv .venv && source .venv/bin/activate
pip install -e .
# or, without installing the console script:
pip install -r requirements.txt
```

### 2. Create Gmail API OAuth credentials

1. Go to the [Google Cloud Console](https://console.cloud.google.com/), create (or
   pick) a project.
2. **APIs & Services → Library →** enable the **Gmail API**.
3. **APIs & Services → OAuth consent screen →** configure it (User type *External*
   is fine; add your own address as a *Test user*).
4. **APIs & Services → Credentials → Create Credentials → OAuth client ID →**
   Application type **Desktop app**.
5. Download the JSON and save it as `credentials.json` in this folder.

The first run opens a browser to authorize access; the resulting token is cached in
`token.json`. **Neither file is committed** (see `.gitignore`).

---

## Usage

Dry run — delete mail older than 2 years (the default):

```bash
gmail-bulk-delete
# or: python -m gmail_bulk_delete.cli
```

Actually move it to Trash:

```bash
gmail-bulk-delete --execute
```

More examples:

```bash
# Older than 18 months instead of 2 years
gmail-bulk-delete --older-than 18m --execute

# Everything before a specific date
gmail-bulk-delete --before 2022-01-01 --execute

# Only old newsletters from one sender
gmail-bulk-delete --older-than 1y --query "from:newsletters@example.com" --execute

# Permanently delete (irreversible — needs broader OAuth scope) and skip the prompt
gmail-bulk-delete --older-than 3y --permanent --execute --yes
```

### Options

| Flag | Description |
| --- | --- |
| `--older-than DURATION` | Delete mail older than this (`2y`, `18m`, `6w`, `90d`). Default `2y`. |
| `--before YYYY-MM-DD` | Delete mail before a specific date (overrides `--older-than`). |
| `--query "..."` | Extra Gmail search terms ANDed with the date filter. |
| `--include-spam-trash` | Also consider mail already in Spam/Trash. |
| `--max N` | Process at most N candidate messages. |
| `--permanent` | Permanently delete instead of trashing (**irreversible**). |
| `--no-verify` | Skip the per-message label re-check (faster, trusts the search). |
| `--execute` | Actually apply changes (otherwise it's a dry run). |
| `--yes` | Skip the interactive confirmation prompt. |
| `--credentials PATH` | OAuth client secrets file (default `credentials.json`). |
| `--token PATH` | Token cache file (default `token.json`). |

---

## Safety notes

- **Dry run by default.** Nothing is deleted unless you pass `--execute`.
- **Trash by default.** Trashed mail is recoverable in Gmail for ~30 days. Only
  `--permanent` is irreversible.
- **Two-layer keep rule.** Starred / important / user-labelled mail is excluded both
  by the search query and the client-side re-check.
- Start small with `--max 50` to confirm behavior on your account.

---

## Development

```bash
pip install -e ".[dev]"
pytest
```

The date math, query building, and keep/delete rules live in
`gmail_bulk_delete/filters.py` and are covered by `tests/test_filters.py` (no network
required).

## License

MIT — see [LICENSE](LICENSE).
