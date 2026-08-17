import pytest

from solver.feedback import (
    is_solved,
    letter_outcomes,
    merge_counts,
    parse_feedback,
    update_absent_chars,
    update_correct_state,
    update_present_chars,
    update_present_state,
)
from solver.types import SlotFeedback
from tests.helpers import GUESS_API_RAW, GUESS_FEEDBACK, SOLVED_FEEDBACK


def test_parse_feedback_normalizes_the_guess_api_example():
    assert parse_feedback(GUESS_API_RAW) == GUESS_FEEDBACK


def test_parse_feedback_lowercases_guess_letters():
    raw = [
        {"slot": 0, "guess": "G", "result": "absent"},
        {"slot": 1, "guess": "U", "result": "correct"},
    ]
    parsed = parse_feedback(raw)
    assert parsed[0].guess == "g"
    assert parsed[1].guess == "u"
    assert parsed[1].result == "correct"


def test_parse_feedback_rejects_invalid_result():
    with pytest.raises(ValueError):
        parse_feedback([{"slot": 0, "guess": "a", "result": "yellow"}])


def test_parse_feedback_rejects_missing_fields():
    with pytest.raises(ValueError):
        parse_feedback([{"slot": 0, "guess": "a"}])


def test_is_solved_true_when_every_slot_is_correct():
    assert is_solved(SOLVED_FEEDBACK) is True


def test_is_solved_false_when_any_slot_is_not_correct():
    assert is_solved(GUESS_FEEDBACK) is False


def test_update_correct_state_writes_correct_slots_only():
    start = (None, None, None, None, None)
    result = update_correct_state(start, GUESS_FEEDBACK)
    assert result == (None, "u", None, None, "s")
    assert start == (None, None, None, None, None)


def test_update_correct_state_does_not_clear_existing_correct_slots():
    start = ("j", None, None, None, None)
    extra = (SlotFeedback(slot=2, guess="x", result="absent"),)
    result = update_correct_state(start, extra)
    assert result[0] == "j"


def test_update_present_state_adds_present_letters_to_that_slot():
    start = (frozenset(), frozenset(), frozenset(), frozenset(), frozenset())
    result = update_present_state(start, GUESS_FEEDBACK)
    assert result[3] == frozenset({"s"})
    assert result[0] == frozenset()
    assert result[1] == frozenset()
    assert start[3] == frozenset()


def test_update_present_state_accumulates_multiple_present_letters():
    start = (frozenset({"a"}), frozenset(), frozenset())
    feedback = (SlotFeedback(slot=0, guess="b", result="present"),)
    result = update_present_state(start, feedback)
    assert result[0] == frozenset({"a", "b"})


def test_letter_outcomes_for_guess_api_example():
    newly_present, newly_absent, min_delta, max_delta = letter_outcomes(GUESS_FEEDBACK)
    assert newly_present == frozenset({"u", "s"})
    assert newly_absent == frozenset({"g", "e"})
    assert min_delta["u"] == 1
    assert min_delta["s"] == 2
    assert max_delta["g"] == 0
    assert max_delta["e"] == 0
    assert "s" not in max_delta
    assert "u" not in max_delta


def test_letter_outcomes_duplicate_letter_absent_caps_exact_count():
    feedback = (
        SlotFeedback(slot=0, guess="g", result="absent"),
        SlotFeedback(slot=1, guess="u", result="correct"),
        SlotFeedback(slot=2, guess="e", result="absent"),
        SlotFeedback(slot=3, guess="s", result="absent"),
        SlotFeedback(slot=4, guess="s", result="correct"),
    )
    newly_present, newly_absent, min_delta, max_delta = letter_outcomes(feedback)
    assert newly_present == frozenset({"u", "s"})
    assert newly_absent == frozenset({"g", "e"})
    assert "s" not in newly_absent
    assert min_delta["s"] == 1
    assert max_delta["s"] == 1


def test_merge_counts_tightens_min_up_and_max_down():
    new_min, new_max = merge_counts(
        old_min={"s": 1},
        old_max={"s": 5},
        delta_min={"s": 2},
        delta_max={"s": 2},
        n=5,
    )
    assert new_min["s"] == 2
    assert new_max["s"] == 2


def test_merge_counts_defaults_max_to_word_length():
    new_min, new_max = merge_counts(
        old_min={},
        old_max={},
        delta_min={"a": 1},
        delta_max={},
        n=5,
    )
    assert new_min["a"] == 1
    assert new_max["a"] == 5


def test_update_present_chars_unions_new_letters():
    assert update_present_chars(frozenset({"u"}), frozenset({"s", "u"})) == frozenset(
        {"u", "s"}
    )


def test_update_absent_chars_drops_letters_that_are_present():
    result = update_absent_chars(
        absent_chars=frozenset({"x"}),
        newly_absent=frozenset({"g", "s"}),
        present_chars=frozenset({"s", "u"}),
    )
    assert result == frozenset({"x", "g"})
    assert "s" not in result
