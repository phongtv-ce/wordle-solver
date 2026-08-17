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
# Edit .env — set WORDLE_API_ENTRYPOINT at minimum
```

## Configuration

Settings are read from `.env` (see `.env.example`):

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `WORDLE_API_ENTRYPOINT` | yes | — | POST URL for guesses |
| `WORDLE_API_KEY` | no | — | Bearer token, if the API requires auth |
| `WORDLE_API_TIMEOUT_SECONDS` | no | `10` | HTTP timeout |
| `WORDLE_WORD_LENGTH` | no | `5` | Puzzle word length |
| `WORDLE_ALGORITHM` | no | `candidates` | `candidates`, `brute_force`, or `llm` |
| `WORDLE_DICTIONARY_PATH` | no | `../data/words_alpha.txt` | Path to word list |
| `WORDLE_MAX_GUESSES` | no | `50` | Stop after this many guesses |

## Usage

```bash
wordle-solver
wordle-solver --algorithm brute_force
wordle-solver --algorithm candidates --env-file /path/to/.env
```

On success the program prints the solved word and exits `0`. If `WORDLE_MAX_GUESSES` is reached without a full `correct` row, it exits `1`.

## API contract

The client sends:

```http
GET {WORDLE_API_ENTRYPOINT}?guess=guess&size=5
Accept: application/json
Authorization: Bearer {WORDLE_API_KEY}   # optional
```

`size` is `WORDLE_WORD_LENGTH` and must match the length of `guess`.

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
