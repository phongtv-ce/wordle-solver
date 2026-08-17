from solver.config import AppConfig
from solver.types import SlotFeedback, SolverState

ALPHABET = frozenset("abcdefghijklmnopqrstuvwxyz")

GUESS_API_RAW = [
    {"slot": 0, "guess": "g", "result": "absent"},
    {"slot": 1, "guess": "u", "result": "correct"},
    {"slot": 2, "guess": "e", "result": "absent"},
    {"slot": 3, "guess": "s", "result": "present"},
    {"slot": 4, "guess": "s", "result": "correct"},
]

GUESS_FEEDBACK = (
    SlotFeedback(slot=0, guess="g", result="absent"),
    SlotFeedback(slot=1, guess="u", result="correct"),
    SlotFeedback(slot=2, guess="e", result="absent"),
    SlotFeedback(slot=3, guess="s", result="present"),
    SlotFeedback(slot=4, guess="s", result="correct"),
)

SOLVED_FEEDBACK = (
    SlotFeedback(slot=0, guess="j", result="correct"),
    SlotFeedback(slot=1, guess="u", result="correct"),
    SlotFeedback(slot=2, guess="d", result="correct"),
    SlotFeedback(slot=3, guess="a", result="correct"),
    SlotFeedback(slot=4, guess="s", result="correct"),
)


def make_config(**overrides) -> AppConfig:
    values = {
        "api_base": "https://api.example.test",
        "api_timeout_seconds": 5.0,
        "size_begin": 5,
        "size_end": 5,
        "seed_begin": None,
        "seed_end": None,
        "mode": "daily",
        "algorithm": "candidates",
        "dictionary_path": "/tmp/words.txt",
        "max_guesses": 50,
    }
    values.update(overrides)
    return AppConfig(**values)


def make_state(*, word_length: int = 5, **overrides) -> SolverState:
    values = {
        "word_length": word_length,
        "present_chars": frozenset(),
        "absent_chars": frozenset(),
        "untried_dictionary_chars": frozenset(),
        "untried_external_chars": ALPHABET,
        "present_state": tuple(frozenset() for _ in range(word_length)),
        "correct_state": tuple(None for _ in range(word_length)),
        "min_counts": {},
        "max_counts": {},
        "tried_chars": frozenset(),
        "position_probed_chars": frozenset(),
        "candidates": (),
    }
    values.update(overrides)
    return SolverState(**values)


def wordle_feedback(guess: str, target: str) -> tuple[SlotFeedback, ...]:
    """Compute standard Wordle feedback for a guess against a target word."""
    guess = guess.lower()
    target = target.lower()
    if len(guess) != len(target):
        raise ValueError("guess and target must have the same length")

    n = len(target)
    results: list[str] = ["absent"] * n
    remaining: dict[str, int] = {}
    for letter in target:
        remaining[letter] = remaining.get(letter, 0) + 1

    for i in range(n):
        if guess[i] == target[i]:
            results[i] = "correct"
            remaining[guess[i]] -= 1

    for i in range(n):
        if results[i] == "correct":
            continue
        letter = guess[i]
        if remaining.get(letter, 0) > 0:
            results[i] = "present"
            remaining[letter] -= 1

    return tuple(
        SlotFeedback(slot=i, guess=guess[i], result=results[i])
        for i in range(n)
    )


def wordle_feedback_raw(guess: str, target: str) -> list[dict[str, object]]:
    return [
        {"slot": slot.slot, "guess": slot.guess, "result": slot.result}
        for slot in wordle_feedback(guess, target)
    ]
