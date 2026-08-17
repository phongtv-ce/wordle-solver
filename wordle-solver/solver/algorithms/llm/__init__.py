from collections.abc import Callable, Sequence

from solver.algorithms.candidates.state import apply_feedback, initial_state
from solver.algorithms.llm.prompt import build_prompt, extract_guess, format_history
from solver.types import Feedback, SolverState

NAME = "llm"

CompleteFn = Callable[[str], str]


def next_guess(
    state: SolverState,
    *,
    history: Sequence[tuple[str, Feedback]] = (),
    complete: CompleteFn | None = None,
) -> str:
    if complete is None:
        raise NotImplementedError(
            "LLM algorithm needs a complete(prompt) callback; set WORDLE_ALGORITHM=candidates for now"
        )
    prompt = build_prompt(state.word_length, format_history(history))
    return extract_guess(complete(prompt))


__all__ = [
    "NAME",
    "apply_feedback",
    "build_prompt",
    "extract_guess",
    "format_history",
    "initial_state",
    "next_guess",
]
