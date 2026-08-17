# Wordle Solver

A Python solver for Wordle-style puzzles. It posts guesses to a remote API and narrows the answer using feedback (`correct`, `present`, `absent`).

**Getting started:** see [wordle-solver/README.md](wordle-solver/README.md) for setup, configuration, and usage.

## Documentation

### Project guide

| Document | Description |
|----------|-------------|
| [wordle-solver/README.md](wordle-solver/README.md) | Setup, configuration, CLI usage, project layout |

### Implementation reference (`wordle-solver/docs/`)

| Document | Description |
|----------|-------------|
| [ARCHITECTURE.md](wordle-solver/docs/ARCHITECTURE.md) | Data flow, `SolverState`, algorithm overview, module map |
| [API.md](wordle-solver/docs/API.md) | HTTP request/response format, feedback semantics, duplicate letters |
| [FUNCTIONS.md](wordle-solver/docs/FUNCTIONS.md) | Every pure function: purpose, input, output, test mapping |

### Algorithm design (`docs/`)

| Document | Description |
|----------|-------------|
| [ALGORITHMS.md](docs/ALGORITHMS.md) | High-level comparison of all three strategies |
| [algorithms/candidtes.md](docs/algorithms/candidtes.md) | Dictionary candidates — state groups, filtering, probe strategy |
| [algorithms/brute-force.md](docs/algorithms/brute-force.md) | Charset and position probes without a dictionary |
| [algorithms/llm-promt.md](docs/algorithms/llm-promt.md) | LLM prompt template and response format |

### Data

| Document | Description |
|----------|-------------|
| [data/CREDITS.md](data/CREDITS.md) | Dictionary source and license |

## Repository layout

```
CodeTest/
├── README.md              # This file — documentation index
├── data/
│   ├── words_alpha.txt    # English word list (default dictionary)
│   └── CREDITS.md
├── docs/                  # Algorithm design notes
│   ├── ALGORITHMS.md
│   └── algorithms/
│       ├── candidtes.md
│       ├── brute-force.md
│       └── llm-promt.md
└── wordle-solver/         # Python package and CLI
    ├── README.md          # Setup and usage
    ├── docs/              # Architecture and API reference
    ├── solver/            # Source code
    └── tests/             # pytest suite
```

## Algorithms

Three solving strategies are available (default: **candidates**):

| Algorithm | Module | Strategy |
|-----------|--------|----------|
| `candidates` | `solver.algorithms.candidates` | Filter a dictionary until one word remains; probe when many candidates remain |
| `brute_force` | `solver.algorithms.brute_force` | Discover letters and positions without relying on the dictionary |
| `llm` | `solver.algorithms.llm` | Build a prompt from guess history and ask an LLM for the next word |

See [docs/ALGORITHMS.md](docs/ALGORITHMS.md) for design notes and [wordle-solver/docs/ARCHITECTURE.md](wordle-solver/docs/ARCHITECTURE.md) for how they fit into the code.
