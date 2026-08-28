"""Short-lived Google runtime access tokens from the Cloud Run metadata identity."""

from __future__ import annotations

from dataclasses import dataclass
import json
import time
from typing import Callable, Mapping
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


_METADATA_TOKEN_URL = (
    "http://metadata.google.internal/computeMetadata/v1/"
    "instance/service-accounts/default/token"
)
_METADATA_HEADERS = {"Metadata-Flavor": "Google"}


class GoogleRuntimeAuthError(Exception):
    """Raised when the managed runtime cannot obtain a valid Google access token."""


@dataclass(frozen=True)
class _CachedAccessToken:
    token: str
    expires_at: float


class GoogleMetadataAccessTokenProvider:
    """Callable access-token provider using Cloud Run's attached service identity."""

    def __init__(
        self,
        *,
        clock: Callable[[], float] | None = None,
        fetch_json: Callable[[], Mapping[str, object]] | None = None,
        refresh_skew_seconds: int = 60,
    ) -> None:
        if (
            not isinstance(refresh_skew_seconds, int)
            or isinstance(refresh_skew_seconds, bool)
            or not 0 <= refresh_skew_seconds <= 300
        ):
            raise GoogleRuntimeAuthError(
                "refresh_skew_seconds must be an integer from 0 through 300"
            )
        self._clock = clock or time.time
        self._fetch_json = fetch_json or self._fetch_metadata_json
        self._refresh_skew_seconds = refresh_skew_seconds
        self._cached: _CachedAccessToken | None = None

    def __call__(self) -> str:
        now = self._clock_value()
        cached = self._cached
        if cached is not None and now < cached.expires_at - self._refresh_skew_seconds:
            return cached.token

        payload = self._fetch_json()
        if not isinstance(payload, Mapping):
            raise GoogleRuntimeAuthError("Google metadata token response is not an object")
        token = payload.get("access_token")
        expires_in = payload.get("expires_in")
        token_type = payload.get("token_type")
        if not isinstance(token, str) or not token.strip() or token != token.strip():
            raise GoogleRuntimeAuthError("Google metadata response has no valid access_token")
        if (
            not isinstance(expires_in, int)
            or isinstance(expires_in, bool)
            or expires_in <= 0
        ):
            raise GoogleRuntimeAuthError("Google metadata response has invalid expires_in")
        if not isinstance(token_type, str) or token_type.lower() != "bearer":
            raise GoogleRuntimeAuthError("Google metadata response has invalid token_type")

        self._cached = _CachedAccessToken(token=token, expires_at=now + expires_in)
        return token

    def _clock_value(self) -> float:
        value = self._clock()
        if not isinstance(value, (int, float)) or isinstance(value, bool) or value < 0:
            raise GoogleRuntimeAuthError("clock must return a non-negative numeric value")
        return float(value)

    @staticmethod
    def _fetch_metadata_json() -> Mapping[str, object]:
        request = Request(
            _METADATA_TOKEN_URL,
            headers=dict(_METADATA_HEADERS),
            method="GET",
        )
        try:
            with urlopen(request, timeout=3.0) as response:
                raw = response.read()
        except HTTPError as exc:
            raise GoogleRuntimeAuthError(
                f"Google metadata token HTTP failure: {exc.code}"
            ) from exc
        except (URLError, OSError) as exc:
            raise GoogleRuntimeAuthError("Google metadata token transport failure") from exc
        try:
            payload = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise GoogleRuntimeAuthError("Google metadata token response is invalid JSON") from exc
        if not isinstance(payload, Mapping):
            raise GoogleRuntimeAuthError("Google metadata token response is not an object")
        return payload
