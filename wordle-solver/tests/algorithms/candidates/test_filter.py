from solver.algorithms.candidates.filter import (
    filter_candidates,
    matches_absent_chars,
    matches_correct_state,
    matches_present_chars,
    matches_present_state,
    word_matches,
)

EMPTY2 = (frozenset(), frozenset())


def test_matches_correct_state_requires_known_slots():
    correct = (None, "u", None, None, "s")
    assert matches_correct_state("judas", correct) is True
    assert matches_correct_state("jadas", correct) is False
    assert matches_correct_state("xxxxx", (None, None, None, None, None)) is True


def test_matches_present_state_forbids_letter_in_that_slot():
    present_state = (frozenset(), frozenset(), frozenset(), frozenset({"s"}), frozenset())
    assert matches_present_state("judas", present_state) is True
    assert matches_present_state("jussx", present_state) is False


def test_matches_present_chars_requires_each_letter_and_min_count():
    assert matches_present_chars("judas", frozenset({"u", "s"}), {"u": 1, "s": 1}) is True
    assert matches_present_chars("xxxxx", frozenset({"u"}), {"u": 1}) is False
    assert matches_present_chars("judas", frozenset({"s"}), {"s": 2}) is False
    assert matches_present_chars("sassy", frozenset({"s"}), {"s": 2}) is True


def test_matches_absent_chars_rejects_forbidden_letters_and_extra_duplicates():
    assert matches_absent_chars("judas", frozenset({"g", "e"}), {"g": 0, "e": 0}) is True
    assert matches_absent_chars("guess", frozenset({"g", "e"}), {"g": 0, "e": 0}) is False
    assert matches_absent_chars("sassy", frozenset(), {"s": 1}) is False
    assert matches_absent_chars("judas", frozenset(), {"s": 1}) is True


def test_word_matches_and_of_all_constraints():
    correct = (None, "u", None, None, "s")
    present_state = (frozenset(), frozenset(), frozenset(), frozenset({"s"}), frozenset())
    kwargs = {
        "correct_state": correct,
        "present_state": present_state,
        "present_chars": frozenset({"u", "s"}),
        "absent_chars": frozenset({"g", "e"}),
        "min_counts": {"u": 1, "s": 1},
        "max_counts": {"g": 0, "e": 0, "s": 2},
    }
    assert word_matches("judas", **kwargs) is True
    assert word_matches("guess", **kwargs) is False
    assert word_matches("ludus", **kwargs) is False


def test_filter_candidates_keeps_only_matching_words_in_order():
    correct = (None, None)
    present_state = (frozenset({"a"}), frozenset())
    result = filter_candidates(
        candidates=("ab", "ac", "ba", "zz", "de"),
        correct_state=correct,
        present_state=present_state,
        present_chars=frozenset({"a"}),
        absent_chars=frozenset({"z"}),
        min_counts={"a": 1},
        max_counts={"z": 0},
    )
    assert result == ("ba",)


def test_filter_candidates_does_not_reload_missing_dictionary_words():
    result = filter_candidates(
        candidates=("ba",),
        correct_state=(None, None),
        present_state=EMPTY2,
        present_chars=frozenset(),
        absent_chars=frozenset(),
        min_counts={},
        max_counts={},
    )
    assert result == ("ba",)
