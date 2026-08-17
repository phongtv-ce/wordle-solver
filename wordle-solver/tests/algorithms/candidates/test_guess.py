from solver.algorithms.brute_force.probes import next_fallback_guess
from solver.algorithms.candidates.guess import (
    build_probe_guess,
    can_place,
    chars_not_universal,
    next_guess,
    place_letters,
    position_priority,
    score_candidate,
    select_candidate_guess,
)
from tests.helpers import ALPHABET, make_state

EMPTY5 = (frozenset(), frozenset(), frozenset(), frozenset(), frozenset())


def test_position_priority_correct_then_present_then_rest():
    correct = (None, "u", None, None, "s")
    present_state = (
        frozenset(),
        frozenset(),
        frozenset(),
        frozenset({"s"}),
        frozenset(),
    )
    assert position_priority(correct, present_state) == (1, 4, 3, 0, 2)


def test_position_priority_all_empty_is_left_to_right():
    assert position_priority((None, None, None), EMPTY5[:3]) == (0, 1, 2)


def test_chars_not_universal_drops_letters_in_every_candidate():
    assert chars_not_universal(frozenset({"a", "b", "c"}), ("ab", "ac")) == ("b", "c")


def test_chars_not_universal_empty_when_all_present_letters_are_shared():
    assert chars_not_universal(frozenset({"a"}), ("ab", "ac")) == ()


def test_can_place_false_when_letter_is_known_wrong_for_that_slot():
    present_state = (frozenset(), frozenset(), frozenset(), frozenset({"s"}), frozenset())
    assert can_place("s", 3, present_state) is False
    assert can_place("s", 0, present_state) is True
    assert can_place("u", 3, present_state) is True


def test_place_letters_fills_empty_slots_in_priority_order():
    slots = (None, None, None, None, None)
    order = (1, 4, 3, 0, 2)
    result = place_letters(slots, "qwxzy", order, EMPTY5)
    assert tuple(result) == ("z", "q", "y", "x", "w")


def test_place_letters_skips_slot_when_letter_cannot_be_placed_there():
    present_state = (frozenset(), frozenset(), frozenset(), frozenset({"x"}), frozenset())
    result = place_letters(
        (None, None, None, None, None),
        "qx",
        (1, 4, 3, 0, 2),
        present_state,
    )
    assert tuple(result)[1] == "q"
    assert tuple(result)[3] != "x"
    assert "x" in tuple(result)


def test_place_letters_skips_letter_when_no_legal_slot_remains():
    present_state = tuple(frozenset({"a"}) for _ in range(3))
    result = place_letters((None, None, None), "a", (0, 1, 2), present_state)
    assert tuple(result) == (None, None, None)


def test_build_probe_guess_uses_sorted_untried_dictionary_chars_first():
    state = make_state(
        word_length=5,
        candidates=("aaaaa", "bbbbb", "ccccc"),
        untried_dictionary_chars=frozenset("qwxzy"),
        correct_state=(None, "u", None, None, "s"),
        present_state=(
            frozenset(),
            frozenset(),
            frozenset(),
            frozenset({"s"}),
            frozenset(),
        ),
        present_chars=frozenset({"u", "s"}),
    )
    guess = build_probe_guess(state)
    assert guess == "yqzxw"
    assert len(guess) == 5
    assert guess.islower()


def test_build_probe_guess_falls_back_to_discriminating_present_chars():
    state = make_state(
        word_length=2,
        candidates=("ab", "ac"),
        untried_dictionary_chars=frozenset(),
        present_chars=frozenset({"a", "b", "c"}),
        present_state=(frozenset(), frozenset()),
        correct_state=(None, None),
        untried_external_chars=frozenset(),
    )
    guess = build_probe_guess(state)
    assert len(guess) == 2
    assert set(guess) <= set("abc")
    assert "b" in guess or "c" in guess


def test_score_candidate_prefers_more_correct_slots():
    present_state = (frozenset(), frozenset(), frozenset())
    higher = score_candidate("abc", ("a", None, None), present_state, frozenset({"a"}))
    lower = score_candidate("xbc", ("a", None, None), present_state, frozenset({"a"}))
    assert higher > lower


def test_select_candidate_guess_picks_highest_score_then_lexicographic():
    present_state = (frozenset(), frozenset())
    assert (
        select_candidate_guess(("bc", "ab"), (None, None), present_state, frozenset())
        == "ab"
    )


def test_select_candidate_guess_returns_the_only_candidate():
    present_state = (frozenset(), frozenset())
    assert (
        select_candidate_guess(("ba",), (None, None), present_state, frozenset({"a"}))
        == "ba"
    )


def test_next_guess_uses_the_single_remaining_candidate():
    state = make_state(
        word_length=2,
        candidates=("ba",),
        present_chars=frozenset({"a"}),
        present_state=(frozenset({"a"}), frozenset()),
        correct_state=(None, None),
    )
    assert next_guess(state) == "ba"


def test_next_guess_chooses_one_of_two_remaining_candidates():
    state = make_state(
        word_length=2,
        candidates=("ab", "ac"),
        present_chars=frozenset({"a"}),
        present_state=(frozenset(), frozenset()),
        correct_state=(None, None),
    )
    assert next_guess(state) in {"ab", "ac"}


def test_next_guess_probes_when_more_than_two_candidates_remain():
    state = make_state(
        word_length=5,
        candidates=("aaaaa", "bbbbb", "ccccc"),
        untried_dictionary_chars=frozenset("qwxzy"),
        correct_state=(None, "u", None, None, "s"),
        present_state=(
            frozenset(),
            frozenset(),
            frozenset(),
            frozenset({"s"}),
            frozenset(),
        ),
        present_chars=frozenset({"u", "s"}),
    )
    assert next_guess(state) == build_probe_guess(state)


def test_next_guess_falls_back_when_candidates_are_empty():
    state = make_state(
        word_length=5,
        candidates=(),
        present_chars=frozenset({"a"}),
        min_counts={"a": 1},
        untried_external_chars=ALPHABET - frozenset("a"),
        correct_state=(None, None, None, None, None),
    )
    assert next_guess(state) == next_fallback_guess(state)
