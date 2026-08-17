import pytest

from solver.algorithms.brute_force import initial_state as brute_initial_state
from solver.algorithms.brute_force.probes import (
    charset_probe,
    next_fallback_guess,
    position_probe,
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


def test_next_fallback_guess_repeats_next_unplaced_present_letter():
    state = make_state(
        word_length=5,
        candidates=(),
        present_chars=frozenset({"a"}),
        min_counts={"a": 1},
        correct_state=(None, None, None, None, None),
        untried_external_chars=ALPHABET - frozenset("a"),
    )
    assert next_fallback_guess(state) == "aaaaa"


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
    )
    assert next_fallback_guess(state) == "abb"
