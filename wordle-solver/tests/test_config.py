from pathlib import Path

from solver.config import load_config


def test_load_config_reads_api_entrypoint_from_env_file(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "WORDLE_API_ENTRYPOINT=https://api.example.test/wordle/",
                "WORDLE_API_KEY=secret-token",
                "WORDLE_WORD_LENGTH=6",
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
    monkeypatch.delenv("WORDLE_API_KEY", raising=False)
    monkeypatch.delenv("WORDLE_WORD_LENGTH", raising=False)
    monkeypatch.delenv("WORDLE_ALGORITHM", raising=False)
    monkeypatch.delenv("WORDLE_DICTIONARY_PATH", raising=False)
    monkeypatch.delenv("WORDLE_MAX_GUESSES", raising=False)
    monkeypatch.delenv("WORDLE_API_TIMEOUT_SECONDS", raising=False)

    config = load_config(env_file=env_file)

    assert config.api_entrypoint == "https://api.example.test/wordle"
    assert config.api_key == "secret-token"
    assert config.word_length == 6
    assert config.algorithm == "brute_force"
    assert config.dictionary_path == (Path(__file__).resolve().parents[1] / "words.txt").resolve()
    assert config.max_guesses == 12
    assert config.api_timeout_seconds == 3.5


def test_load_config_requires_api_entrypoint(tmp_path, monkeypatch):
    monkeypatch.delenv("WORDLE_API_ENTRYPOINT", raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text("WORDLE_WORD_LENGTH=5\n", encoding="utf-8")
    try:
        load_config(env_file=env_file)
    except ValueError as exc:
        assert "WORDLE_API_ENTRYPOINT" in str(exc)
    else:
        raise AssertionError("expected missing WORDLE_API_ENTRYPOINT to raise")


def test_load_config_rejects_unknown_algorithm(tmp_path, monkeypatch):
    monkeypatch.setenv("WORDLE_API_ENTRYPOINT", "https://api.example.test/wordle")
    monkeypatch.setenv("WORDLE_ALGORITHM", "magic")
    env_file = tmp_path / ".env"
    env_file.write_text("", encoding="utf-8")
    try:
        load_config(env_file=env_file)
    except ValueError as exc:
        assert "WORDLE_ALGORITHM" in str(exc)
    else:
        raise AssertionError("expected unknown algorithm to raise")
