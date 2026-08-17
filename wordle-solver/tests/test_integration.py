from solver.algorithms.candidates import apply_feedback, initial_state, next_guess
from solver.feedback import is_solved, parse_feedback
from tests.helpers import wordle_feedback_raw


def test_candidates_algorithm_solves_known_target():
    target = "plane"
    dictionary = (
        "crane",
        "plane",
        "trace",
        "pleat",
        "learn",
        "panel",
        "apple",
        "grade",
        "stone",
        "words",
    )
    state = initial_state(5, dictionary)

    for _ in range(15):
        guess = next_guess(state)
        raw = wordle_feedback_raw(guess, target)
        feedback = parse_feedback(raw)
        if is_solved(feedback):
            assert guess == target
            return
        state = apply_feedback(state, feedback)

    raise AssertionError("candidates algorithm did not solve within 15 guesses")


def test_fallback_fills_present_slots_with_correct_and_present_letters():
    """Near-miss dictionary word: only test remaining holes, using extra greens."""
    target = "counterintuitive"
    dictionary = ("counterinvective",)
    state = initial_state(16, dictionary)
    seen: list[str] = []

    for _ in range(40):
        guess = next_guess(state)
        assert guess not in seen, f"stuck repeating {guess!r} after {seen}"
        seen.append(guess)
        raw = wordle_feedback_raw(guess, target)
        feedback = parse_feedback(raw)
        if is_solved(feedback):
            assert guess == target
            return
        state = apply_feedback(state, feedback)

    raise AssertionError(f"did not solve; guesses={seen}")
