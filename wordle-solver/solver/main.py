from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from types import ModuleType

from solver.algorithms import get_algorithm
from solver.api import PuzzleMode, WordleApiError, WordleClient
from solver.config import AppConfig, load_config
from solver.dictionary import load_dictionary
from solver.display_log import (
    log_guess_attempt,
    log_guess_attempt_header,
    log_solve_summary_header,
    log_solve_summary_line,
)
from solver.feedback import is_solved, parse_feedback
from solver.types import Feedback, SolverState


@dataclass(frozen=True)
class SizeSolveResult:
    size: int
    solved: bool
    attempts: int
    word: str | None


def _first_guess_feedback(
    client: WordleClient,
    algorithm: ModuleType,
    state: SolverState,
    size: int,
    *,
    puzzle: PuzzleMode,
    seed: int | None,
) -> tuple[Feedback, SolverState, str] | None:
    guess = algorithm.next_guess(state)
    try:
        raw = client.guess(guess, size=size, puzzle=puzzle, seed=seed)
        feedback = parse_feedback(raw)
    except (WordleApiError, ValueError):
        return None

    state = algorithm.apply_feedback(state, feedback)
    return feedback, state, guess


def solve_puzzle_for_size(
    size: int,
    config: AppConfig,
    algorithm: ModuleType,
    dictionary: tuple[str, ...],
    client: WordleClient,
    *,
    puzzle: PuzzleMode,
    seed: int | None = None,
    verbose: bool,
) -> SizeSolveResult | None:
    state = algorithm.initial_state(size, dictionary)
    first = _first_guess_feedback(
        client, algorithm, state, size, puzzle=puzzle, seed=seed
    )
    if first is None:
        return None

    feedback, state, guess = first
    attempt = 1
    if verbose:
        log_guess_attempt(attempt, feedback, state)

    if is_solved(feedback):
        return SizeSolveResult(size=size, solved=True, attempts=attempt, word=guess)

    for _ in range(config.max_guesses - 1):
        attempt += 1
        guess = algorithm.next_guess(state)
        try:
            raw = client.guess(guess, size=size, puzzle=puzzle, seed=seed)
            feedback = parse_feedback(raw)
        except (WordleApiError, ValueError) as exc:
            print(
                f"size {size}: request failed on attempt {attempt}: {exc}",
                file=sys.stderr,
            )
            return SizeSolveResult(size=size, solved=False, attempts=attempt, word=None)

        state = algorithm.apply_feedback(state, feedback)
        if verbose:
            log_guess_attempt(attempt, feedback, state)
        if is_solved(feedback):
            return SizeSolveResult(size=size, solved=True, attempts=attempt, word=guess)

    return SizeSolveResult(size=size, solved=False, attempts=attempt, word=None)


