from collections.abc import Sequence
from dataclasses import replace

from solver.algorithms.brute_force.probes import next_fallback_guess, position_probe_letter
from solver.types import Feedback, SolverState, alphabet, empty_correct_state, empty_present_state

NAME = "brute_force"


def initial_state(n: int, dictionary: Sequence[str] = ()) -> SolverState:
    del dictionary
    letters = alphabet()
    return SolverState(
        word_length=n,
        present_chars=frozenset(),
        absent_chars=frozenset(),
        untried_dictionary_chars=frozenset(),
        untried_external_chars=letters,
        present_state=empty_present_state(n),
        correct_state=empty_correct_state(n),
        min_counts={},
        max_counts={},
        tried_chars=frozenset(),
        position_probed_chars=frozenset(),
        candidates=(),
    )


def apply_feedback(state: SolverState, feedback: Feedback) -> SolverState:
    from solver.algorithms.candidates.state import apply_feedback as apply_candidate_feedback

    new_state = apply_candidate_feedback(state, feedback)
    letter = position_probe_letter(feedback, state.correct_state)
    if letter is not None:
        return replace(
            new_state,
            position_probed_chars=new_state.position_probed_chars | {letter},
        )
    return new_state


def next_guess(state: SolverState) -> str:
    return next_fallback_guess(state)


__all__ = ["NAME", "apply_feedback", "initial_state", "next_guess"]
