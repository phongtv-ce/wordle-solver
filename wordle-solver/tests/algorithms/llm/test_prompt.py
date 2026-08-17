import pytest

from solver.algorithms.llm.prompt import build_prompt, extract_guess, format_history
from solver.types import SlotFeedback
from tests.helpers import GUESS_FEEDBACK


def test_build_prompt_includes_word_length_and_history():
    prompt = build_prompt(5, "guess -> mixed")
    assert "5-letter" in prompt
    assert "guess -> mixed" in prompt
    assert "<guess>WORD</guess>" in prompt


def test_format_history_empty_and_with_feedback():
    assert format_history(()) == "(no guesses yet)"
    text = format_history((("guess", GUESS_FEEDBACK),))
    assert "guess" in text
    assert '"slot": 1' in text
    assert "correct" in text


def test_extract_guess_reads_xml_tag_and_lowercases():
    assert extract_guess("Analysis...\n<guess>JUDAS</guess>") == "judas"


def test_extract_guess_rejects_missing_tag():
    with pytest.raises(ValueError):
        extract_guess("I think the word is judas")


def test_format_history_slot_shape_matches_api():
    feedback = (
        SlotFeedback(slot=0, guess="g", result="absent"),
        SlotFeedback(slot=1, guess="u", result="correct"),
    )
    text = format_history((("gu", feedback),))
    assert '"guess": "g"' in text
    assert '"result": "absent"' in text
