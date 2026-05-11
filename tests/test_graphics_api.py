import pytest

from command_context import CommandContext, FontTarget
from document import Document
from graphics_api import MAX_FONT_SIZE, MIN_FONT_SIZE, build_namespace


def test_namespace_exposes_move_to():
    ns = build_namespace(CommandContext(active_document=Document()))
    assert callable(ns.get("move_to"))


def test_move_to_delegates_to_document():
    doc = Document()
    ns = build_namespace(CommandContext(active_document=doc))
    ns["move_to"](10, 20)
    assert doc.cursor == (10, 20)


def test_namespace_includes_builtins():
    ns = build_namespace(CommandContext(active_document=Document()))
    assert ns.get("print") is print
    assert "len" in ns


def _ctx_with_font_target():
    ctx = CommandContext(active_document=Document())
    size = {"value": 10}
    ctx.font_targets["Command"] = FontTarget(
        get=lambda: size["value"],
        set=lambda n: size.__setitem__("value", n),
    )
    return ctx, size


def test_hi_app_set_font_dispatches_to_registered_setter():
    ctx, size = _ctx_with_font_target()
    ns = build_namespace(ctx)
    ns["hi_app_set_font"]("Command", 14)
    assert size["value"] == 14


def test_hi_app_get_font_returns_current_size():
    ctx, size = _ctx_with_font_target()
    size["value"] = 11
    ns = build_namespace(ctx)
    assert ns["hi_app_get_font"]("Command") == 11


def test_hi_app_set_font_is_case_insensitive():
    ctx, size = _ctx_with_font_target()
    ns = build_namespace(ctx)
    ns["hi_app_set_font"]("COMMAND", 12)
    assert size["value"] == 12
    ns["hi_app_set_font"]("command", 16)
    assert size["value"] == 16


def test_hi_app_get_font_is_case_insensitive():
    ctx, size = _ctx_with_font_target()
    size["value"] = 13
    ns = build_namespace(ctx)
    assert ns["hi_app_get_font"]("command") == 13
    assert ns["hi_app_get_font"]("COMMAND") == 13


def test_get_set_round_trip():
    ctx, _ = _ctx_with_font_target()
    ns = build_namespace(ctx)
    current = ns["hi_app_get_font"]("Command")
    ns["hi_app_set_font"]("Command", current + 2)
    assert ns["hi_app_get_font"]("Command") == current + 2


def test_hi_app_set_font_unknown_target_lists_valid_targets():
    ctx, _ = _ctx_with_font_target()
    ns = build_namespace(ctx)
    with pytest.raises(ValueError, match="Command"):
        ns["hi_app_set_font"]("Schematic", 12)


def test_hi_app_get_font_unknown_target_lists_valid_targets():
    ctx, _ = _ctx_with_font_target()
    ns = build_namespace(ctx)
    with pytest.raises(ValueError, match="Command"):
        ns["hi_app_get_font"]("Schematic")


def test_hi_app_set_font_rejects_non_string_target():
    ctx, _ = _ctx_with_font_target()
    ns = build_namespace(ctx)
    with pytest.raises(ValueError):
        ns["hi_app_set_font"](123, 12)


@pytest.mark.parametrize("bad_size", [MIN_FONT_SIZE - 1, MAX_FONT_SIZE + 1, 0, -1, 1000])
def test_hi_app_set_font_rejects_out_of_range_size(bad_size):
    ctx, _ = _ctx_with_font_target()
    ns = build_namespace(ctx)
    with pytest.raises(ValueError, match=str(MIN_FONT_SIZE)):
        ns["hi_app_set_font"]("Command", bad_size)


@pytest.mark.parametrize("bad_size", [10.5, "12", None, True, False])
def test_hi_app_set_font_rejects_non_integer_size(bad_size):
    ctx, _ = _ctx_with_font_target()
    ns = build_namespace(ctx)
    with pytest.raises(ValueError):
        ns["hi_app_set_font"]("Command", bad_size)


def test_hi_app_set_font_accepts_boundary_sizes():
    ctx, size = _ctx_with_font_target()
    ns = build_namespace(ctx)
    ns["hi_app_set_font"]("Command", MIN_FONT_SIZE)
    assert size["value"] == MIN_FONT_SIZE
    ns["hi_app_set_font"]("Command", MAX_FONT_SIZE)
    assert size["value"] == MAX_FONT_SIZE


def test_load_executes_file_into_namespace(tmp_path):
    f = tmp_path / "snippet.py"
    f.write_text("x = 42\ny = x * 2\n")
    ns = build_namespace(CommandContext(active_document=Document()))
    ns["load"](str(f))
    assert ns["x"] == 42
    assert ns["y"] == 84


def test_load_can_call_namespace_functions(tmp_path):
    f = tmp_path / "calls_move.py"
    f.write_text("move_to(7, 9)\n")
    doc = Document()
    ns = build_namespace(CommandContext(active_document=doc))
    ns["load"](str(f))
    assert doc.cursor == (7, 9)


def test_load_missing_file_raises_file_not_found(tmp_path):
    ns = build_namespace(CommandContext(active_document=Document()))
    with pytest.raises(FileNotFoundError):
        ns["load"](str(tmp_path / "does_not_exist.py"))


def test_load_propagates_syntax_error_with_file_path(tmp_path):
    f = tmp_path / "broken.py"
    f.write_text("def (\n")
    ns = build_namespace(CommandContext(active_document=Document()))
    with pytest.raises(SyntaxError) as exc_info:
        ns["load"](str(f))
    assert str(f) in (exc_info.value.filename or "")


def test_load_propagates_runtime_error(tmp_path):
    f = tmp_path / "boom.py"
    f.write_text("1/0\n")
    ns = build_namespace(CommandContext(active_document=Document()))
    with pytest.raises(ZeroDivisionError):
        ns["load"](str(f))


def test_move_to_raises_when_no_active_document():
    ns = build_namespace(CommandContext())
    with pytest.raises(RuntimeError, match="No active schematic"):
        ns["move_to"](1, 2)


def test_load_propagates_move_to_error_when_no_active_document(tmp_path):
    f = tmp_path / "no_target.py"
    f.write_text("move_to(1, 2)\n")
    ns = build_namespace(CommandContext())
    with pytest.raises(RuntimeError, match="No active schematic"):
        ns["load"](str(f))
