from command_history import CommandHistory


def test_empty_history_prev_and_next_return_none():
    h = CommandHistory()
    assert h.prev("") is None
    assert h.next("") is None


def test_add_populates_and_prev_returns_most_recent():
    h = CommandHistory()
    h.add("a")
    h.add("b")
    assert h.prev("") == "b"


def test_add_skips_blank_lines():
    h = CommandHistory()
    h.add("")
    assert h.prev("") is None


def test_add_skips_duplicate_of_last():
    h = CommandHistory()
    h.add("a")
    h.add("a")
    assert h.prev("") == "a"
    assert h.prev("") is None  # only one entry, not two


def test_non_consecutive_duplicates_are_kept():
    h = CommandHistory()
    h.add("a")
    h.add("b")
    h.add("a")
    assert h.prev("") == "a"
    assert h.prev("") == "b"
    assert h.prev("") == "a"


def test_prev_walks_back_to_oldest_then_returns_none():
    h = CommandHistory()
    for line in ["a", "b", "c"]:
        h.add(line)
    assert h.prev("") == "c"
    assert h.prev("") == "b"
    assert h.prev("") == "a"
    assert h.prev("") is None  # stays at oldest


def test_next_walks_forward_to_past_end_then_returns_none():
    h = CommandHistory()
    for line in ["a", "b", "c"]:
        h.add(line)
    h.prev("")  # c
    h.prev("")  # b
    h.prev("")  # a
    assert h.next("") == "b"
    assert h.next("") == "c"
    assert h.next("") == ""  # past end, draft was empty
    assert h.next("") is None  # already past end


def test_prev_from_past_end_saves_draft_and_next_restores_it():
    h = CommandHistory()
    h.add("a")
    h.add("b")
    assert h.prev("draft-text") == "b"
    assert h.prev("ignored") == "a"
    assert h.next("ignored") == "b"
    assert h.next("ignored") == "draft-text"


def test_draft_is_saved_only_when_leaving_past_end_zone():
    h = CommandHistory()
    h.add("a")
    h.add("b")
    h.prev("first-draft")     # leaves past-end, saves "first-draft"
    h.prev("not-saved")       # already mid-history, draft not touched
    h.next("not-saved")
    assert h.next("anything") == "first-draft"


def test_add_after_navigation_resets_cursor_and_draft():
    h = CommandHistory()
    h.add("a")
    h.add("b")
    h.prev("draft")  # walk back, save draft
    h.add("c")       # submitting a new line resets state
    assert h.prev("") == "c"
    assert h.next("") == ""  # draft cleared, not "draft"


def test_skipped_add_still_resets_cursor_and_draft():
    h = CommandHistory()
    h.add("a")
    h.prev("draft")          # at "a", draft saved
    h.add("a")               # duplicate, skipped from entries
    assert h.prev("") == "a"  # cursor was reset; we navigate freshly
    h.next("")
    assert h.next("") is None  # draft was cleared (not "draft")


def test_navigating_does_not_corrupt_entries():
    h = CommandHistory()
    h.add("a")
    h.add("b")
    h.add("c")
    # walk and verify entries themselves unchanged
    h.prev("x"); h.prev("y"); h.prev("z")
    h.next(""); h.next(""); h.next("")
    assert h.prev("") == "c"
    assert h.prev("") == "b"
    assert h.prev("") == "a"
