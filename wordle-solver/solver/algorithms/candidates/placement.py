def can_place(letter: str, index: int, present_state: tuple[frozenset[str], ...]) -> bool:
    return letter not in present_state[index]
