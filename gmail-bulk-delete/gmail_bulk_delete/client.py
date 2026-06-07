"""Thin wrapper around the Gmail API for the operations we need."""

from __future__ import annotations

from typing import Callable, Iterator

from googleapiclient.errors import HttpError

from .filters import is_user_label, should_delete

# API limits.
_LIST_PAGE_SIZE = 500
_BATCH_MODIFY_MAX = 1000
_BATCH_DELETE_MAX = 1000
_GET_BATCH_SIZE = 100

_TRASH_LABEL = "TRASH"


class GmailClient:
    """Operations on a single authenticated mailbox (``me``)."""

    def __init__(self, service, user_id: str = "me") -> None:
        self._service = service
        self._user = user_id

    # -- labels ---------------------------------------------------------------

    def user_label_ids(self) -> set[str]:
        """Ids of all custom/user-created labels in the mailbox."""
        resp = self._service.users().labels().list(userId=self._user).execute()
        return {
            label["id"]
            for label in resp.get("labels", [])
            if is_user_label(label)
        }

    # -- listing --------------------------------------------------------------

    def iter_message_ids(
        self,
        query: str,
        *,
        include_spam_trash: bool = False,
        limit: int | None = None,
    ) -> Iterator[str]:
        """Yield message ids matching ``query``, paging through all results."""
        yielded = 0
        page_token: str | None = None
        messages = self._service.users().messages()
        while True:
            resp = messages.list(
                userId=self._user,
                q=query,
                pageToken=page_token,
                maxResults=_LIST_PAGE_SIZE,
                includeSpamTrash=include_spam_trash,
            ).execute()
            for msg in resp.get("messages", []):
                yield msg["id"]
                yielded += 1
                if limit is not None and yielded >= limit:
                    return
            page_token = resp.get("nextPageToken")
            if not page_token:
                return

    # -- verification ---------------------------------------------------------

    def partition_deletable(
        self,
        message_ids: list[str],
        user_label_ids: set[str],
        *,
        on_progress: Callable[[int, int], None] | None = None,
    ) -> tuple[list[str], list[str]]:
        """Fetch labels for each id and split into (deletable, kept).

        This is the client-side safety net: even if the search query let
        something through, anything starred/important/user-labelled is
        moved to the ``kept`` list here.
        """
        deletable: list[str] = []
        kept: list[str] = []
        total = len(message_ids)
        done = 0
        for start in range(0, total, _GET_BATCH_SIZE):
            chunk = message_ids[start : start + _GET_BATCH_SIZE]
            labels_by_id = self._fetch_labels(chunk)
            for msg_id in chunk:
                label_ids = labels_by_id.get(msg_id)
                if label_ids is None:
                    # Couldn't read it -> err on the side of keeping it.
                    kept.append(msg_id)
                elif should_delete(label_ids, user_label_ids):
                    deletable.append(msg_id)
                else:
                    kept.append(msg_id)
            done += len(chunk)
            if on_progress:
                on_progress(done, total)
        return deletable, kept

    def _fetch_labels(self, message_ids: list[str]) -> dict[str, list[str]]:
        """Batch-fetch labelIds for up to ``_GET_BATCH_SIZE`` messages."""
        result: dict[str, list[str]] = {}

        def _callback(request_id, response, exception):
            if exception is not None:
                return  # leave missing -> treated as "keep"
            result[response["id"]] = response.get("labelIds", [])

        batch = self._service.new_batch_http_request(callback=_callback)
        messages = self._service.users().messages()
        for msg_id in message_ids:
            batch.add(
                messages.get(userId=self._user, id=msg_id, format="minimal")
            )
        batch.execute()
        return result

    # -- deletion -------------------------------------------------------------

    def trash(
        self,
        message_ids: list[str],
        *,
        on_progress: Callable[[int, int], None] | None = None,
    ) -> int:
        """Move messages to Trash (auto-purged by Gmail after ~30 days)."""
        return self._batched(
            message_ids,
            _BATCH_MODIFY_MAX,
            self._trash_batch,
            on_progress=on_progress,
        )

    def delete_forever(
        self,
        message_ids: list[str],
        *,
        on_progress: Callable[[int, int], None] | None = None,
    ) -> int:
        """Permanently delete messages (irreversible; needs full scope)."""
        return self._batched(
            message_ids,
            _BATCH_DELETE_MAX,
            self._delete_batch,
            on_progress=on_progress,
        )

    def _trash_batch(self, chunk: list[str]) -> None:
        self._service.users().messages().batchModify(
            userId=self._user,
            body={"ids": chunk, "addLabelIds": [_TRASH_LABEL]},
        ).execute()

    def _delete_batch(self, chunk: list[str]) -> None:
        self._service.users().messages().batchDelete(
            userId=self._user, body={"ids": chunk}
        ).execute()

    def _batched(
        self,
        message_ids: list[str],
        size: int,
        action: Callable[[list[str]], None],
        *,
        on_progress: Callable[[int, int], None] | None = None,
    ) -> int:
        total = len(message_ids)
        done = 0
        for start in range(0, total, size):
            chunk = message_ids[start : start + size]
            try:
                action(chunk)
            except HttpError as exc:
                raise RuntimeError(
                    f"Gmail API error while deleting {len(chunk)} messages: {exc}"
                ) from exc
            done += len(chunk)
            if on_progress:
                on_progress(done, total)
        return done
