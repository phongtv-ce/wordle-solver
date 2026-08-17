from solver.display_log import (
    format_colored_guess,
    format_guess_attempt_line,
    log_guess_attempt_header,
)
from solver.types import SlotFeedback
from tests.helpers import GUESS_FEEDBACK, make_state


def test_format_colored_guess_without_color():
    assert format_colored_guess(GUESS_FEEDBACK, color=False) == "guess"


def test_format_guess_attempt_line_without_color():
    feedback = (
        SlotFeedback(slot=0, guess="a", result="correct"),
        SlotFeedback(slot=1, guess="b", result="absent"),
    )
    state = make_state(
        word_length=2,
        present_chars=frozenset({"a"}),
        absent_chars=frozenset({"b"}),
        untried_dictionary_chars=frozenset({"c", "d"}),
        untried_external_chars=frozenset({"x", "y"}),
        correct_state=("a", None),
        min_counts={"a": 1},
        max_counts={"b": 0},
        tried_chars=frozenset({"a", "b"}),
        candidates=("ac",),
    )
    line = format_guess_attempt_line(1, feedback, state, color=False)
    assert line == "1 | ab | a | cd | xy"


def test_log_guess_attempt_header_without_color():
    import io
    from unittest.mock import patch

    out = io.StringIO()
    with patch("solver.display_log.sys.stdout", out):
        log_guess_attempt_header(color=False)
    header = out.getvalue()
    assert "attempt" in header
    assert "untried in dictionary" in header
    assert "untried not in dictionary" in header
