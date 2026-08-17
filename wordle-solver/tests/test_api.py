import json
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlparse

import pytest

from solver.api import WordleApiError, WordleClient, derive_api_base
from tests.helpers import GUESS_API_RAW, make_config


def test_client_gets_guess_with_size_and_guess_query_params():
    captured: dict[str, object] = {}

    def http_get(url, headers, timeout):
        captured["url"] = url
        captured["headers"] = headers
        captured["timeout"] = timeout
        return json.dumps(GUESS_API_RAW).encode("utf-8")

    client = WordleClient(make_config(), http_get=http_get)
    result = client.guess("GUESS")

    assert result == GUESS_API_RAW
    parsed = urlparse(captured["url"])
    query = parse_qs(parsed.query)
    assert parsed.scheme == "https"
    assert parsed.netloc == "api.example.test"
    assert parsed.path == "/daily"
    assert query["guess"] == ["guess"]
    assert query["size"] == ["5"]
    assert captured["headers"] == {"Accept": "application/json"}
    assert captured["timeout"] == 5.0


def test_client_merges_query_params_with_existing_entrypoint_query():
    captured: dict[str, object] = {}

    def http_get(url, headers, timeout):
        captured["url"] = url
        return b"[]"

    client = WordleClient(
        make_config(api_base="https://api.example.test?foo=bar"),
        http_get=http_get,
    )
    client.guess("crane")

    query = parse_qs(urlparse(captured["url"]).query)
    assert query["foo"] == ["bar"]
    assert query["guess"] == ["crane"]
    assert query["size"] == ["5"]


def test_client_rejects_guess_when_length_does_not_match_size():
    client = WordleClient(make_config(size_begin=5, size_end=5), http_get=lambda *args: b"[]")
    with pytest.raises(ValueError, match="guess length 4 does not match size 5"):
        client.guess("abcd")


def test_client_wraps_http_error_as_wordle_api_error():
    def http_get(url, headers, timeout):
        raise HTTPError(url, 503, "unavailable", hdrs=None, fp=None)

    client = WordleClient(make_config(), http_get=http_get)
    with pytest.raises(WordleApiError, match="guess request failed"):
        client.guess("crane")


def test_client_rejects_invalid_utf8_body():
    def http_get(url, headers, timeout):
        return b"\xff\xfe"

    client = WordleClient(make_config(), http_get=http_get)
    with pytest.raises(WordleApiError, match="not valid JSON"):
        client.guess("crane")


def test_client_rejects_non_list_json():
    def http_get(url, headers, timeout):
        return b'{"error": "nope"}'

    client = WordleClient(make_config(), http_get=http_get)
    with pytest.raises(WordleApiError):
        client.guess("crane")


def test_client_random_uses_random_endpoint_and_seed():
    captured: dict[str, object] = {}

    def http_get(url, headers, timeout):
        captured["url"] = url
        return json.dumps(GUESS_API_RAW).encode("utf-8")

    client = WordleClient(
        make_config(api_base="https://wordle.votee.dev:8000"),
        http_get=http_get,
    )
    client.guess("crane", size=5, puzzle="random", seed=42)

    parsed = urlparse(captured["url"])
    query = parse_qs(parsed.query)
    assert parsed.path == "/random"
    assert query["guess"] == ["crane"]
    assert query["size"] == ["5"]
    assert query["seed"] == ["42"]


def test_client_random_omits_seed_when_not_set():
    captured: dict[str, object] = {}

    def http_get(url, headers, timeout):
        captured["url"] = url
        return b"[]"

    client = WordleClient(
        make_config(api_base="https://wordle.votee.dev:8000"),
        http_get=http_get,
    )
    client.guess("crane", puzzle="random")

    query = parse_qs(urlparse(captured["url"]).query)
    assert "seed" not in query


def test_derive_api_base_strips_daily_suffix():
    assert derive_api_base("https://wordle.votee.dev:8000/daily") == (
        "https://wordle.votee.dev:8000"
    )


def test_derive_api_base_strips_random_suffix():
    assert derive_api_base("https://wordle.votee.dev:8000/random") == (
        "https://wordle.votee.dev:8000"
    )
