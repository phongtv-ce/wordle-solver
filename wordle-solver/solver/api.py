from __future__ import annotations

import json
from collections.abc import Callable, Mapping, Sequence
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse
from urllib.request import Request, urlopen

from solver.config import AppConfig

JsonObject = Mapping[str, object]
HttpGet = Callable[[str, dict[str, str], float], bytes]


class WordleApiError(RuntimeError):
    pass


class WordleClient:
    def __init__(self, config: AppConfig, *, http_get: HttpGet | None = None) -> None:
        self._config = config
        self._http_get = http_get or _urllib_get

    def guess(self, word: str) -> Sequence[JsonObject]:
        guess = word.lower()
        size = self._config.word_length
        if len(guess) != size:
            raise ValueError(
                f"guess length {len(guess)} does not match size {size}"
            )

        url = _url_with_query(
            self._config.api_entrypoint,
            {"guess": guess, "size": size},
        )
        headers = {"Accept": "application/json"}
        if self._config.api_key:
            headers["Authorization"] = f"Bearer {self._config.api_key}"

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
