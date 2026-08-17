from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ENV_FILE = PROJECT_ROOT / ".env"
DEFAULT_DICTIONARY_PATH = PROJECT_ROOT.parent / "data" / "words_alpha.txt"
ALGORITHMS = ("candidates", "brute_force", "llm")


@dataclass(frozen=True)
class AppConfig:
    api_entrypoint: str
    api_key: str | None
    api_timeout_seconds: float
    word_length: int
    algorithm: str
    dictionary_path: Path
    max_guesses: int


def load_config(*, env_file: str | Path | None = None) -> AppConfig:
    path = Path(env_file) if env_file is not None else DEFAULT_ENV_FILE
    if path.exists():
        load_dotenv(path, override=False)

    entrypoint = _require("WORDLE_API_ENTRYPOINT").rstrip("/")
    api_key = os.getenv("WORDLE_API_KEY", "").strip() or None
    algorithm = os.getenv("WORDLE_ALGORITHM", "candidates").strip().lower().replace("-", "_")
    if algorithm not in ALGORITHMS:
        raise ValueError(f"unknown WORDLE_ALGORITHM {algorithm!r}; choose from {ALGORITHMS}")

    dictionary_raw = os.getenv("WORDLE_DICTIONARY_PATH", str(DEFAULT_DICTIONARY_PATH))
    return AppConfig(
        api_entrypoint=entrypoint,
        api_key=api_key,
        api_timeout_seconds=_float_env("WORDLE_API_TIMEOUT_SECONDS", 10.0),
        word_length=_int_env("WORDLE_WORD_LENGTH", 5),
        algorithm=algorithm,
        dictionary_path=_resolve_path(dictionary_raw),
        max_guesses=_int_env("WORDLE_MAX_GUESSES", 50),
    )


def _require(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"missing required env var {name}")
    return value


def _int_env(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    return int(raw)


def _float_env(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    return float(raw)


def _resolve_path(raw: str) -> Path:
    path = Path(raw).expanduser()
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path.resolve()
