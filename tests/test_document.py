from document import Document


def test_document_starts_with_cursor_at_origin():
    doc = Document()
    assert doc.cursor == (0, 0)


def test_move_to_updates_cursor():
    doc = Document()
    doc.move_to(42, 99)
    assert doc.cursor == (42, 99)
