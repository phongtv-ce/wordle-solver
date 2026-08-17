from collections.abc import Mapping, Sequence


def matches_correct_state(word: str, correct_state: tuple[str | None, ...]) -> bool:
    for i, letter in enumerate(correct_state):
        if letter is not None and word[i] != letter:
            return False
    return True


def matches_present_state(word: str, present_state: tuple[frozenset[str], ...]) -> bool:
    for i, forbidden in enumerate(present_state):
        if word[i] in forbidden:
            return False
    return True


def matches_present_chars(
    word: str,
    present_chars: frozenset[str],
    min_counts: Mapping[str, int],
) -> bool:
    for letter in present_chars:
        if letter not in word:
            return False
    for letter, minimum in min_counts.items():
        if word.count(letter) < minimum:
            return False
    return True


def matches_absent_chars(
    word: str,
    absent_chars: frozenset[str],
    max_counts: Mapping[str, int],
) -> bool:
    for letter in absent_chars:
        if letter in word:
            return False
    for letter, maximum in max_counts.items():
        if word.count(letter) > maximum:
            return False
    return True


def word_matches(
    word: str,
    correct_state: tuple[str | None, ...],
    present_state: tuple[frozenset[str], ...],
    present_chars: frozenset[str],
    absent_chars: frozenset[str],
    min_counts: Mapping[str, int],
    max_counts: Mapping[str, int],
) -> bool:
    return (
        matches_correct_state(word, correct_state)
        and matches_present_state(word, present_state)
        and matches_present_chars(word, present_chars, min_counts)
        and matches_absent_chars(word, absent_chars, max_counts)
    )


def filter_candidates(
    candidates: Sequence[str],
    correct_state: tuple[str | None, ...],
    present_state: tuple[frozenset[str], ...],
    present_chars: frozenset[str],
    absent_chars: frozenset[str],
    min_counts: Mapping[str, int],
    max_counts: Mapping[str, int],
) -> tuple[str, ...]:
    return tuple(
        word
        for word in candidates
        if word_matches(
            word,
            correct_state,
            present_state,
            present_chars,
            absent_chars,
            min_counts,
            max_counts,
        )
    )
