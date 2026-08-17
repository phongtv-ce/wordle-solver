import io
from unittest.mock import MagicMock, patch

import pytest

from solver.api import WordleApiError
from solver.main import (
    _resolve_puzzle_mode,
    main,
    solve_daily_for_size,
    solve_puzzle_for_size,
    SizeSolveResult,
)
from tests.helpers import GUESS_FEEDBACK, make_config, wordle_feedback_raw


def test_resolve_puzzle_mode_cli_mode_wins():
    assert _resolve_puzzle_mode("daily", "random", False) == "random"
    assert _resolve_puzzle_mode("random", "daily", False) == "daily"


def test_resolve_puzzle_mode_random_flag_overrides_config():
    assert _resolve_puzzle_mode("daily", None, True) == "random"


def test_resolve_puzzle_mode_uses_config_when_no_cli_override():
    assert _resolve_puzzle_mode("daily", None, False) == "daily"
    assert _resolve_puzzle_mode("random", None, False) == "random"


def test_solve_daily_skips_size_when_first_guess_errors():
    client = MagicMock()
    client.guess.side_effect = WordleApiError("server error")
    algorithm = MagicMock()
    algorithm.initial_state.return_value = MagicMock()
    algorithm.next_guess.return_value = "abcde"

    result = solve_daily_for_size(
        5,
        make_config(max_guesses=10),
        algorithm,
        ("abcde",),
        client,
        verbose=False,
    )

    assert result is None
    client.guess.assert_called_once_with("abcde", size=5, puzzle="daily", seed=None)


def test_solve_daily_skips_when_first_guess_raises_value_error():
    client = MagicMock()
    client.guess.side_effect = ValueError("guess length mismatch")
    algorithm = MagicMock()
    algorithm.initial_state.return_value = MagicMock()
    algorithm.next_guess.return_value = "abcde"

    result = solve_daily_for_size(
        5,
        make_config(),
        algorithm,
        ("abcde",),
        client,
        verbose=False,
    )

    assert result is None


def test_solve_daily_solves_on_first_guess():
    solved_raw = wordle_feedback_raw("abcde", "abcde")
    client = MagicMock()
    client.guess.return_value = solved_raw
    algorithm = MagicMock()
    state = MagicMock()
    algorithm.initial_state.return_value = state
    algorithm.next_guess.return_value = "abcde"
    algorithm.apply_feedback.return_value = state

    result = solve_daily_for_size(
        5,
        make_config(),
        algorithm,
        ("abcde",),
        client,
        verbose=False,
    )

    assert result is not None
    assert result.solved is True
    assert result.attempts == 1
    assert result.word == "abcde"


def test_solve_daily_solves_on_second_guess():
    partial_raw = wordle_feedback_raw("crane", "plane")
    solved_raw = wordle_feedback_raw("plane", "plane")
    client = MagicMock()
    client.guess.side_effect = [partial_raw, solved_raw]

    from solver.algorithms.candidates import apply_feedback, initial_state, next_guess

    dictionary = ("crane", "plane", "trace")
    state = initial_state(5, dictionary)
    algorithm = MagicMock()
    algorithm.initial_state.return_value = state
    algorithm.next_guess.side_effect = lambda s: next_guess(s)
    algorithm.apply_feedback.side_effect = lambda s, f: apply_feedback(s, f)

    result = solve_daily_for_size(
        5,
        make_config(max_guesses=10),
        algorithm,
        dictionary,
        client,
        verbose=False,
    )

    assert result is not None
    assert result.solved is True
    assert result.attempts == 2
    assert result.word == "plane"


def test_solve_daily_fails_when_later_guess_errors():
    partial_raw = wordle_feedback_raw("crane", "plane")
    client = MagicMock()
    client.guess.side_effect = [partial_raw, WordleApiError("timeout")]

    from solver.algorithms.candidates import apply_feedback, initial_state, next_guess

    dictionary = ("crane", "plane")
    state = initial_state(5, dictionary)
    algorithm = MagicMock()
    algorithm.initial_state.return_value = state
    algorithm.next_guess.side_effect = lambda s: next_guess(s)
    algorithm.apply_feedback.side_effect = lambda s, f: apply_feedback(s, f)

    result = solve_daily_for_size(
        5,
        make_config(max_guesses=10),
        algorithm,
        dictionary,
        client,
        verbose=False,
    )

    assert result is not None
    assert result.solved is False
    assert result.attempts == 2
    assert result.word is None


