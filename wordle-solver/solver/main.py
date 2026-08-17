from __future__ import annotations

import argparse
import sys

from solver.algorithms import get_algorithm
from solver.api import WordleClient
from solver.config import load_config
from solver.dictionary import load_dictionary
from solver.display_log import log_guess_attempt, log_guess_attempt_header
from solver.feedback import is_solved, parse_feedback


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Solve Wordle against a remote guess API.")
    parser.add_argument(
        "--algorithm",
        choices=("candidates", "brute_force", "llm"),
        help="Override WORDLE_ALGORITHM from .env",
    )
    parser.add_argument("--env-file", help="Path to a .env file")
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show colored feedback logs after each guess",
    )
    args = parser.parse_args(argv)

    config = load_config(env_file=args.env_file)
    algorithm_name = args.algorithm or config.algorithm
    algorithm = get_algorithm(algorithm_name)
    client = WordleClient(config)
    dictionary = load_dictionary(config.dictionary_path)
    state = algorithm.initial_state(config.word_length, dictionary)

    if args.verbose:
        log_guess_attempt_header()

    attempt = 0
    for _ in range(config.max_guesses):
        attempt += 1
        guess = algorithm.next_guess(state)
        raw = client.guess(guess)
        feedback = parse_feedback(raw)
        state = algorithm.apply_feedback(state, feedback)
        if args.verbose:
            log_guess_attempt(attempt, feedback, state)
        if is_solved(feedback):
            if args.verbose:
                return 0
            print(f"{attempt} | {guess}")
            return 0

    print("max guesses reached without solving", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
