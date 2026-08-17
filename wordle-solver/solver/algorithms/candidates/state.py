from collections.abc import Sequence

from solver.algorithms.candidates.filter import filter_candidates
from solver.algorithms.candidates.untried import (
    candidate_alphabet,
    known_chars,
    update_tried_chars,
    update_untried_dictionary_chars,
    update_untried_external_chars,
)
from solver.feedback import (
    letter_outcomes,
    merge_counts,
    update_absent_chars,
    update_correct_state,
    update_present_chars,
    update_present_state,
)
from solver.types import Feedback, SolverState, alphabet, empty_correct_state, empty_present_state


def filter_by_length(dictionary: Sequence[str], n: int) -> tuple[str, ...]:
    seen: set[str] = set()
    result: list[str] = []
    for word in dictionary:
        lowered = word.lower()
        if len(lowered) == n and lowered not in seen:
            seen.add(lowered)
            result.append(lowered)
    return tuple(result)


def initial_state(n: int, dictionary: Sequence[str]) -> SolverState:
    candidates = filter_by_length(dictionary, n)
    candidate_letters = candidate_alphabet(candidates)
    known = frozenset()
    untried_dictionary = update_untried_dictionary_chars(candidate_letters, frozenset(), known)
    untried_external = update_untried_external_chars(
        alphabet(), candidate_letters, frozenset(), known
    )
    return SolverState(
        word_length=n,
        present_chars=frozenset(),
        absent_chars=frozenset(),
        untried_dictionary_chars=untried_dictionary,
        untried_external_chars=untried_external,
        present_state=empty_present_state(n),
        correct_state=empty_correct_state(n),
        min_counts={},
        max_counts={},
        tried_chars=frozenset(),
        position_probed_chars=frozenset(),
        candidates=candidates,
    )


def apply_feedback(state: SolverState, feedback: Feedback) -> SolverState:
    correct_state = update_correct_state(state.correct_state, feedback)
    present_state = update_present_state(state.present_state, feedback)
    newly_present, newly_absent, delta_min, delta_max = letter_outcomes(feedback)
    present_chars = update_present_chars(state.present_chars, newly_present)
    absent_chars = update_absent_chars(state.absent_chars, newly_absent, present_chars)
    min_counts, max_counts = merge_counts(
        state.min_counts,
        state.max_counts,
        delta_min,
        delta_max,
        state.word_length,
    )
    candidates = filter_candidates(
        state.candidates,
        correct_state,
        present_state,
        present_chars,
        absent_chars,
        min_counts,
        max_counts,
    )
    tried_chars = update_tried_chars(state.tried_chars, feedback)
    known = known_chars(present_chars, absent_chars)
    candidate_letters = candidate_alphabet(candidates)
    untried_dictionary = update_untried_dictionary_chars(
        candidate_letters, tried_chars, known
    )
    untried_external = update_untried_external_chars(
        alphabet(), candidate_letters, tried_chars, known
    )
    return SolverState(
        word_length=state.word_length,
        present_chars=present_chars,
        absent_chars=absent_chars,
        untried_dictionary_chars=untried_dictionary,
        untried_external_chars=untried_external,
        present_state=present_state,
        correct_state=correct_state,
        min_counts=min_counts,
        max_counts=max_counts,
        tried_chars=tried_chars,
        position_probed_chars=state.position_probed_chars,
        candidates=candidates,
    )
