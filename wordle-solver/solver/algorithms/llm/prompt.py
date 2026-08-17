from __future__ import annotations

import json
import re
from collections.abc import Sequence

from solver.types import Feedback

PROMPT_TEMPLATE = """# Role

You are an expert word puzzle solver. Your goal is to deduce the hidden {WORD_LENGTH}-letter English word in the fewest attempts possible by analyzing the API response history from previous guesses.

## Understanding the API Response Format

For each guess, the API returns a list of objects containing the index (`slot`), the letter (`guess`), and the match status (`result`).

### Status Meanings:

- **`correct`**: The letter at this position is in the target word and in the right spot.
- **`present`**: The letter is in the target word, but located in a DIFFERENT position.
- **`absent`**: The letter is not in the target word (or is an extra occurrence of a letter already used up).

## Strategy Guidelines

1. **Length Constraint**: Your guess must be a valid English word containing **EXACTLY {WORD_LENGTH} letters**.
2. **Elimination**: Strictly avoid letters marked as `absent` in future guesses.
3. **Inclusion**: You MUST include all letters marked as `correct` and `present` in your subsequent guesses.
4. **Positioning**: Respect `correct` positions and place `present` letters in _new_ positions (do not repeat them in the slot they failed).
5. **Information Gain**: Early guesses should prioritize testing common vowels and frequent consonants to narrow down possibilities quickly.

## Current Game State & History

- **Target Word Length**: {WORD_LENGTH} letters
- **History of Previous Guesses & API Responses**:

```
{GAME_HISTORY}
```

## Output Requirements

Your response must follow this exact format:

1. **Analysis**: Briefly analyze the API responses from previous guesses (confirmed letters, eliminated letters, and remaining positions).
2. **Candidate Selection**: Think through 1-2 possible valid {WORD_LENGTH}-letter words.
3. **Final Guess**: Provide ONLY your next {WORD_LENGTH}-letter guess word in uppercase inside the following XML tag:
   <guess>WORD</guess>
"""

_GUESS_TAG = re.compile(r"<guess>\s*([a-zA-Z]+)\s*</guess>", re.IGNORECASE)


def format_history(entries: Sequence[tuple[str, Feedback]]) -> str:
    if not entries:
        return "(no guesses yet)"
    blocks: list[str] = []
    for word, feedback in entries:
        payload = [
            {"slot": slot.slot, "guess": slot.guess, "result": slot.result}
            for slot in feedback
        ]
        blocks.append(f"{word}\n{json.dumps(payload)}")
    return "\n\n".join(blocks)


def build_prompt(word_length: int, game_history: str) -> str:
    return PROMPT_TEMPLATE.replace("{WORD_LENGTH}", str(word_length)).replace(
        "{GAME_HISTORY}", game_history
    )


def extract_guess(response: str) -> str:
    match = _GUESS_TAG.search(response)
    if match is None:
        raise ValueError("LLM response is missing a <guess>WORD</guess> tag")
    return match.group(1).lower()
