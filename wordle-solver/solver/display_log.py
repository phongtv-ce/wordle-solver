"""Terminal display logs for Wordle guess rounds (no solver logic)."""

from __future__ import annotations

import os
import sys

from solver.types import Feedback, SolverState

_RESET = "\033[0m"
_GREEN = "\033[92m"
_YELLOW = "\033[93m"
_RED = "\033[91m"
_DIM = "\033[2m"

_RESULT_COLORS = {
    "correct": _GREEN,
    "present": _YELLOW,
    "absent": _RED,
}


def _use_color() -> bool:
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("WORDLE_NO_COLOR"):
        return False
    if not hasattr(sys.stdout, "isatty") or not sys.stdout.isatty():
        return False
    return True


def _colorize(text: str, color: str, enabled: bool) -> str:
    if not enabled:
        return text
    return f"{color}{text}{_RESET}"


def format_colored_guess(feedback: Feedback, *, color: bool | None = None) -> str:
    """Color each guessed letter: green=correct, yellow=present, red=absent."""
    use_color = color if color is not None else _use_color()
    parts: list[str] = []
    for slot in feedback:
        letter = slot.guess
        parts.append(_colorize(letter, _RESULT_COLORS[slot.result], use_color))
    return "".join(parts)


def format_present_correct_chars(state: SolverState) -> str:
    """Sorted letters confirmed present or correct in the target."""
    return "".join(sorted(state.present_chars))


def format_char_set(chars: frozenset[str]) -> str:
    return "".join(sorted(chars))


def format_guess_attempt_line(
    attempt: int,
    feedback: Feedback,
    state: SolverState,
    *,
    color: bool | None = None,
) -> str:
    """
    attempts | guess word | present/correct | untried in dictionary | untried not in dictionary
    """
    use_color = color if color is not None else _use_color()
    attempt_col = str(attempt)
    guess_col = format_colored_guess(feedback, color=use_color)
    present_col = format_present_correct_chars(state)
    dict_col = format_char_set(state.untried_dictionary_chars)
    external_col = format_char_set(state.untried_external_chars)
    columns = (
        attempt_col,
        guess_col,
        present_col,
        dict_col,
        external_col,
    )
    return " | ".join(columns)


def log_guess_attempt(
    attempt: int,
    feedback: Feedback,
    state: SolverState,
    *,
    stream: object = None,
    color: bool | None = None,
) -> None:
    """Print one display line for a completed guess round."""
    line = format_guess_attempt_line(attempt, feedback, state, color=color)
    out = stream if stream is not None else sys.stdout
    print(line, file=out, flush=True)


def log_guess_attempt_header(*, stream: object = None, color: bool | None = None) -> None:
    """Print column headers for guess attempt lines."""
    use_color = color if color is not None else _use_color()
    headers = (
        "attempt",
        "guess",
        "present/correct",
        "untried in dictionary",
        "untried not in dictionary",
    )
    if use_color:
        headers = tuple(_colorize(h, _DIM, True) for h in headers)
    out = stream if stream is not None else sys.stdout
    print(" | ".join(headers), file=out, flush=True)
