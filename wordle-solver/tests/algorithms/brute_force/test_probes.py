import pytest

from solver.algorithms.brute_force import initial_state as brute_initial_state
from solver.algorithms.brute_force.probes import (
    charset_probe,
    is_position_probe_feedback,
    next_fallback_guess,
    position_probe,
    position_probe_letter,
    unplaced_present,
)
from tests.helpers import ALPHABET, make_state


def test_brute_force_initial_state_ignores_dictionary_and_starts_empty():
    state = brute_initial_state(5, ["apple", "grape"])
    assert state.word_length == 5
    assert state.candidates == ()
    assert state.untried_dictionary_chars == frozenset()
    assert state.untried_external_chars == ALPHABET
    assert state.correct_state == (None, None, None, None, None)


def test_charset_probe_takes_first_n_letters_in_input_order():
    assert charset_probe("zyxwvut", 5) == "zyxwv"
    assert charset_probe(["a", "b", "c", "d", "e", "f"], 5) == "abcde"


def test_charset_probe_cycles_when_fewer_than_n_letters():
    assert charset_probe("ab", 5) == "ababa"
    assert len(charset_probe("abc", 8)) == 8


def test_charset_probe_rejects_empty_untried():
    with pytest.raises(ValueError):
        charset_probe("", 5)


def test_position_probe_repeats_the_letter():
    assert position_probe("a", 5) == "aaaaa"
    assert position_probe("s", 3) == "sss"


def test_position_probe_keeps_previous_correct_slots():
    # After e is locked at slot 2 (3rd letter), probe i as iieiiiii, not iiiiiiii.
    assert position_probe("i", 8, (None, None, "e", None, None, None, None, None)) == "iieiiiii"


def test_position_probe_keeps_several_correct_slots():
    assert position_probe("l", 8, (None, None, "e", None, None, "i", None, None)) == "llellill"


def test_unplaced_present_returns_letters_not_fully_locked():
    result = unplaced_present(
        present_chars=frozenset({"a", "b"}),
        correct_state=("a", None, None),
        min_counts={"a": 1, "b": 1},
    )
    assert result == ("b",)


def test_unplaced_present_keeps_letter_when_min_count_exceeds_correct_slots():
    result = unplaced_present(
        present_chars=frozenset({"s"}),
        correct_state=(None, None, None, None, "s"),
        min_counts={"s": 2},
    )
    assert result == ("s",)


def test_unplaced_present_uses_sorted_order_when_several_letters_remain():
    result = unplaced_present(
        present_chars=frozenset({"c", "a", "b"}),
        correct_state=(None, None, None),
        min_counts={"a": 1, "b": 1, "c": 1},
    )
    assert result == ("a", "b", "c")


def test_unplaced_present_empty_when_all_present_letters_are_placed():
    result = unplaced_present(
        present_chars=frozenset({"u", "s"}),
        correct_state=(None, "u", None, None, "s"),
        min_counts={"u": 1, "s": 1},
    )
    assert result == ()


def test_next_fallback_guess_prefers_charset_while_untried_external_remain():
    state = make_state(
        word_length=8,
        candidates=(),
        present_chars=frozenset({"e"}),
        min_counts={"e": 1},
        absent_chars=frozenset("abcdfgh"),
        tried_chars=frozenset("abcdefgh"),
        untried_external_chars=frozenset("ijklmnopqrstuvwxyz"),
    )
    assert next_fallback_guess(state) == "ijklmnop"


def test_next_fallback_guess_repeats_next_unplaced_present_letter():
    state = make_state(
        word_length=5,
        candidates=(),
        present_chars=frozenset({"a"}),
        min_counts={"a": 1},
        correct_state=(None, None, None, None, None),
        untried_external_chars=frozenset(),
        untried_dictionary_chars=frozenset(),
    )
    assert next_fallback_guess(state) == "aaaaa"


def test_next_fallback_guess_keeps_correct_when_position_probing():
    # pleurisy: e already at slot 2, next unplaced letter is i → iieiiiii
    state = make_state(
        word_length=8,
        candidates=(),
        present_chars=frozenset("eilprsuy"),
        min_counts={letter: 1 for letter in "eilprsuy"},
        correct_state=(None, None, "e", None, None, None, None, None),
        untried_external_chars=frozenset(),
        untried_dictionary_chars=frozenset(),
        position_probed_chars=frozenset({"e"}),
    )
    assert next_fallback_guess(state) == "iieiiiii"


