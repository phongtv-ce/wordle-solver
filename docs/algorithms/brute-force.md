## Input:

- N: The length of the word to be guessed.

## Algorithm:

### 1. Identify the set of characters present in the word

- Method: Try sequences of N distinct characters chosen from the 26 letters of the alphabet (a–z) one by one until all N characters appearing in the word are found (e.g., the set {a, b, c, d}).

- Number of attempts: 26/N attempts (since each attempt checks N distinct characters).

### 2. Determine the exact position of each character

- Method: For each newly found character, try repeating that character across all positions (e.g., aaaaa, then bbbbb, etc.) and use the feedback to determine its exact position in the word.

- Number of attempts: Each character takes a maximum of 1 attempt. With N characters, the total number of attempts in this step is N times.

> Worst-case: 27 attempts (find the characters set (1) + repeating all character(26))
