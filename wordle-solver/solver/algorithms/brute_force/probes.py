from collections.abc import Mapping, Sequence

from solver.algorithms.candidates.placement import can_place
from solver.types import SolverState


def charset_probe(untried: Sequence[str], n: int) -> str:
    if not untried:
        raise ValueError("untried letters must not be empty")
    letters = list(untried)
    result: list[str] = []
    index = 0
    while len(result) < n:
        result.append(letters[index % len(letters)])
        index += 1
    return "".join(result)


def position_probe(letter: str, n: int) -> str:
    return letter * n


def unplaced_present(
    present_chars: frozenset[str],
    correct_state: tuple[str | None, ...],
    min_counts: Mapping[str, int],
) -> tuple[str, ...]:
    result: list[str] = []
    for letter in sorted(present_chars):
        placed = sum(1 for slot in correct_state if slot == letter)
        if placed < min_counts.get(letter, 1):
            result.append(letter)
    return tuple(result)


def next_fallback_guess(state: SolverState) -> str:
    unplaced = unplaced_present(
        state.present_chars, state.correct_state, state.min_counts
    )
    if unplaced and any(slot is None for slot in state.correct_state):
        return position_probe(unplaced[0], state.word_length)

    untried = sorted(state.untried_external_chars)
    if not untried:
        untried = sorted(state.untried_dictionary_chars)
    if untried and any(slot is None for slot in state.correct_state):
        return charset_probe(untried, state.word_length)

    slots: list[str | None] = list(state.correct_state)
    for letter in sorted(state.present_chars):
        for i in range(state.word_length):
            if slots[i] is None and can_place(letter, i, state.present_state):
                slots[i] = letter
                break
    return "".join(slot if slot is not None else "a" for slot in slots)
