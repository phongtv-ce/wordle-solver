from solver.algorithms.candidates.untried import (
    candidate_alphabet,
    known_chars,
    update_tried_chars,
    update_untried_dictionary_chars,
    update_untried_external_chars,
)
from tests.helpers import ALPHABET, GUESS_FEEDBACK


def test_candidate_alphabet_unions_letters_across_words():
    assert candidate_alphabet(("ab", "ac")) == frozenset({"a", "b", "c"})
    assert candidate_alphabet(()) == frozenset()


def test_update_tried_chars_unions_guessed_letters():
    result = update_tried_chars(frozenset({"x"}), GUESS_FEEDBACK)
    assert result == frozenset({"x", "g", "u", "e", "s"})


def test_known_chars_is_present_union_absent():
    assert known_chars(frozenset({"u", "s"}), frozenset({"g", "e"})) == frozenset(
        {"u", "s", "g", "e"}
    )


def test_update_untried_dictionary_chars_removes_tried_and_known():
    result = update_untried_dictionary_chars(
        candidate_letters=frozenset({"a", "b", "u", "s"}),
        tried_chars=frozenset({"u", "g"}),
        known=frozenset({"u", "s", "g"}),
    )
    assert result == frozenset({"a", "b"})


def test_update_untried_external_chars_is_alphabet_minus_candidate_tried_known():
    result = update_untried_external_chars(
        letters=ALPHABET,
        candidate_letters=frozenset({"a", "b"}),
        tried_chars=frozenset({"z"}),
        known=frozenset({"a"}),
    )
    assert result == ALPHABET - frozenset({"a", "b", "z"})
    assert "a" not in result
    assert "b" not in result
    assert "z" not in result
    assert "c" in result
