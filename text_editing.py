def _is_word_char(c: str) -> bool:
    return c.isalnum() or c == "_"


def word_boundary_left(text: str, cursor: int) -> int:
    """Where Ctrl+Backspace should delete back to.

    Walks left over non-word chars, then over word chars.
    """
    i = cursor
    while i > 0 and not _is_word_char(text[i - 1]):
        i -= 1
    while i > 0 and _is_word_char(text[i - 1]):
        i -= 1
    return i


def word_boundary_right(text: str, cursor: int) -> int:
    """Where Ctrl+Delete should delete forward to.

    Walks right over non-word chars, then over word chars.
    """
    i = cursor
    n = len(text)
    while i < n and not _is_word_char(text[i]):
        i += 1
    while i < n and _is_word_char(text[i]):
        i += 1
    return i
