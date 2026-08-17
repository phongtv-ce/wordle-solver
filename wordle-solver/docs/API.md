# Wordle guess API

This document describes the HTTP contract between `WordleClient` and the remote puzzle API.

## Request

- **Method:** `GET`
- **URL:** `WORDLE_API_ENTRYPOINT` (no trailing slash required; config strips it)
- **Headers:**
  - `Accept: application/json`
  - `Authorization: Bearer {WORDLE_API_KEY}` — only when `WORDLE_API_KEY` is set

**Query parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `guess` | string | yes | Lowercase guess word |
| `size` | int | yes | Word length; must equal `len(guess)` |

Example:

```http
GET https://wordle.votee.dev:8000/daily?guess=guess&size=5
```

The client lowercases the guess before sending and sets `size` from `WORDLE_WORD_LENGTH`. If `len(guess) != size`, the client raises before calling the API.

## Response

A JSON **array** with one object per letter slot. Each object has:

| Field | Type | Description |
|-------|------|-------------|
| `slot` | int | Zero-based index `0 .. word_length - 1` |
| `guess` | string | Single letter that was guessed at that slot |
| `result` | string | One of `correct`, `present`, `absent` |

Example (guess `guess` against target `judas`):

```json
[
  {"slot": 0, "guess": "g", "result": "absent"},
  {"slot": 1, "guess": "u", "result": "correct"},
  {"slot": 2, "guess": "e", "result": "absent"},
  {"slot": 3, "guess": "s", "result": "present"},
  {"slot": 4, "guess": "s", "result": "correct"}
]
```

The client rejects non-list JSON, invalid UTF-8, and transport errors (`WordleApiError`).

## Result semantics

### `correct`

The letter at `slot` belongs in the target word **at that index**.

Solver effect:

- `correct_state[slot] = letter`
- Letter added to `present_chars`
- `min_counts[letter]` increases (duplicate-aware)

### `present`

The letter at `slot` is in the target word but **not** at that index.

Solver effect:

- Letter added to `present_state[slot]` (forbidden at this index later)
- Letter added to `present_chars`
- `min_counts[letter]` increases

### `absent`

The letter is not in the target, **or** it is an extra occurrence beyond what the target contains.

Solver effect:

- If the letter had no `correct`/`present` in the same guess → `absent_chars`
- If the letter also had `correct`/`present` in the same guess → exact count (`max = min`), letter stays in `present_chars`

## Duplicate letters

When the same letter appears multiple times in one guess:

1. Count how many slots are `correct` or `present` for that letter → minimum count in the target.
2. If any slot for that letter is `absent`, that minimum is also the **maximum** (exact count).
3. If all slots for that letter are `absent`, the letter is fully absent (`max = 0`).

Example: guess `speed` against `speed` — both `e` slots `present`/`correct`; no conflict.

Example: guess `guess` with slot 3 `s` = `present`, slot 4 `s` = `correct` — target has at least two `s`; if another `s` were `absent` in the same row, count would be exact.

## Solved condition

A puzzle is solved when **every** slot in the latest feedback has `result == "correct"`. The driver checks this with `is_solved(feedback)` before applying feedback to state.

## Parsing

`parse_feedback(raw)` converts the API list into `Feedback`: a tuple of `SlotFeedback(slot, guess, result)` with lowercase letters and validated slots/results. Invalid API data raises an error at parse time rather than silently corrupting state.
