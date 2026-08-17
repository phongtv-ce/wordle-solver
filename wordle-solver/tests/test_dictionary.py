from solver.dictionary import load_dictionary


def test_load_dictionary_lowercases_dedupes_and_skips_blank_lines(tmp_path):
    path = tmp_path / "words.txt"
    path.write_text("CAT\n\ncat\ndog\nBird\n", encoding="utf-8")
    assert load_dictionary(path) == ("cat", "dog", "bird")