def solve_daily_for_size(
    size: int,
    config: AppConfig,
    algorithm: ModuleType,
    dictionary: tuple[str, ...],
    client: WordleClient,
    *,
    verbose: bool,
) -> SizeSolveResult | None:
    return solve_puzzle_for_size(
        size,
        config,
        algorithm,
        dictionary,
        client,
        puzzle="daily",
        verbose=verbose,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Solve Wordle against a remote guess API.")
    parser.add_argument(
        "--algorithm",
        choices=("candidates", "brute_force", "llm"),
        help="Override WORDLE_ALGORITHM from .env",
    )
    parser.add_argument("--env-file", help="Path to a .env file")
    parser.add_argument(
        "--size-begin",
        type=int,
        help="Override WORDLE_SIZE_BEGIN (inclusive)",
    )
    parser.add_argument(
        "--size-end",
        type=int,
        help="Override WORDLE_SIZE_END (inclusive)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show colored feedback logs after each guess",
    )
    parser.add_argument(
        "--random",
        action="store_true",
        help="Use random mode (overrides WORDLE_MODE=daily)",
    )
    parser.add_argument(
        "--mode",
        choices=("daily", "random"),
        help="Override WORDLE_MODE from .env",
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="Optional seed for /random (same seed = same target word per size)",
    )
    parser.add_argument(
        "--seed-begin",
        type=int,
        help="Override WORDLE_SEED_BEGIN (inclusive; requires --random or WORDLE_SEED_END)",
    )
    parser.add_argument(
        "--seed-end",
        type=int,
        help="Override WORDLE_SEED_END (inclusive)",
    )
    args = parser.parse_args(argv)

    config = load_config(env_file=args.env_file)
    puzzle: PuzzleMode = _resolve_puzzle_mode(config.mode, args.mode, args.random)

    if args.seed is not None and puzzle != "random":
        print("--seed requires random mode (WORDLE_MODE=random or --random)", file=sys.stderr)
        return 1
    if (args.seed_begin is None) != (args.seed_end is None):
        print("--seed-begin and --seed-end must be used together", file=sys.stderr)
        return 1
    if args.size_begin is not None:
        config = _replace_config(config, size_begin=args.size_begin)
    if args.size_end is not None:
        config = _replace_config(config, size_end=args.size_end)
    if args.seed_begin is not None:
        config = _replace_config(config, seed_begin=args.seed_begin, seed_end=args.seed_end)
    if config.size_begin > config.size_end:
        print(
            f"size range invalid: begin {config.size_begin} > end {config.size_end}",
            file=sys.stderr,
        )
        return 1
    if (
        config.seed_begin is not None
        and config.seed_end is not None
        and config.seed_begin > config.seed_end
    ):
        print(
            f"seed range invalid: begin {config.seed_begin} > end {config.seed_end}",
            file=sys.stderr,
        )
        return 1

    algorithm_name = args.algorithm or config.algorithm
    algorithm = get_algorithm(algorithm_name)
    client = WordleClient(config)
    dictionary = load_dictionary(config.dictionary_path)

    if puzzle == "random":
        seeds = (args.seed,) if args.seed is not None else config.seeds()
    else:
        seeds = (None,)
    solved: list[SizeSolveResult] = []
    skipped: list[tuple[int, int | None]] = []
    failed: list[SizeSolveResult] = []

    if not args.verbose:
        show_seed_in_summary = puzzle == "random" and (
            args.seed is not None or config.seed_begin is not None
        )
        log_solve_summary_header(show_seed=show_seed_in_summary)

    for size in config.sizes():
        for seed in seeds:
            if args.verbose:
                header = f"\n--- size {size}"
                if puzzle == "random" and seed is not None:
                    header += f" (seed {seed})"
                header += " ---"
                print(header, flush=True)
                log_guess_attempt_header()

            result = solve_puzzle_for_size(
                size,
                config,
                algorithm,
                dictionary,
                client,
                puzzle=puzzle,
                seed=seed,
                verbose=args.verbose,
            )
            if result is None:
                skipped.append((size, seed))
                skip_reason = "no puzzle for this length" if puzzle == "daily" else "request failed"
                label = f"size {size}"
                if seed is not None:
                    label += f" seed {seed}"
                print(f"{label}: skipped ({skip_reason})", file=sys.stderr)
                continue

            if result.solved:
                solved.append(result)
                if args.verbose:
                    solved_label = f"size {size}"
                    if seed is not None:
                        solved_label += f" seed {seed}"
                    print(f"{solved_label}: solved in {result.attempts} | {result.word}")
                else:
                    log_solve_summary_line(
                        result.attempts,
                        result.word,
                        size,
                        seed=seed,
                    )
            else:
                failed.append(result)
                fail_label = f"size {size}"
                if seed is not None:
                    fail_label += f" seed {seed}"
                print(
                    f"{fail_label}: max guesses reached without solving",
                    file=sys.stderr,
                )

    if skipped:
        skipped_labels = []
        for size, seed in skipped:
            label = str(size)
            if seed is not None:
                label += f"/{seed}"
            skipped_labels.append(label)
        print(
            f"skipped puzzles (no puzzle): {', '.join(skipped_labels)}",
            file=sys.stderr,
        )
    if solved:
        print(
            f"solved {len(solved)} puzzle(s): "
            + ", ".join(f"{r.size}={r.word}" for r in solved),
        )

    return 0 if not failed else 1


def _resolve_puzzle_mode(
    config_mode: str,
    cli_mode: str | None,
    cli_random: bool,
) -> PuzzleMode:
    if cli_mode is not None:
        return cli_mode
    if cli_random:
        return "random"
    return config_mode  # type: ignore[return-value]


def _replace_config(config: AppConfig, **changes) -> AppConfig:
    return AppConfig(
        api_base=config.api_base,
        api_entrypoint=config.api_entrypoint,
        api_timeout_seconds=config.api_timeout_seconds,
        word_length=changes.get("word_length", config.word_length),
        size_begin=changes.get("size_begin", config.size_begin),
        size_end=changes.get("size_end", config.size_end),
        seed_begin=changes.get("seed_begin", config.seed_begin),
        seed_end=changes.get("seed_end", config.seed_end),
        mode=changes.get("mode", config.mode),
        algorithm=config.algorithm,
        dictionary_path=config.dictionary_path,
        max_guesses=config.max_guesses,
    )


if __name__ == "__main__":
    raise SystemExit(main())
