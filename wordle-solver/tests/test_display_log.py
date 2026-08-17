from solver.types import SlotFeedback

from solver.display_log import format_colored_guess, format_guess_attempt_line


def test_format_colored_guess_without_color():
    feedback = (
        SlotFeedback(slot=0, guess="g", result="absent"),
        SlotFeedback(slot=1, guess="u", result="correct"),
        SlotFeedback(slot=2, guess="e", result="absent"),
        SlotFeedback(slot=3, guess="s", result="present"),
        SlotFeedback(slot=4, guess="s", result="correct"),
    )
    assert format_colored_guess(feedback, color=False) == "guess"


def test_format_guess_attempt_line_without_color():
    from solver.types import SolverState

    feedback = (
        SlotFeedback(slot=0, guess="a", result="correct"),
        SlotFeedback(slot=1, guess="b", result="absent"),
    )
    state = SolverState(
        word_length=2,
        present_chars=frozenset({"a"}),
        absent_chars=frozenset({"b"}),
        untried_dictionary_chars=frozenset({"c", "d"}),
        untried_external_chars=frozenset({"x", "y"}),
        present_state=(frozenset(), frozenset()),
        correct_state=("a", None),
        min_counts={"a": 1},
        max_counts={"b": 0},
        tried_chars=frozenset({"a", "b"}),
        position_probed_chars=frozenset(),
        candidates=("ac",),
    )
    line = format_guess_attempt_line(1, feedback, state, color=False)
    assert line == "1 | ab | a | cd | xy"
