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
        "candidates": (),
    }
    values.update(overrides)
    return SolverState(**values)
