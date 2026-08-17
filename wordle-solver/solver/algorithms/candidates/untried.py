from collections.abc import Sequence

from solver.types import Feedback


def candidate_alphabet(candidates: Sequence[str]) -> frozenset[str]:
    letters: set[str] = set()
    for word in candidates:
        letters.update(word)
    return frozenset(letters)


def update_tried_chars(tried_chars: frozenset[str], feedback: Feedback) -> frozenset[str]:
    return tried_chars | frozenset(slot.guess for slot in feedback)


def known_chars(present_chars: frozenset[str], absent_chars: frozenset[str]) -> frozenset[str]:
    return present_chars | absent_chars


def update_untried_dictionary_chars(
    candidate_letters: frozenset[str],
    tried_chars: frozenset[str],
    known: frozenset[str],
) -> frozenset[str]:
    return candidate_letters - tried_chars - known


def update_untried_external_chars(
    letters: frozenset[str],
    candidate_letters: frozenset[str],
    tried_chars: frozenset[str],
    known: frozenset[str],
) -> frozenset[str]:
    return letters - candidate_letters - tried_chars - known