def test_next_fallback_guess_skips_position_probe_after_letter_was_probed():
    state = make_state(
        word_length=5,
        candidates=(),
        present_chars=frozenset({"a", "b"}),
        min_counts={"a": 1, "b": 1},
        correct_state=(None, None, None, None, None),
        untried_external_chars=frozenset(),
        untried_dictionary_chars=frozenset(),
        position_probed_chars=frozenset({"a"}),
    )
    assert next_fallback_guess(state) == "bbbbb"


def test_is_position_probe_feedback_all_same_letter():
    from solver.types import SlotFeedback

    feedback = tuple(
        SlotFeedback(slot=i, guess="e", result="absent") for i in range(8)
    )
    assert is_position_probe_feedback(feedback) is True
    assert position_probe_letter(feedback) == "e"


def test_is_position_probe_feedback_keeps_correct_slots():
    from solver.types import SlotFeedback

    # Guess iieiiiii after e is locked at slot 2
    guesses = list("iieiiiii")
    feedback = tuple(
        SlotFeedback(slot=i, guess=letter, result="absent")
        for i, letter in enumerate(guesses)
    )
    correct_state = (None, None, "e", None, None, None, None, None)
    assert is_position_probe_feedback(feedback, correct_state) is True
    assert position_probe_letter(feedback, correct_state) == "i"


def test_is_position_probe_feedback_rejects_charset_guess():
    from solver.types import SlotFeedback

    feedback = tuple(
        SlotFeedback(slot=i, guess=letter, result="absent")
        for i, letter in enumerate("abcdefgh")
    )
    assert is_position_probe_feedback(feedback) is False
    assert position_probe_letter(feedback) is None


def test_next_fallback_guess_probes_sorted_untried_external_when_presents_are_placed():
    state = make_state(
        word_length=3,
        candidates=(),
        present_chars=frozenset({"a"}),
        min_counts={"a": 1},
        correct_state=("a", None, None),
        untried_external_chars=frozenset("zqm"),
        untried_dictionary_chars=frozenset(),
    )
    assert next_fallback_guess(state) == "mqz"


def test_next_fallback_guess_fills_remaining_holes_from_present_chars():
    state = make_state(
        word_length=3,
        candidates=(),
        present_chars=frozenset({"a", "b"}),
        min_counts={"a": 1, "b": 1},
        correct_state=("a", "b", None),
        present_state=(frozenset(), frozenset(), frozenset({"a"})),
        untried_external_chars=frozenset(),
        untried_dictionary_chars=frozenset(),
        position_probed_chars=frozenset({"a", "b"}),
    )
    assert next_fallback_guess(state) == "abb"


def test_brute_force_apply_feedback_marks_position_probe_letters():
    from solver.algorithms.brute_force import apply_feedback, initial_state
    from solver.types import SlotFeedback

    state = initial_state(3)
    feedback = (
        SlotFeedback(slot=0, guess="a", result="absent"),
        SlotFeedback(slot=1, guess="a", result="present"),
        SlotFeedback(slot=2, guess="a", result="absent"),
    )
    state = apply_feedback(state, feedback)
    assert state.position_probed_chars == frozenset({"a"})


def test_brute_force_apply_feedback_marks_probe_when_correct_slots_kept():
    from solver.algorithms.brute_force import apply_feedback, initial_state
    from solver.types import SlotFeedback

    state = initial_state(4)
    # First lock e at slot 1 via a uniform probe.
    state = apply_feedback(
        state,
        (
            SlotFeedback(slot=0, guess="e", result="absent"),
            SlotFeedback(slot=1, guess="e", result="correct"),
            SlotFeedback(slot=2, guess="e", result="absent"),
            SlotFeedback(slot=3, guess="e", result="absent"),
        ),
    )
    assert state.correct_state == (None, "e", None, None)
    # Then probe i while keeping e: ieii
    state = apply_feedback(
        state,
        (
            SlotFeedback(slot=0, guess="i", result="absent"),
            SlotFeedback(slot=1, guess="e", result="correct"),
            SlotFeedback(slot=2, guess="i", result="correct"),
            SlotFeedback(slot=3, guess="i", result="absent"),
        ),
    )
    assert state.position_probed_chars == frozenset({"e", "i"})
    assert state.correct_state == (None, "e", "i", None)
