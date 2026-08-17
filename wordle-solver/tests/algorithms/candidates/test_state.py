from solver.algorithms.candidates.state import apply_feedback, filter_by_length, initial_state
from solver.types import SlotFeedback
from tests.helpers import ALPHABET, GUESS_FEEDBACK, make_state


def test_filter_by_length_lowercases_dedupes_and_keeps_order():
    assert filter_by_length(["CAT", "dog", "cat", "bird", "a"], 3) == ("cat", "dog")


def test_filter_by_length_empty_when_no_word_has_that_length():
    assert filter_by_length(["aa", "bb"], 5) == ()


def test_initial_state_loads_length_n_candidates_and_untried_sets():
    state = initial_state(3, ["cat", "dog", "bird", "CAT"])
    assert state.word_length == 3
    assert state.candidates == ("cat", "dog")
    assert state.present_chars == frozenset()
    assert state.absent_chars == frozenset()
    assert state.tried_chars == frozenset()
    assert state.correct_state == (None, None, None)
    assert state.present_state == (frozenset(), frozenset(), frozenset())
    assert state.untried_dictionary_chars == frozenset("catdog")
    assert state.untried_external_chars == ALPHABET - frozenset("catdog")
    assert state.untried_dictionary_chars.isdisjoint(state.untried_external_chars)


def test_initial_state_untried_external_starts_from_full_alphabet_minus_candidates():
    state = initial_state(1, ["a", "b"])
    assert "a" not in state.untried_external_chars
    assert "b" not in state.untried_external_chars
    assert "z" in state.untried_external_chars


def test_apply_feedback_narrows_two_letter_candidates():
    state = make_state(
        word_length=2,
        candidates=("ab", "ac", "ba", "zz", "de"),
        untried_dictionary_chars=frozenset("abcdez"),
        untried_external_chars=ALPHABET - frozenset("abcdez"),
        present_state=(frozenset(), frozenset()),
        correct_state=(None, None),
    )
    feedback = (
        SlotFeedback(slot=0, guess="a", result="present"),
        SlotFeedback(slot=1, guess="z", result="absent"),
    )
    next_state = apply_feedback(state, feedback)

    assert next_state.correct_state == (None, None)
    assert next_state.present_state[0] == frozenset({"a"})
    assert next_state.present_chars == frozenset({"a"})
    assert next_state.absent_chars == frozenset({"z"})
    assert next_state.min_counts["a"] == 1
    assert next_state.max_counts["z"] == 0
    assert "z" not in next_state.present_chars
    assert next_state.tried_chars == frozenset({"a", "z"})
    assert next_state.candidates == ("ba",)
    assert next_state.untried_dictionary_chars == frozenset({"b"})
    assert "a" not in next_state.untried_dictionary_chars
    assert "z" not in next_state.untried_external_chars
    assert state.candidates == ("ab", "ac", "ba", "zz", "de")


def test_apply_feedback_guess_example_sets_positions_and_letter_sets():
    state = make_state(
        word_length=5,
        candidates=("guess", "judas", "guise", "ludus", "humus"),
        untried_dictionary_chars=frozenset("guesjadlhm"),
        untried_external_chars=ALPHABET - frozenset("guesjadlhm"),
    )
    next_state = apply_feedback(state, GUESS_FEEDBACK)
    assert next_state.correct_state == (None, "u", None, None, "s")
    assert next_state.present_state[3] == frozenset({"s"})
    assert next_state.present_chars == frozenset({"u", "s"})
    assert next_state.absent_chars == frozenset({"g", "e"})
    assert next_state.min_counts["s"] == 2
    assert next_state.min_counts["u"] == 1
    assert "guess" not in next_state.candidates
    assert "guise" not in next_state.candidates
    for word in next_state.candidates:
        assert word[1] == "u"
        assert word[4] == "s"
        assert word[3] != "s"
        assert "g" not in word and "e" not in word
        assert word.count("s") >= 2
