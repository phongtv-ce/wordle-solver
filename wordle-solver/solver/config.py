from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ENV_FILE = PROJECT_ROOT / ".env"
DEFAULT_DICTIONARY_PATH = PROJECT_ROOT.parent / "data" / "words_alpha.txt"
ALGORITHMS = ("candidates", "brute_force", "llm")
PUZZLE_MODES = ("daily", "random")


@dataclass(frozen=True)
class AppConfig:
    api_base: str
    api_entrypoint: str
    api_timeout_seconds: float
    size_begin: int
    size_end: int
    seed_begin: int | None
    seed_end: int | None
    mode: str
    algorithm: str
    dictionary_path: Path
    max_guesses: int

    def sizes(self) -> range:
        return range(self.size_begin, self.size_end + 1)

    def seeds(self) -> tuple[int | None, ...]:
        if self.seed_begin is None:
            return (None,)
        return tuple(range(self.seed_begin, self.seed_end + 1))


def load_config(*, env_file: str | Path | None = None) -> AppConfig:
    path = Path(env_file) if env_file is not None else DEFAULT_ENV_FILE
    if path.exists():
        load_dotenv(path, override=False)

    from solver.api import derive_api_base

    entrypoint = _require("WORDLE_API_ENTRYPOINT").rstrip("/")
    api_base = os.getenv("WORDLE_API_BASE", "").strip() or derive_api_base(entrypoint)
    algorithm = os.getenv("WORDLE_ALGORITHM", "candidates").strip().lower().replace("-", "_")
    if algorithm not in ALGORITHMS:
        raise ValueError(f"unknown WORDLE_ALGORITHM {algorithm!r}; choose from {ALGORITHMS}")

    dictionary_raw = os.getenv("WORDLE_DICTIONARY_PATH", str(DEFAULT_DICTIONARY_PATH))
    size_begin = _int_env("WORDLE_SIZE_BEGIN", 5)
    size_end = _int_env("WORDLE_SIZE_END", size_begin)
    if size_begin > size_end:
        raise ValueError(
            f"WORDLE_SIZE_BEGIN ({size_begin}) must be <= WORDLE_SIZE_END ({size_end})"
        )

    seed_begin = _optional_int_env("WORDLE_SEED_BEGIN")
    seed_end = _optional_int_env("WORDLE_SEED_END")
    if (seed_begin is None) != (seed_end is None):
        raise ValueError(
            "WORDLE_SEED_BEGIN and WORDLE_SEED_END must both be set or both omitted"
        )
    if seed_begin is not None and seed_begin > seed_end:
        raise ValueError(
            f"WORDLE_SEED_BEGIN ({seed_begin}) must be <= WORDLE_SEED_END ({seed_end})"
        )

    mode = os.getenv("WORDLE_MODE", "daily").strip().lower()
    if mode not in PUZZLE_MODES:
        raise ValueError(f"unknown WORDLE_MODE {mode!r}; choose from {PUZZLE_MODES}")

    return AppConfig(
        api_base=api_base.rstrip("/"),
        api_entrypoint=entrypoint,
        api_timeout_seconds=_float_env("WORDLE_API_TIMEOUT_SECONDS", 10.0),
        size_begin=size_begin,
        size_end=size_end,
        seed_begin=seed_begin,
        seed_end=seed_end,
        mode=mode,
        algorithm=algorithm,
        dictionary_path=_resolve_path(dictionary_raw),
        max_guesses=_int_env("WORDLE_MAX_GUESSES", 50),
    )


def _require(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"missing required env var {name}")
    return value


def _optional_int_env(name: str) -> int | None:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return None
    return int(raw)


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
