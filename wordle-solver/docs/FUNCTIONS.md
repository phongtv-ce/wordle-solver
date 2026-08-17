# Function reference

Every pure function in the solver: **purpose**, **input**, **output**. Functions raise `NotImplementedError` until implemented; behavior is defined by tests in `tests/`.

Convention: all letter sets use lowercase `a-z`. Guesses are length `N` lowercase strings.

---

## Types (`solver/types.py`)

### `SolverState`

Immutable game state. Fields documented in [ARCHITECTURE.md](ARCHITECTURE.md#solverstate).

### `SlotFeedback` / `Feedback`

- `SlotFeedback(slot, guess, result)` — one letter result from the API.
- `Feedback` — `tuple[SlotFeedback, ...]` of length `N`.

### `alphabet()`

- **Purpose:** Full English letter set for untried-external initialization.
- **Input:** none
- **Output:** `frozenset[str]` — `{"a", ..., "z"}`

### `empty_present_state(n)`

- **Purpose:** Initialize per-slot “wrong position” sets.
- **Input:** `n: int` — word length
- **Output:** `tuple[frozenset[str], ...]` — length `n`, each empty

### `empty_correct_state(n)`

- **Purpose:** Initialize confirmed-letter slots.
- **Input:** `n: int`
- **Output:** `tuple[str | None, ...]` — length `n`, all `None`

---

## Feedback (`solver/feedback.py`)

### `parse_feedback(raw)`

- **Purpose:** Normalize API JSON into typed `Feedback`.
- **Input:** `raw: Sequence[Mapping[str, object]]` — API slot list
- **Output:** `Feedback` — lowercase letters, valid slots/results. Raises on invalid data.

### `is_solved(feedback)`

- **Purpose:** Detect a winning guess.
- **Input:** `feedback: Feedback`
- **Output:** `bool` — `True` if every slot is `correct`

### `update_correct_state(correct_state, feedback)`

- **Purpose:** Lock letters at known indexes.
- **Input:** current `correct_state`, `feedback`
- **Output:** new `correct_state`; `correct` slots set; never clears existing correct slots

### `update_present_state(present_state, feedback)`

- **Purpose:** Record letters that are in the word but not at this index.
- **Input:** current `present_state`, `feedback`
- **Output:** new `present_state`; `present` letters added to that slot’s set

### `letter_outcomes(feedback)`

- **Purpose:** Classify this guess’s letters, including duplicate min/max counts.
- **Input:** `feedback: Feedback`
- **Output:** `(newly_present, newly_absent, min_counts_delta, max_counts_delta)`
  - `newly_present` — letters with any `correct` or `present`
  - `newly_absent` — letters that are **only** `absent`
  - deltas follow duplicate rules in [API.md](API.md)

### `merge_counts(old_min, old_max, delta_min, delta_max, n)`

- **Purpose:** Tighten letter-count bounds across guesses.
- **Input:** previous min/max maps, this-guess deltas, word length `n`
- **Output:** `(new_min, new_max)` — `max(old, delta)` / `min(old, delta)`; default max `n`

### `update_present_chars(present_chars, newly_present)`

- **Purpose:** Accumulate letters known to appear in the target.
- **Input:** previous set, this-guess present/correct letters
- **Output:** `frozenset[str]` — union

### `update_absent_chars(absent_chars, newly_absent, present_chars)`

- **Purpose:** Accumulate fully-absent letters; no overlap with present.
- **Input:** previous absent, only-absent letters, **updated** present set
- **Output:** `(absent | newly_absent) - present_chars`

---

## Candidate filter (`solver/algorithms/candidates/filter.py`)

### `matches_correct_state(word, correct_state)`

- **Purpose:** Word agrees with known-correct slots.
- **Input:** `word: str`, `correct_state`
- **Output:** `bool`

### `matches_present_state(word, present_state)`

- **Purpose:** Word does not place a letter in a forbidden slot.
- **Input:** `word`, `present_state`
- **Output:** `bool` — `word[i] not in present_state[i]` for all `i`

### `matches_present_chars(word, present_chars, min_counts)`

- **Purpose:** Word contains required letters with enough duplicates.
- **Input:** `word`, `present_chars`, `min_counts`
- **Output:** `bool`

### `matches_absent_chars(word, absent_chars, max_counts)`

- **Purpose:** No forbidden letters or excess duplicates.
- **Input:** `word`, `absent_chars`, `max_counts`
- **Output:** `bool`

### `word_matches(word, correct_state, present_state, present_chars, absent_chars, min_counts, max_counts)`

- **Purpose:** Apply all constraints to one word.
- **Input:** word + six constraint fields
- **Output:** `bool` — AND of the four matchers

### `filter_candidates(candidates, ...)`

- **Purpose:** Remove dictionary words that no longer fit feedback.
- **Input:** previous `candidates` + constraint fields (same as `word_matches`)
- **Output:** `tuple[str, ...]` — matching subsequence (does not reload full dictionary)

---

## Untried sets (`solver/algorithms/candidates/untried.py`)

### `candidate_alphabet(candidates)`

- **Purpose:** Letters that appear in at least one remaining candidate.
- **Input:** `candidates: Sequence[str]`
- **Output:** `frozenset[str]`

### `update_tried_chars(tried_chars, feedback)`

- **Purpose:** Remember letters already guessed.
- **Input:** previous tried set, `feedback`
- **Output:** union with all guessed letters

### `known_chars(present_chars, absent_chars)`

- **Purpose:** Letters already classified (not “untried”).
- **Input:** present set, absent set
- **Output:** union

### `update_untried_dictionary_chars(candidate_letters, tried_chars, known)`

- **Purpose:** Unknown letters still in the candidate alphabet.
- **Input:** candidate alphabet, tried, known (present ∪ absent)
- **Output:** `candidate_letters - tried - known`

### `update_untried_external_chars(letters, candidate_letters, tried_chars, known)`

- **Purpose:** Unused letters outside the candidate alphabet.
- **Input:** usually `alphabet()`, candidate alphabet, tried, known
- **Output:** `letters - candidate_letters - tried - known`

---

## State pipeline (`solver/algorithms/candidates/state.py`)

### `filter_by_length(dictionary, n)`

- **Purpose:** Restrict dictionary to puzzle length.
- **Input:** word list, `n`
- **Output:** lowercase unique words with `len == n`, stable order

### `initial_state(n, dictionary)`

- **Purpose:** First `SolverState` for the candidates algorithm.
- **Input:** word length, dictionary
- **Output:** `SolverState` with empty constraints, filtered candidates, untried sets filled

### `apply_feedback(state, feedback)`

- **Purpose:** Produce next state from one API response.
- **Input:** `SolverState`, `Feedback`
- **Output:** new `SolverState` in order:
  1. position updates
  2. present/absent/counts
  3. `filter_candidates`
  4. `update_tried_chars`
  5. untried set updates

---

## Guess generation (`solver/algorithms/candidates/guess.py`)

### `next_guess(state)`

- **Purpose:** Next string to send to the API (candidates algorithm).
- **Input:** `SolverState`
- **Output:** `str` length `N`
  - `0` candidates → fallback
  - `≤ 2` candidates → `select_candidate_guess`
  - else → `build_probe_guess`

### `position_priority(correct_state, present_state)`

- **Purpose:** Slot fill order for probes (overwrite known-correct first).
- **Input:** `correct_state`, `present_state`
- **Output:** `tuple[int, ...]` — indices ordered: correct slots → present slots → rest

### `chars_not_universal(present_chars, candidates)`

- **Purpose:** Present letters that split the candidate set.
- **Input:** `present_chars`, `candidates`
- **Output:** sorted `tuple[str, ...]` — letters not in every candidate

### `can_place(letter, index, present_state)`

- **Purpose:** Letter is allowed at this slot.
- **Input:** letter, index, `present_state`
- **Output:** `bool` — `letter not in present_state[index]`

### `place_letters(slots, letters, order, present_state)`

- **Purpose:** Fill empty slots from a letter list in priority order.
- **Input:** partial guess (`None` = empty), letters, slot order, `present_state`
- **Output:** new slot tuple; skips letters with no legal slot

### `build_probe_guess(state)`

- **Purpose:** Information-gain guess while many candidates remain.
- **Input:** `SolverState` with `len(candidates) > 2`
- **Output:** `str` — filled from untried dictionary → discriminating present → other present → external → pad

### `score_candidate(word, correct_state, present_state, present_chars)`

- **Purpose:** Rank a remaining candidate.
- **Input:** one word + constraint fields
- **Output:** `int` — +2 per matching correct slot, +1 per present letter, +1 per respected present slot

### `select_candidate_guess(candidates, correct_state, present_state, present_chars)`

- **Purpose:** Guess a real dictionary word when 1–2 remain.
- **Input:** 1–2 candidates + constraints
- **Output:** `str` — highest score, lexicographic tie-break

---

## Brute-force probes (`solver/algorithms/brute_force/probes.py`)

See [algorithms/brute-force.md](algorithms/brute-force.md).

### `charset_probe(untried, n)`

- **Purpose:** Find the character set (step 1).
- **Input:** unused letters, word length
- **Output:** `str` length `n` (cycles if fewer than `n` letters remain)

### `position_probe(letter, n, correct_state=())`

- **Purpose:** Repeat `letter` in unknown slots to find its position (step 2); keeps `correct_state` greens. Example: `aaaaa`, or `iieiiiii` when slot 2 is already `e`.
- **Input:** one letter, `n`, optional `correct_state`
- **Output:** `str` length `n`

### `position_probe_letter(feedback, correct_state=())`

- **Purpose:** Detect which letter a position-probe guess was testing.
- **Input:** `Feedback`, pre-guess `correct_state`
- **Output:** the repeated letter, or `None`

### `unplaced_present(present_chars, correct_state, min_counts)`

- **Purpose:** Present letters not yet fully placed in `correct_state`.
- **Input:** present set, `correct_state`, `min_counts`
- **Output:** `tuple[str, ...]`

### `next_fallback_guess(state)`

- **Purpose:** Next guess when dictionary candidates are empty.
- **Input:** `SolverState`
- **Output:** `str` —
  1. `charset_probe` while `untried_external_chars` or `untried_dictionary_chars` remain
  2. else `position_probe` once per present letter not in `position_probed_chars` (unknown slots only)
  3. else fill holes from `present_chars` that `can_place`

---

## LLM (`solver/algorithms/llm/prompt.py`)

### `format_history(entries)`

- **Purpose:** Serialize guess history for the prompt.
- **Input:** `Sequence[tuple[str, Feedback]]` — `(guess_word, feedback)` pairs
- **Output:** `str` — human-readable blocks or `(no guesses yet)`

### `build_prompt(word_length, game_history)`

- **Purpose:** Fill the LLM prompt template.
- **Input:** `word_length`, formatted history string
- **Output:** `str` — full prompt

### `extract_guess(response)`

- **Purpose:** Parse model output.
- **Input:** `response: str` — raw LLM text
- **Output:** `str` — lowercase word from `<guess>WORD</guess>`; raises if missing

### `next_guess(state, history=..., complete=...)` (`solver/algorithms/llm/__init__.py`)

- **Purpose:** LLM-driven next guess.
- **Input:** `SolverState`, optional history, `complete(prompt) -> str` callback
- **Output:** `str` — extracted guess; raises if no `complete` callback

---

## I/O (not pure — documented for context)

| Function | Module | Purpose |
|----------|--------|---------|
| `load_config` | `config.py` | Read `.env` into `AppConfig` |
| `WordleClient.guess` | `api.py` | POST guess, return raw JSON list |
| `load_dictionary` | `dictionary.py` | Read word file into `tuple[str, ...]` |
| `main` | `main.py` | CLI guess loop |

---

## Test mapping

| Test file | Functions covered |
|-----------|-------------------|
| `tests/test_types.py` | `alphabet`, `empty_present_state`, `empty_correct_state` |
| `tests/test_feedback.py` | All `solver/feedback.py` |
| `tests/algorithms/candidates/test_filter.py` | `filter.py` matchers |
| `tests/algorithms/candidates/test_untried.py` | `untried.py` |
| `tests/algorithms/candidates/test_state.py` | `state.py` |
| `tests/algorithms/candidates/test_guess.py` | `guess.py` |
| `tests/algorithms/brute_force/test_probes.py` | `probes.py` |
| `tests/algorithms/llm/test_prompt.py` | `prompt.py` |
| `tests/test_api.py` | `WordleClient` |
| `tests/test_config.py` | `load_config` |
| `tests/test_dictionary.py` | `load_dictionary` |
