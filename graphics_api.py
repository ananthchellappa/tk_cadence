import builtins as _builtins

from command_context import CommandContext, FontTarget

MIN_FONT_SIZE = 6
MAX_FONT_SIZE = 72


def build_namespace(context: CommandContext) -> dict:
    ns: dict = dict(vars(_builtins))

    def move_to(x, y):
        if context.active_document is None:
            raise RuntimeError(
                "No active schematic window. Open one with File > New > Schematic."
            )
        context.active_document.move_to(x, y)

    def hi_app_set_font(target: str, size: int) -> None:
        ft = _lookup_target(context, target)
        _validate_size(size)
        ft.set(size)

    def hi_app_get_font(target: str) -> int:
        ft = _lookup_target(context, target)
        return ft.get()

    def load(path: str) -> None:
        with open(path) as f:
            source = f.read()
        exec(compile(source, path, "exec"), ns)

    ns["move_to"] = move_to
    ns["hi_app_set_font"] = hi_app_set_font
    ns["hi_app_get_font"] = hi_app_get_font
    ns["load"] = load
    return ns


def _lookup_target(context: CommandContext, target) -> FontTarget:
    if not isinstance(target, str):
        valid = sorted(context.font_targets)
        raise ValueError(
            f"target must be a string, got {type(target).__name__}. Valid targets: {valid}"
        )
    target_cf = target.casefold()
    for key, ft in context.font_targets.items():
        if key.casefold() == target_cf:
            return ft
    valid = sorted(context.font_targets)
    raise ValueError(f"unknown font target {target!r}. Valid targets: {valid}")


def _validate_size(size) -> None:
    if isinstance(size, bool) or not isinstance(size, int):
        raise ValueError(
            f"size must be an integer between {MIN_FONT_SIZE} and {MAX_FONT_SIZE}, "
            f"got {type(size).__name__}: {size!r}"
        )
    if not (MIN_FONT_SIZE <= size <= MAX_FONT_SIZE):
        raise ValueError(
            f"size must be between {MIN_FONT_SIZE} and {MAX_FONT_SIZE}, got {size}"
        )
