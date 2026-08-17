from pathlib import Path

import pytest

from solver.config import load_config


def test_load_config_reads_api_entrypoint_from_env_file(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "WORDLE_API_ENTRYPOINT=https://api.example.test/wordle/",
                "WORDLE_SIZE_BEGIN=4",
                "WORDLE_SIZE_END=7",
                "WORDLE_ALGORITHM=brute_force",
                "WORDLE_DICTIONARY_PATH=words.txt",
                "WORDLE_MAX_GUESSES=12",
                "WORDLE_API_TIMEOUT_SECONDS=3.5",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.delenv("WORDLE_API_ENTRYPOINT", raising=False)
    monkeypatch.delenv("WORDLE_SIZE_BEGIN", raising=False)
    monkeypatch.delenv("WORDLE_SIZE_END", raising=False)
    monkeypatch.delenv("WORDLE_ALGORITHM", raising=False)
    monkeypatch.delenv("WORDLE_DICTIONARY_PATH", raising=False)
    monkeypatch.delenv("WORDLE_MAX_GUESSES", raising=False)
    monkeypatch.delenv("WORDLE_API_TIMEOUT_SECONDS", raising=False)

    config = load_config(env_file=env_file)

    assert config.api_entrypoint == "https://api.example.test/wordle"
    assert config.api_base == "https://api.example.test/wordle"
    assert config.size_begin == 4
    assert config.size_end == 7
    assert list(config.sizes()) == [4, 5, 6, 7]
    assert config.algorithm == "brute_force"
    assert config.dictionary_path == (Path(__file__).resolve().parents[1] / "words.txt").resolve()
    assert config.max_guesses == 12
    assert config.api_timeout_seconds == 3.5


def test_load_config_defaults_size_range_when_unset(tmp_path, monkeypatch):
    monkeypatch.delenv("WORDLE_SIZE_BEGIN", raising=False)
    monkeypatch.delenv("WORDLE_SIZE_END", raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text(
        "WORDLE_API_ENTRYPOINT=https://api.example.test/wordle\n",
        encoding="utf-8",
    )
    config = load_config(env_file=env_file)
    assert config.size_begin == 5
    assert config.size_end == 5
    assert list(config.sizes()) == [5]


def test_load_config_defaults_size_end_to_begin(tmp_path, monkeypatch):
    monkeypatch.delenv("WORDLE_SIZE_END", raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "WORDLE_API_ENTRYPOINT=https://api.example.test/wordle",
                "WORDLE_SIZE_BEGIN=7",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    config = load_config(env_file=env_file)
    assert config.size_begin == 7
    assert config.size_end == 7


def test_load_config_requires_api_entrypoint(tmp_path, monkeypatch):
    monkeypatch.delenv("WORDLE_API_ENTRYPOINT", raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text("", encoding="utf-8")
    with pytest.raises(ValueError, match="WORDLE_API_ENTRYPOINT"):
        load_config(env_file=env_file)


def test_load_config_rejects_unknown_algorithm(tmp_path, monkeypatch):
    monkeypatch.setenv("WORDLE_API_ENTRYPOINT", "https://api.example.test/wordle")
    monkeypatch.setenv("WORDLE_ALGORITHM", "magic")
    env_file = tmp_path / ".env"
    env_file.write_text("", encoding="utf-8")
    with pytest.raises(ValueError, match="WORDLE_ALGORITHM"):
        load_config(env_file=env_file)


def test_load_config_derives_api_base_from_daily_entrypoint(tmp_path, monkeypatch):
    monkeypatch.delenv("WORDLE_API_BASE", raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text(
        "WORDLE_API_ENTRYPOINT=https://wordle.votee.dev:8000/daily\n",
        encoding="utf-8",
    )
    config = load_config(env_file=env_file)
    assert config.api_base == "https://wordle.votee.dev:8000"
    assert config.api_entrypoint == "https://wordle.votee.dev:8000/daily"


def test_load_config_uses_explicit_api_base(tmp_path, monkeypatch):
    monkeypatch.delenv("WORDLE_API_BASE", raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "WORDLE_API_ENTRYPOINT=https://wordle.votee.dev:8000/daily",
                "WORDLE_API_BASE=https://custom.example.test",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    config = load_config(env_file=env_file)
    assert config.api_base == "https://custom.example.test"


def test_load_config_rejects_begin_greater_than_end(tmp_path, monkeypatch):
    monkeypatch.setenv("WORDLE_API_ENTRYPOINT", "https://api.example.test/wordle")
    env_file = tmp_path / ".env"
    env_file.write_text(
        "WORDLE_SIZE_BEGIN=8\nWORDLE_SIZE_END=4\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="WORDLE_SIZE_BEGIN"):
        load_config(env_file=env_file)


def test_load_config_reads_seed_range(tmp_path, monkeypatch):
    monkeypatch.delenv("WORDLE_SEED_BEGIN", raising=False)
    monkeypatch.delenv("WORDLE_SEED_END", raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "WORDLE_API_ENTRYPOINT=https://api.example.test/wordle",
                "WORDLE_SEED_BEGIN=1",
                "WORDLE_SEED_END=3",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    config = load_config(env_file=env_file)
    assert config.seed_begin == 1
    assert config.seed_end == 3
    assert config.seeds() == (1, 2, 3)


def test_load_config_defaults_seeds_to_none(tmp_path, monkeypatch):
    monkeypatch.delenv("WORDLE_SEED_BEGIN", raising=False)
    monkeypatch.delenv("WORDLE_SEED_END", raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text(
        "WORDLE_API_ENTRYPOINT=https://api.example.test/wordle\n",
        encoding="utf-8",
    )
    config = load_config(env_file=env_file)
    assert config.seed_begin is None
    assert config.seed_end is None
    assert config.seeds() == (None,)


def test_load_config_rejects_partial_seed_range(tmp_path, monkeypatch):
    monkeypatch.delenv("WORDLE_SEED_END", raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "WORDLE_API_ENTRYPOINT=https://api.example.test/wordle",
                "WORDLE_SEED_BEGIN=1",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="WORDLE_SEED_BEGIN"):
        load_config(env_file=env_file)


def test_load_config_rejects_seed_begin_greater_than_end(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "WORDLE_API_ENTRYPOINT=https://api.example.test/wordle",
                "WORDLE_SEED_BEGIN=10",
                "WORDLE_SEED_END=5",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="WORDLE_SEED_BEGIN"):
        load_config(env_file=env_file)


def test_load_config_reads_wordle_mode(tmp_path, monkeypatch):
    monkeypatch.delenv("WORDLE_MODE", raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "WORDLE_API_ENTRYPOINT=https://api.example.test/wordle",
                "WORDLE_MODE=random",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    config = load_config(env_file=env_file)
    assert config.mode == "random"


def test_load_config_rejects_unknown_mode(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "WORDLE_API_ENTRYPOINT=https://api.example.test/wordle",
                "WORDLE_MODE=weekly",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="WORDLE_MODE"):
        load_config(env_file=env_file)


def test_load_config_defaults_mode_to_daily(tmp_path, monkeypatch):
    monkeypatch.delenv("WORDLE_MODE", raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text(
        "WORDLE_API_ENTRYPOINT=https://api.example.test/wordle\n",
        encoding="utf-8",
    )
    config = load_config(env_file=env_file)
    assert config.mode == "daily"
