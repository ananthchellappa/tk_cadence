from command_context import CommandContext
from document import Document
from graphics_api import build_namespace
from interpreter import CommandInterpreter


def _make(log=None):
    log = [] if log is None else log
    context = CommandContext(active_document=Document())
    interp = CommandInterpreter(build_namespace(context), log.append)
    return interp, log


def test_single_line_returns_false_and_updates_namespace():
    interp, _ = _make()
    more = interp.execute("x = 42")
    assert more is False
    assert interp.namespace["x"] == 42


def test_multiline_def_returns_true_until_block_closes():
    interp, _ = _make()
    assert interp.execute("def f():") is True
    assert interp.execute("    return 1 + 2") is True
    assert interp.execute("") is False
    assert interp.namespace["f"]() == 3


def test_stdout_from_user_code_routed_to_log_callback():
    interp, log = _make()
    interp.execute("print('hello')")
    assert "hello" in log


def test_runtime_error_reported_via_log_callback_not_raised():
    interp, log = _make()
    interp.execute("1/0")  # must not raise
    joined = "\n".join(log)
    assert "ZeroDivisionError" in joined
    assert "division by zero" in joined
