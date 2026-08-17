from __future__ import annotations

from collections.abc import Sequence
from types import ModuleType
from typing import Protocol

from solver.algorithms import brute_force, candidates, llm
from solver.types import Feedback, SolverState


class Algorithm(Protocol):
    NAME: str

    def initial_state(self, n: int, dictionary: Sequence[str]) -> SolverState: ...

    def apply_feedback(self, state: SolverState, feedback: Feedback) -> SolverState: ...

    def next_guess(self, state: SolverState) -> str: ...


REGISTRY: dict[str, ModuleType] = {
    candidates.NAME: candidates,
    brute_force.NAME: brute_force,
    llm.NAME: llm,
}


def get_algorithm(name: str) -> ModuleType:
    key = name.strip().lower().replace("-", "_")
    try:
        return REGISTRY[key]
    except KeyError as exc:
        known = ", ".join(sorted(REGISTRY))
        raise ValueError(f"unknown algorithm {name!r}; choose from {known}") from exc
