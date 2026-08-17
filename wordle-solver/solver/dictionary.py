from pathlib import Path


def load_dictionary(path: str | Path) -> tuple[str, ...]:
    text = Path(path).read_text(encoding="utf-8")
    seen: set[str] = set()
    words: list[str] = []
    for line in text.splitlines():
        word = line.strip().lower()
        if not word or word in seen:
            continue
        seen.add(word)
        words.append(word)
    return tuple(words)
