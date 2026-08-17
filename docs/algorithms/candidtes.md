## Narrow down the candidates set, which consists of the dictionary words matching the known constraints, until the exact target word is identified.

### 1. It is necessary to store 4 groups of states:

- `presentChars`: The set of characters confirmed to be in the answer (correct + present).
- `absentChars`: The set of characters confirmed not to be in the answer.
- `untriedDictionaryChars`: The set of characters that have not been tried yet but appear in the dictionary's candidates set.
- `untriedExternalChars`: The set of characters that have not been tried yet and do not belong to the set of characters appearing in the dictionary's candidates.

- Initial state:
  - `untriedExternalChars = a-z`
  - `untriedDictionaryChars = []`
  - `presentChars = []`
  - `absentChars = []`

In addition to the 4 groups above, 2 more states need to be stored for each position of the word:

- `presentState`: An array of length N, corresponding to the N positions in the word. Each element is a set of characters.
  - `presentState[i]` contains the characters confirmed to be in the answer but definitely not at position i.
  - Example:
    - `presentState = [['a', 'b'], [], ['c']]`

  - This means:
    - Position 0: a and b are in the answer but not at position 0.
    - Position 1: no present information yet.
    - Position 2: c is in the answer but not at position 2.

- `correctState`: An array of length N, used to store positions that have been correctly identified.
  - Example:
    - `correctState = ['a', None, 'c', None]`

  - Where:
    - `correctState[i] = char`: The character at position i has been confirmed as correct.
    - `correctState[i] = None`: Position i has not been confirmed as correct yet.

- Initialization:
  - `correctState = [None, None, ..., None]`

### 2. After each prediction API call, the following steps must be performed:

- Update `presentState` and `correctState` based on the API response.
  - If the API returns `present` for a character at position i, add that character to `presentState[i]`.
  - If the API returns `correct` for a character at position i, update `correctState[i] = char`.

- Update `presentChars` and `absentChars`.
  - `presentChars` contains all characters identified as present or correct.
  - `absentChars` contains all characters identified as absent.

- Update `candidates`.
  - Use all current states including `correctState`, `presentState`, `presentChars`, and `absentChars` to filter the dictionary again.
  - Candidates must only contain words that satisfy all current constraints.

- Update `untriedDictionaryChars`.
  - Based on the current candidates, get all characters appearing in the candidates that have never been tried and have not been identified as present, correct, or absent.

- Update `untriedExternalChars`.
  - Starting from the set `a-z`, remove characters that have been tried or identified as present, correct, or absent.

**General processing flow:**

**API Prediction Response**

→ Update `presentState` / `correctState`
→ Update `presentChars` / `absentChars`

→ Update `candidates`

→ Update `untriedDictionaryChars`
→ Update `untriedExternalChars`

### 3. The ultimate goal is to continuously narrow down the candidates after each prediction until the exact answer is identified.

**Current step is generating a guess to further narrow down the candidates.**

#### If `candidates > 2`:

- The guess is created by selecting N characters in the following priority order:
  - Prioritize using `untriedDictionaryChars`. Sequentially take characters from `untriedDictionaryChars` and fill them into positions in the following priority order:
    - First, positions where `correctState[i]` is not None. Using this position for getting more information.
    - Next, positions where `presentState[i]` is not empty. Because present is not correct position, we can use that for getting other info.
    - Finally, the remaining positions.

  > The purpose is to reuse characters known to be in the answer but try them at different positions to gather more information.
  - If there are still not enough N characters after the above step, continue using `presentChars`.
    - Find a character in `presentChars` that does not appear in all candidates. Example:

      ```py
      candidates = [ab, ac];
      presentChars = [a, b, c];
      ```

      Character a appears in all candidates, while b only appears in ab and c only appears in ac. Therefore, b or c can be selected to be included in the guess. This make sure at the next guessing, we can narrow down the candidates.

    - Sequentially take characters from `presentChars` and fill them into positions i where that character does not appear in `presentState[i]`.

- The purpose of this step is to select characters capable of distinguishing between candidates and helping to narrow down candidates faster.

→ **Guess word:**

#### If candidates are only `<= 2` words remaining

- There is no need to generate a guess according to the steps above.
- Choose 1 candidate that matches the most states and directly use that candidate as the guess.

## Fallback

If our dictionary doesn't contain the target word, we will use a brute-force approach to solve it, and we can reuse previous guess history.
