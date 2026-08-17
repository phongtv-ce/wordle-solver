from solver.types import alphabet, empty_correct_state, empty_present_state
from tests.helpers import ALPHABET


def test_alphabet_is_lowercase_a_to_z():
    assert alphabet() == ALPHABET
    assert len(alphabet()) == 26


def test_empty_present_state_has_n_empty_sets():
    assert empty_present_state(5) == (
        frozenset(),
        frozenset(),
        frozenset(),
        frozenset(),
        frozenset(),
    )


def test_empty_present_state_zero_length():
    assert empty_present_state(0) == ()


def test_empty_correct_state_has_n_nones():
    assert empty_correct_state(4) == (None, None, None, None)


def test_empty_correct_state_zero_length():
    assert empty_correct_state(0) == ()
