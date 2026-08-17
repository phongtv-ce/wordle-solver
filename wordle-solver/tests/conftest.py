import os

import pytest

_WORDLE_PREFIX = "WORDLE_"


@pytest.fixture(autouse=True)
def isolate_wordle_env(monkeypatch):
    for key in list(os.environ):
        if key.startswith(_WORDLE_PREFIX):
            monkeypatch.delenv(key, raising=False)
