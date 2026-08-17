from dataclasses import dataclass
from typing import Literal, Mapping

LetterResult = Literal["correct", "present", "absent"]


@dataclass(frozen=True)
class SlotFeedback:
    slot: int
    guess: str
    result: LetterResult


Feedback = tuple[SlotFeedback, ...]


@dataclass(frozen=True)
class SolverState:
    word_length: int
    present_chars: frozenset[str]
    absent_chars: frozenset[str]
    untried_dictionary_chars: frozenset[str]
    untried_external_chars: frozenset[str]
    present_state: tuple[frozenset[str], ...]
    correct_state: tuple[str | None, ...]
    min_counts: Mapping[str, int]
    max_counts: Mapping[str, int]
    tried_chars: frozenset[str]
    candidates: tuple[str, ...]


def alphabet() -> frozenset[str]:
    return frozenset("abcdefghijklmnopqrstuvwxyz")


def empty_present_state(n: int) -> tuple[frozenset[str], ...]:
    return tuple(frozenset() for _ in range(n))


def empty_correct_state(n: int) -> tuple[str | None, ...]:
    return tuple(None for _ in range(n))
