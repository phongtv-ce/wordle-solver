from __future__ import annotations

import json
from collections.abc import Callable, Mapping, Sequence
from typing import Literal
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse
from urllib.request import Request, urlopen

from solver.config import AppConfig

JsonObject = Mapping[str, object]
HttpGet = Callable[[str, dict[str, str], float], bytes]
PuzzleMode = Literal["daily", "random"]


class WordleApiError(RuntimeError):
    pass


def derive_api_base(entrypoint: str) -> str:
    """Strip a known puzzle path suffix to get the API base URL."""
    url = entrypoint.rstrip("/")
    for suffix in ("/daily", "/random"):
        if url.endswith(suffix):
            return url[: -len(suffix)]
    return url


def endpoint_for_puzzle(entrypoint: str, api_base: str, puzzle: PuzzleMode) -> str:
    daily_url = entrypoint.rstrip("/")
    if puzzle == "daily":
        if daily_url.endswith("/daily"):
            return daily_url
        return daily_url
    return f"{api_base.rstrip('/')}/random"


class WordleClient:
    def __init__(self, config: AppConfig, *, http_get: HttpGet | None = None) -> None:
        self._config = config
        self._http_get = http_get or _urllib_get

    def guess(
        self,
        word: str,
        *,
        size: int | None = None,
        puzzle: PuzzleMode = "daily",
        seed: int | None = None,
    ) -> Sequence[JsonObject]:
        guess = word.lower()
        effective_size = size if size is not None else self._config.size_begin
        if len(guess) != effective_size:
            raise ValueError(
                f"guess length {len(guess)} does not match size {effective_size}"
            )

        endpoint = endpoint_for_puzzle(
            self._config.api_entrypoint,
            self._config.api_base,
            puzzle,
        )
        params: dict[str, object] = {"guess": guess, "size": effective_size}
        if puzzle == "random" and seed is not None:
            params["seed"] = seed

        url = _url_with_query(endpoint, params)
        headers = {"Accept": "application/json"}

        try:
            body = self._http_get(
                url,
                headers,
                self._config.api_timeout_seconds,
            )
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            raise WordleApiError(f"guess request failed: {exc}") from exc

        try:
            parsed = json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise WordleApiError("guess response is not valid JSON") from exc

        if not isinstance(parsed, list):
            raise WordleApiError("guess response must be a JSON list of slot results")
        return parsed


def _url_with_query(url: str, params: Mapping[str, object]) -> str:
    parsed = urlparse(url)
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    query.update({key: str(value) for key, value in params.items()})
    return urlunparse(parsed._replace(query=urlencode(query)))


def _urllib_get(url: str, headers: dict[str, str], timeout: float) -> bytes:
    request = Request(url, headers=headers, method="GET")
    with urlopen(request, timeout=timeout) as response:
        return response.read()
