from collections.abc import Mapping, Sequence

from solver.algorithms.candidates.placement import can_place
from solver.types import Feedback, SolverState


def is_position_probe_feedback(
    feedback: Feedback,
    correct_state: Sequence[str | None] = (),
) -> bool:
    return position_probe_letter(feedback, correct_state) is not None


def position_probe_letter(
    feedback: Feedback,
    correct_state: Sequence[str | None] = (),
) -> str | None:
    """Return the repeated letter if this guess is a position probe, else None.

    A position probe fills every still-unknown slot with the same letter and
    keeps letters already locked in ``correct_state``.
    """
    if not feedback:
        return None
    unknown: list[str] = []
    for slot in feedback:
        known = correct_state[slot.slot] if slot.slot < len(correct_state) else None
        if known is not None:
            continue
        unknown.append(slot.guess)
    if not unknown:
        return None
    letter = unknown[0]
    if all(guessed == letter for guessed in unknown):
        return letter
    return None


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


def position_probe(
    letter: str,
    n: int,
    correct_state: Sequence[str | None] = (),
) -> str:
    return "".join(
        correct_state[i] if i < len(correct_state) and correct_state[i] is not None else letter
        for i in range(n)
    )


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
    # Step 1: discover letters with untried external (non-dictionary) chars first.
    untried = sorted(state.untried_external_chars)
    if not untried:
        untried = sorted(state.untried_dictionary_chars)
    if untried:
        return charset_probe(untried, state.word_length)

    # Step 2: position-probe each discovered letter at most once.
    unplaced = unplaced_present(
        state.present_chars, state.correct_state, state.min_counts
    )
    for letter in unplaced:
        if letter not in state.position_probed_chars:
            return position_probe(letter, state.word_length, state.correct_state)

    if any(slot is None for slot in state.correct_state):
        for letter in sorted(state.present_chars):
            if letter not in state.position_probed_chars:
                return position_probe(letter, state.word_length, state.correct_state)

    slots: list[str | None] = list(state.correct_state)
    for letter in sorted(state.present_chars):
        for i in range(state.word_length):
            if slots[i] is None and can_place(letter, i, state.present_state):
                slots[i] = letter
                break
    return "".join(slot if slot is not None else "a" for slot in slots)
