# Wordle Solver

A Python program that solves Wordle-style puzzles by posting guesses to a remote API and narrowing the answer using feedback (`correct`, `present`, `absent`).

Three solving strategies are supported:

| Algorithm | Module | Strategy |
|-----------|--------|----------|
| `candidates` | `solver.algorithms.candidates` | Filter a dictionary until one word remains; probe when many candidates remain |
| `brute_force` | `solver.algorithms.brute_force` | Discover letters and positions without relying on the dictionary |
| `llm` | `solver.algorithms.llm` | Build a prompt from guess history and ask an LLM for the next word |

The default algorithm is **candidates**. When the dictionary does not contain the target word, the candidates algorithm falls back to the same brute-force probes used by `brute_force`.

## Requirements

- Python 3.11+
- Dictionary file (default: [`../data/words_alpha.txt`](../../data/words_alpha.txt) from [dwyl/english-words](https://github.com/dwyl/english-words/))

## Setup

```bash
cd wordle-solver
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
# Edit .env — set WORDLE_API_BASE at minimum
```

## Configuration

Settings are read from `.env` (see `.env.example`):

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `WORDLE_API_BASE` | yes | — | API root (e.g. `http://localhost:8000`); `/daily` or `/random` is appended from mode |
| `WORDLE_API_TIMEOUT_SECONDS` | no | `10` | HTTP timeout |
| `WORDLE_MODE` | no | `daily` | Puzzle source: `daily` or `random` |
| `WORDLE_SIZE_BEGIN` | no | `5` | First puzzle length to try (inclusive) |
| `WORDLE_SIZE_END` | no | `WORDLE_SIZE_BEGIN` | Last puzzle length to try (inclusive) |
| `WORDLE_SEED_BEGIN` | no | — | First random seed (inclusive); requires `WORDLE_SEED_END` |
| `WORDLE_SEED_END` | no | — | Last random seed (inclusive); used when `WORDLE_MODE=random` |
| `WORDLE_ALGORITHM` | no | `candidates` | `candidates`, `brute_force`, or `llm` |
| `WORDLE_DICTIONARY_PATH` | no | `../data/words_alpha.txt` | Path to word list |
| `WORDLE_MAX_GUESSES` | no | `50` | Stop after this many guesses |

## Usage

```bash
wordle-solver
wordle-solver --mode random
wordle-solver --random --seed 42
wordle-solver --size-begin 4 --size-end 8 -v
```

**Daily** (`WORDLE_MODE=daily`): loops sizes in `[WORDLE_SIZE_BEGIN, WORDLE_SIZE_END]` against `GET /daily`. If the first guess for size `N` returns a server/parse error, that size is skipped.

**Random** (`WORDLE_MODE=random` or `--random`): loops sizes (and optional seed range) against `GET /random`. Same seed + size → same word on [wordle.votee.dev](https://wordle.votee.dev:8000/docs).

On success the program prints each solved word. If `WORDLE_MAX_GUESSES` is reached for any size, it exits `1`.

## API contract

[Votee Wordle API](https://wordle.votee.dev:8000/docs) endpoints:

| Endpoint | Description |
|----------|-------------|
| `GET /daily?guess=&size=` | Today's puzzle for the given length |
| `GET /random?guess=&size=&seed=` | Random word; optional `seed` for reproducibility |
| `GET /word/{word}?guess=` | Practice against a fixed word |

Daily (default):

```http
GET {WORDLE_API_BASE}/daily?guess=guess&size=5
Accept: application/json
```

Random:

```http
GET {WORDLE_API_BASE}/random?guess=guess&size=5&seed=42
```

`size` must match the length of `guess`. The client lowercases guesses before sending.

The response must be a JSON **array** of slot results:

```json
[
  {"slot": 0, "guess": "g", "result": "absent"},
  {"slot": 1, "guess": "u", "result": "correct"},
  {"slot": 2, "guess": "e", "result": "absent"},
  {"slot": 3, "guess": "s", "result": "present"},
  {"slot": 4, "guess": "s", "result": "correct"}
]
```

| `result` | Meaning |
|----------|---------|
| `correct` | Letter is in the target word at this index |
| `present` | Letter is in the target word but not at this index |
| `absent` | Letter is not in the target (or is an extra duplicate) |

Full details: [docs/API.md](docs/API.md).

## Project layout

```
wordle-solver/
├── solver/
│   ├── main.py              # CLI entry: guess loop
│   ├── config.py            # .env loading
│   ├── api.py               # HTTP client
│   ├── dictionary.py        # Load word list
│   ├── feedback.py          # Parse feedback, update letter/position state
│   ├── types.py             # SolverState, Feedback, helpers
│   └── algorithms/
│       ├── candidates/      # Dictionary narrowing + probe guesses
│       ├── brute_force/     # Charset / position probes
│       └── llm/             # Prompt builder + guess extraction
├── tests/                   # pytest suite (TDD)
└── docs/                    # Architecture and function reference
```

## Testing

Tests are written first; many pure functions still raise `NotImplementedError` until implemented.

```bash
pytest
pytest tests/algorithms/candidates/test_filter.py -v
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md) — data flow, `SolverState`, algorithms
- [API contract](docs/API.md) — request/response format and feedback rules
- [Function reference](docs/FUNCTIONS.md) — every pure function: purpose, input, output
- [Algorithms overview](../../docs/ALGORITHMS.md) — high-level strategy notes (parent repo)

## License

Dictionary credits: [data/CREDITS.md](../../data/CREDITS.md).
