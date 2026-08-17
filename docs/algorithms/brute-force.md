## Input:

- N: The length of the word to be guessed.

## Algorithm:

### 1. Identify the set of characters present in the word

- Method: Try sequences of N distinct characters chosen from the 26 letters of the alphabet (a–z) one by one until all N characters appearing in the word are found (e.g., the set {a, b, c, d}).

- Number of attempts: 26/N attempts (since each attempt checks N distinct characters).

### 2. Determine the exact position of each character

- Method: For each newly found character, fill every **unknown** slot with that character and **keep letters already marked correct**. Use the feedback to lock the new letter’s index.

  Example (target `pleurisy`, after `e` is locked at slot 2):

  - Probe `i` as `iieiiiii`, not `iiiiiiii`.
  - Slot 2 stays `e` (`correct`); remaining slots test `i`.

  Keeping known-correct letters means later probes can finish the word in fewer guesses, because `is_solved` checks the current guess row — overwriting a known slot would force extra reconstruction attempts.

- Number of attempts: Each remaining unplaced character takes a maximum of 1 attempt. With N characters, the total number of attempts in this step is at most N.

> Worst-case: 27 attempts (find the characters set (1) + repeating all character(26)). Average is lower when correct slots are reused.
