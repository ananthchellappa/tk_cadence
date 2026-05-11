from command_context import CommandContext
from document import Document
from schematic_window import SchematicManager


class FakeWindow:
    def __init__(self):
        self.document = Document()


def test_register_makes_new_window_active():
    ctx = CommandContext()
    mgr = SchematicManager(ctx)
    win = FakeWindow()
    mgr.register(win)
    assert ctx.active_document is win.document
    assert mgr.windows == [win]


def test_register_second_window_steals_active():
    ctx = CommandContext()
    mgr = SchematicManager(ctx)
    w1, w2 = FakeWindow(), FakeWindow()
    mgr.register(w1)
    mgr.register(w2)
    assert ctx.active_document is w2.document


def test_focus_switches_active_document():
    ctx = CommandContext()
    mgr = SchematicManager(ctx)
    w1, w2 = FakeWindow(), FakeWindow()
    mgr.register(w1)
    mgr.register(w2)
    mgr.focus(w1)
    assert ctx.active_document is w1.document


def test_focus_moves_window_to_end_of_list():
    ctx = CommandContext()
    mgr = SchematicManager(ctx)
    w1, w2, w3 = FakeWindow(), FakeWindow(), FakeWindow()
    mgr.register(w1)
    mgr.register(w2)
    mgr.register(w3)
    mgr.focus(w1)
    assert mgr.windows == [w2, w3, w1]


def test_unregister_active_falls_back_to_most_recent_remaining():
    ctx = CommandContext()
    mgr = SchematicManager(ctx)
    w1, w2, w3 = FakeWindow(), FakeWindow(), FakeWindow()
    mgr.register(w1)
    mgr.register(w2)
    mgr.register(w3)
    mgr.focus(w1)  # order is now [w2, w3, w1], active = w1
    mgr.unregister(w1)
    # Most-recently-focused remaining is w3 (end of list).
    assert ctx.active_document is w3.document


def test_unregister_last_window_clears_active():
    ctx = CommandContext()
    mgr = SchematicManager(ctx)
    w = FakeWindow()
    mgr.register(w)
    mgr.unregister(w)
    assert ctx.active_document is None
    assert mgr.windows == []


def test_unregister_inactive_window_does_not_change_active():
    ctx = CommandContext()
    mgr = SchematicManager(ctx)
    w1, w2 = FakeWindow(), FakeWindow()
    mgr.register(w1)
    mgr.register(w2)  # w2 is active
    mgr.unregister(w1)
    assert ctx.active_document is w2.document


def test_unregister_unknown_window_is_safe():
    ctx = CommandContext()
    mgr = SchematicManager(ctx)
    stranger = FakeWindow()
    mgr.unregister(stranger)
    assert ctx.active_document is None


def test_focus_unregistered_window_still_sets_active():
    # Defensive: focus events can race with registration on some platforms.
    ctx = CommandContext()
    mgr = SchematicManager(ctx)
    w = FakeWindow()
    mgr.focus(w)
    assert ctx.active_document is w.document


def test_windows_property_returns_a_copy():
    ctx = CommandContext()
    mgr = SchematicManager(ctx)
    w = FakeWindow()
    mgr.register(w)
    snapshot = mgr.windows
    snapshot.clear()
    assert mgr.windows == [w]