def test_solve_daily_exhausts_max_guesses():
    wrong_raw = wordle_feedback_raw("crane", "plane")
    client = MagicMock()
    client.guess.return_value = wrong_raw

    from solver.algorithms.candidates import apply_feedback, initial_state, next_guess

    dictionary = ("crane", "plane")
    state = initial_state(5, dictionary)
    algorithm = MagicMock()
    algorithm.initial_state.return_value = state
    algorithm.next_guess.side_effect = lambda s: next_guess(s)
    algorithm.apply_feedback.side_effect = lambda s, f: apply_feedback(s, f)

    result = solve_daily_for_size(
        5,
        make_config(max_guesses=3),
        algorithm,
        dictionary,
        client,
        verbose=False,
    )

    assert result is not None
    assert result.solved is False
    assert result.attempts == 3
    assert client.guess.call_count == 3


def test_solve_random_passes_puzzle_and_seed():
    solved_raw = wordle_feedback_raw("crane", "crane")
    client = MagicMock()
    client.guess.return_value = solved_raw
    algorithm = MagicMock()
    state = MagicMock()
    algorithm.initial_state.return_value = state
    algorithm.next_guess.return_value = "crane"
    algorithm.apply_feedback.return_value = state

    result = solve_puzzle_for_size(
        5,
        make_config(),
        algorithm,
        ("crane",),
        client,
        puzzle="random",
        seed=42,
        verbose=False,
    )

    assert result is not None
    assert result.solved is True
    client.guess.assert_called_once_with("crane", size=5, puzzle="random", seed=42)


def test_solve_verbose_logs_attempt_lines():
    solved_raw = wordle_feedback_raw("ab", "ab")
    client = MagicMock()
    client.guess.return_value = solved_raw

    from solver.algorithms.candidates import apply_feedback, initial_state, next_guess

    dictionary = ("ab", "ac")
    state = initial_state(2, dictionary)
    algorithm = MagicMock()
    algorithm.initial_state.return_value = state
    algorithm.next_guess.side_effect = lambda s: next_guess(s)
    algorithm.apply_feedback.side_effect = lambda s, f: apply_feedback(s, f)

    out = io.StringIO()
    with patch("solver.display_log.sys.stdout", out):
        result = solve_daily_for_size(
            2,
            make_config(size_begin=2, size_end=2),
            algorithm,
            dictionary,
            client,
            verbose=True,
        )

    assert result is not None
    assert result.solved is True
    logged = out.getvalue()
    assert "1 | ab |" in logged
    assert "ab" in logged


def test_main_skips_size_then_solves_next(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "WORDLE_API_ENTRYPOINT=https://api.example.test/daily",
                "WORDLE_SIZE_BEGIN=4",
                "WORDLE_SIZE_END=5",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    def fake_solve(size, config, algorithm, dictionary, client, *, puzzle, seed, verbose):
        if size == 4:
            return None
        return SizeSolveResult(size=5, solved=True, attempts=2, word="crane")

    with patch("solver.main.solve_puzzle_for_size", side_effect=fake_solve):
        with patch("solver.main.load_dictionary", return_value=("crane",)):
            with patch("solver.main.WordleClient"):
                rc = main(["--env-file", str(env_file)])

    assert rc == 0


def test_main_returns_one_when_a_size_fails(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "WORDLE_API_ENTRYPOINT=https://api.example.test/daily\n",
        encoding="utf-8",
    )

    def fake_solve(size, config, algorithm, dictionary, client, *, puzzle, seed, verbose):
        return SizeSolveResult(size=size, solved=False, attempts=3, word=None)

    with patch("solver.main.solve_puzzle_for_size", side_effect=fake_solve):
        with patch("solver.main.load_dictionary", return_value=()):
            with patch("solver.main.WordleClient"):
                rc = main(["--env-file", str(env_file)])

    assert rc == 1


def test_main_rejects_seed_without_random_mode(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "WORDLE_API_ENTRYPOINT=https://api.example.test/daily\n",
        encoding="utf-8",
    )

    rc = main(["--env-file", str(env_file), "--seed", "42"])
    assert rc == 1
