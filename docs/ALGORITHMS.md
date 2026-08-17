### BRUTE FORCE

1. Identify the set of characters present in the word
2. Determine the exact position of every character by testing all possible combinations from the character set, and use the feedback results to verify correctness.

> [detail](./algorithms/brute-force.md)

### DICTIONARY CANDIDATES

1. Filter and narrow down the list of candidate words by checking against all known constraints (such as correct letter positions, present letters, and excluded letters).
2. After each feedback iteration, eliminate any dictionary words that do not match these criteria, and repeat this filtering process until only the single, exact target word remains.

> [detail](./algorithms/candidtes.md)

### LLM

1. Create a prompt incorporating necessary constraints for the LLM to guess a new word.
2. After each feedback, update the prompt with the feedback history so the LLM can guess the next word.
3. Repeat this process until the correct word is found.

> [Example Prompt](./algorithms/llm-promt.md)
