from text_editing import word_boundary_left, word_boundary_right


# --- left (Ctrl+Backspace) ---


def test_left_at_end_of_word_walks_to_word_start():
    assert word_boundary_left("abc xyz", 7) == 4


def test_left_eats_trailing_whitespace_then_word():
    assert word_boundary_left("abc xyz ", 8) == 4


def test_left_at_start_returns_zero():
    assert word_boundary_left("abc", 0) == 0


def test_left_on_empty_string_is_zero():
    assert word_boundary_left("", 0) == 0


def test_left_mid_word_deletes_back_to_word_start():
    assert word_boundary_left("abcdef", 4) == 0


def test_left_treats_underscore_as_word_char():
    assert word_boundary_left("foo_bar", 7) == 0


def test_left_at_end_only_eats_trailing_word_not_earlier_spaces():
    # Cursor at end; no trailing non-word, so just the trailing word goes.
    assert word_boundary_left("abc    xyz", 10) == 7


def test_left_just_past_spaces_eats_spaces_and_preceding_word():
    # Cursor right after the run of spaces — eat spaces then "abc".
    assert word_boundary_left("abc    xyz", 7) == 0


def test_left_treats_punctuation_as_non_word():
    # "foo(bar)|" — eat ")", then "bar"; stop at "("
    assert word_boundary_left("foo(bar)", 8) == 4


def test_left_only_whitespace_to_left_walks_to_zero():
    assert word_boundary_left("    ", 4) == 0


# --- right (Ctrl+Delete) ---


def test_right_at_word_start_walks_to_word_end():
    assert word_boundary_right("abc xyz", 0) == 3


def test_right_eats_leading_whitespace_then_word():
    assert word_boundary_right("abc xyz", 3) == 7


def test_right_at_end_returns_len():
    assert word_boundary_right("abc", 3) == 3


def test_right_on_empty_string_is_zero():
    assert word_boundary_right("", 0) == 0


def test_right_mid_word_walks_to_word_end():
    assert word_boundary_right("abcdef", 2) == 6


def test_right_treats_underscore_as_word_char():
    assert word_boundary_right("foo_bar", 0) == 7


def test_right_eats_run_of_whitespace_then_word():
    assert word_boundary_right("abc    xyz", 3) == 10


def test_right_treats_punctuation_as_non_word():
    # "foo|(bar)" — eat "(", then "bar"; stop at ")"
    assert word_boundary_right("foo(bar)", 3) == 7


def test_right_only_whitespace_to_right_walks_to_end():
    assert word_boundary_right("    ", 0) == 4
