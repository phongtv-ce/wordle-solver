from collections.abc import Sequence

from solver.algorithms.candidates.placement import can_place
from solver.types import SolverState


def next_guess(state: SolverState) -> str:
    if len(state.candidates) == 0:
        from solver.algorithms.brute_force.probes import next_fallback_guess

        return next_fallback_guess(state)
    if len(state.candidates) <= 2:
        return select_candidate_guess(
            state.candidates,
            state.correct_state,
            state.present_state,
            state.present_chars,
        )
    return build_probe_guess(state)


def position_priority(
    correct_state: tuple[str | None, ...],
    present_state: tuple[frozenset[str], ...],
) -> tuple[int, ...]:
    correct_indices = [i for i, letter in enumerate(correct_state) if letter is not None]
    present_indices = [i for i, forbidden in enumerate(present_state) if forbidden]
    rest = [
        i
        for i in range(len(correct_state))
        if i not in correct_indices and i not in present_indices
    ]
    return tuple(correct_indices + present_indices + rest)


def chars_not_universal(
    present_chars: frozenset[str],
    candidates: Sequence[str],
) -> tuple[str, ...]:
    if not candidates:
        return ()
    result: list[str] = []
    for letter in sorted(present_chars):
        if not all(letter in word for word in candidates):
            result.append(letter)
    return tuple(result)


def place_letters(
    slots: Sequence[str | None],
    letters: Sequence[str],
    order: Sequence[int],
    present_state: tuple[frozenset[str], ...],
) -> tuple[str | None, ...]:
    result = list(slots)
    for letter in letters:
        placed = False
        for index in order:
            if result[index] is None and can_place(letter, index, present_state):
                result[index] = letter
                placed = True
                break
        if not placed:
            continue
    return tuple(result)


def build_probe_guess(state: SolverState) -> str:
    order = position_priority(state.correct_state, state.present_state)
    slots: list[str | None] = [None] * state.word_length

    for letters in (
        sorted(state.untried_dictionary_chars),
        chars_not_universal(state.present_chars, state.candidates),
        sorted(state.present_chars),
        sorted(state.untried_external_chars),
    ):
        slots = list(place_letters(slots, letters, order, state.present_state))

    if any(slot is None for slot in slots):
        for letter in sorted(state.present_chars):
            slots = list(place_letters(slots, [letter], order, state.present_state))

    return "".join(slot if slot is not None else "a" for slot in slots)


def score_candidate(
    word: str,
    correct_state: tuple[str | None, ...],
    present_state: tuple[frozenset[str], ...],
    present_chars: frozenset[str],
) -> int:
    score = 0
    for i, letter in enumerate(correct_state):
        if letter is not None and word[i] == letter:
            score += 2
    for letter in present_chars:
        if letter in word:
            score += 1
    for i, forbidden in enumerate(present_state):
        if word[i] not in forbidden:
            score += 1
    return score


def select_candidate_guess(
    candidates: Sequence[str],
    correct_state: tuple[str | None, ...],
    present_state: tuple[frozenset[str], ...],
    present_chars: frozenset[str],
) -> str:
    return min(
        candidates,
        key=lambda word: (
            -score_candidate(word, correct_state, present_state, present_chars),
            word,
        ),
    )
