import pytest

from solver.algorithms import get_algorithm
from solver.algorithms import brute_force, candidates, llm


def test_get_algorithm_returns_each_named_module():
    assert get_algorithm("candidates") is candidates
    assert get_algorithm("brute-force") is brute_force
    assert get_algorithm("LLM") is llm


def test_get_algorithm_rejects_unknown_name():
    with pytest.raises(ValueError, match="unknown algorithm"):
        get_algorithm("magic")


def test_each_algorithm_exposes_the_shared_entrypoint():
    for module in (candidates, brute_force, llm):
        assert hasattr(module, "NAME")
        assert hasattr(module, "initial_state")
        assert hasattr(module, "apply_feedback")
        assert hasattr(module, "next_guess")
