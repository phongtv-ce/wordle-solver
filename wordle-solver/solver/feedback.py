from collections.abc import Mapping, Sequence

from solver.types import Feedback, LetterResult, SlotFeedback

VALID_RESULTS = frozenset({"correct", "present", "absent"})


def parse_feedback(raw: Sequence[Mapping[str, object]]) -> Feedback:
    result: list[SlotFeedback] = []
    for item in raw:
        if "slot" not in item or "guess" not in item or "result" not in item:
            raise ValueError("feedback item must have slot, guess, and result")
        slot = item["slot"]
        guess = item["guess"]
        res = item["result"]
        if not isinstance(slot, int):
            raise ValueError(f"invalid slot: {slot!r}")
        if not isinstance(guess, str) or len(guess) != 1:
            raise ValueError(f"invalid guess letter: {guess!r}")
        if not isinstance(res, str) or res not in VALID_RESULTS:
            raise ValueError(f"invalid result: {res!r}")
        result.append(SlotFeedback(slot=slot, guess=guess.lower(), result=res))
    return tuple(result)


def is_solved(feedback: Feedback) -> bool:
    return all(slot.result == "correct" for slot in feedback)


def update_correct_state(
    correct_state: tuple[str | None, ...],
    feedback: Feedback,
) -> tuple[str | None, ...]:
    updated = list(correct_state)
    for slot in feedback:
        if slot.result == "correct":
            updated[slot.slot] = slot.guess
    return tuple(updated)


def update_present_state(
    present_state: tuple[frozenset[str], ...],
    feedback: Feedback,
) -> tuple[frozenset[str], ...]:
    updated = [set(s) for s in present_state]
    for slot in feedback:
        if slot.result == "present":
            updated[slot.slot].add(slot.guess)
    return tuple(frozenset(s) for s in updated)


def letter_outcomes(
    feedback: Feedback,
) -> tuple[frozenset[str], frozenset[str], Mapping[str, int], Mapping[str, int]]:
    newly_present: set[str] = set()
    newly_absent: set[str] = set()
    min_delta: dict[str, int] = {}
    max_delta: dict[str, int] = {}
    present_count: dict[str, int] = {}
    has_absent: set[str] = set()

    for slot in feedback:
        letter = slot.guess
        if slot.result in ("correct", "present"):
            newly_present.add(letter)
            present_count[letter] = present_count.get(letter, 0) + 1
        elif slot.result == "absent":
            has_absent.add(letter)

    for letter, count in present_count.items():
        min_delta[letter] = count
        if letter in has_absent:
            max_delta[letter] = count

    for letter in has_absent:
        if letter not in present_count:
            newly_absent.add(letter)
            max_delta[letter] = 0

    return frozenset(newly_present), frozenset(newly_absent), min_delta, max_delta


def merge_counts(
    old_min: Mapping[str, int],
    old_max: Mapping[str, int],
    delta_min: Mapping[str, int],
    delta_max: Mapping[str, int],
    n: int,
) -> tuple[Mapping[str, int], Mapping[str, int]]:
    letters = set(old_min) | set(old_max) | set(delta_min) | set(delta_max)
    new_min: dict[str, int] = {}
    new_max: dict[str, int] = {}
    for letter in letters:
        new_min[letter] = max(old_min.get(letter, 0), delta_min.get(letter, 0))
        new_max[letter] = min(old_max.get(letter, n), delta_max.get(letter, n))
    return new_min, new_max


def update_present_chars(
    present_chars: frozenset[str],
    newly_present: frozenset[str],
) -> frozenset[str]:
    return present_chars | newly_present


def update_absent_chars(
    absent_chars: frozenset[str],
    newly_absent: frozenset[str],
    present_chars: frozenset[str],
) -> frozenset[str]:
    return (absent_chars | newly_absent) - present_chars
