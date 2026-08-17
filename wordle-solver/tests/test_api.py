import json
from urllib.parse import parse_qs, urlparse

import pytest

from solver.api import WordleApiError, WordleClient
from solver.config import AppConfig
from tests.helpers import GUESS_API_RAW


def _config(**overrides) -> AppConfig:
    values = {
        "api_entrypoint": "https://api.example.test/wordle",
        "api_key": None,
        "api_timeout_seconds": 5.0,
        "word_length": 5,
        "algorithm": "candidates",
        "dictionary_path": "/tmp/words.txt",
        "max_guesses": 50,
    }
    values.update(overrides)
    return AppConfig(**values)


def test_client_gets_guess_with_size_and_guess_query_params():
    captured: dict[str, object] = {}

    def http_get(url, headers, timeout):
        captured["url"] = url
        captured["headers"] = headers
        captured["timeout"] = timeout
        return json.dumps(GUESS_API_RAW).encode("utf-8")

    client = WordleClient(_config(api_key="token-1"), http_get=http_get)
    result = client.guess("GUESS")

    assert result == GUESS_API_RAW
    parsed = urlparse(captured["url"])
    query = parse_qs(parsed.query)
    assert parsed.scheme == "https"
    assert parsed.netloc == "api.example.test"
    assert parsed.path == "/wordle"
    assert query["guess"] == ["guess"]
    assert query["size"] == ["5"]
    assert captured["headers"]["Authorization"] == "Bearer token-1"
    assert captured["headers"]["Accept"] == "application/json"
    assert captured["timeout"] == 5.0


def test_client_rejects_guess_when_length_does_not_match_size():
    client = WordleClient(_config(word_length=5), http_get=lambda *args: b"[]")
    with pytest.raises(ValueError, match="guess length 4 does not match size 5"):
        client.guess("abcd")


def test_client_rejects_non_list_json():
    def http_get(url, headers, timeout):
        return b'{"error": "nope"}'

    client = WordleClient(_config(), http_get=http_get)
    with pytest.raises(WordleApiError):
        client.guess("aaaaa")
