"""OAuth2 authentication and Gmail service construction."""

from __future__ import annotations

from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Trashing only needs gmail.modify. Permanent deletion (batchDelete) requires
# the broad mail.google.com scope.
SCOPE_TRASH = "https://www.googleapis.com/auth/gmail.modify"
SCOPE_PERMANENT = "https://mail.google.com/"


def get_service(
    credentials_path: str | Path,
    token_path: str | Path,
    scopes: list[str],
):
    """Return an authorized Gmail API service.

    Reuses ``token_path`` when it exists and still covers ``scopes``,
    refreshing silently when possible and otherwise launching the local
    OAuth consent flow.
    """
    credentials_path = Path(credentials_path)
    token_path = Path(token_path)

    creds: Credentials | None = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), scopes)
        if not creds.has_scopes(scopes):
            # Saved token lacks a now-required scope (e.g. switching to
            # permanent deletion). Force a fresh consent.
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not credentials_path.exists():
                raise FileNotFoundError(
                    f"OAuth client secrets not found at {credentials_path}. "
                    "See the README for how to create one."
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                str(credentials_path), scopes
            )
            creds = flow.run_local_server(port=0)
        token_path.write_text(creds.to_json())

    return build("gmail", "v1", credentials=creds, cache_discovery=False)
