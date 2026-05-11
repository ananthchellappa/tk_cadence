# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Setup and commands

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"          # editable install + pytest/pytest-cov

python main.py                   # launch the app (Tk command window + any number of schematic Toplevels)
pytest                           # run all tests (testpaths = "tests", -ra --strict-markers)
pytest tests/test_graphics_api.py::test_load_executes_file_into_namespace  # single test
pytest --cov                     # coverage
```

Python 3.10+. Pure Tk — no pygame, no third-party runtime dependencies. The project is laid out as flat top-level modules (see `pyproject.toml`'s `py-modules` list) rather than a package — imports are `from interpreter import …`, not `from pygame_cadence.interpreter import …`.

## Architecture

This is a Tk-based schematic editor: a single "Commands" window (REPL + menus) plus zero-or-more independent "Schematic" `tk.Toplevel` windows, each with its own `tk.Canvas` and its own `Document`.

**Single-threaded Tk event loop.** `main.py` calls `root.mainloop()`. Tk dispatches its own redraws — there is no manual `root.after` tick loop. User code submitted at the REPL runs on the Tk main thread, so long-running commands will freeze every window — see the NOTE in `command_window.py:_on_return`.

**REPL → namespace → active document.** The flow when the user presses Enter:
1. `CommandWindow._on_return` records the line to the transcript and calls the executor.
2. `CommandInterpreter` (wraps `code.InteractiveConsole`) calls `console.push(line)`. stdout/stderr are redirected through `_LogSink` back into the Tk log widget; tracebacks are formatted via overridden `showtraceback` / `showsyntaxerror` so errors appear in the log instead of crashing.
3. The interpreter's locals are the dict produced by `graphics_api.build_namespace(context)`. **To add a new REPL command, add it there** — the dict seeds builtins plus `move_to`, `hi_app_set_font`, `hi_app_get_font`, `load`. `load(path)` execs a file into the same namespace, so variables and definitions persist across loads.
4. `move_to` (and any future drawing command) targets `context.active_document`. If no schematic is open, it raises a `RuntimeError` with a hint to open one — don't silently no-op.

**Multi-window schematic model.** Each `SchematicWindow` is a `tk.Toplevel` + `tk.Canvas` that owns its own `Document`. `SchematicManager` (in [schematic_window.py](schematic_window.py)) is the pure-Python state machine that tracks the open windows and keeps `CommandContext.active_document` pointed at whichever one the user last interacted with:
- **register(win)** — new window becomes active.
- **focus(win)** — user clicked or tabbed in; that window's document becomes active. The manager also moves the window to the end of its internal list so the close-fallback prefers the most recently focused.
- **unregister(win)** — if the closed window was active, fall back to the most recently focused remaining window, or `None` if there are no more.

The manager is intentionally Tk-free so the active-document state machine can be unit-tested with fake windows (see [tests/test_schematic_manager.py](tests/test_schematic_manager.py)). `SchematicWindow` itself only wires Tk events (`WM_DELETE_WINDOW`, `<FocusIn>` on the Toplevel) to the manager callbacks.

**`CommandContext` is the bridge from REPL to UI state.** Two slots today:
- `active_document` — managed by `SchematicManager` as described above.
- `font_targets: dict[str, FontTarget]` — UI widgets that expose tunable state register `get`/`set` callbacks. `main.py` registers the Command window's font under `"Command"`; the REPL function `hi_app_set_font("Command", 14)` looks it up case-insensitively. Add new tunables by registering more `FontTarget`-like entries.

This keeps `graphics_api` from importing Tk directly.

**Schematic lifecycle.** `File > New > Schematic` always creates a new Toplevel (no singleton gate); the title counter (`Schematic 1`, `Schematic 2`, …) never reuses numbers. Closing a window via its X button fires `WM_DELETE_WINDOW` → `SchematicWindow._handle_close` → `toplevel.destroy()` → `manager.unregister(self)`. App shutdown is just `transcript.close()` + `root.destroy()`; the latter cascades and destroys all Toplevels. `WM_DELETE_WINDOW` does *not* fire during cascade-destroy, so the manager isn't notified — that's fine because the process is exiting. The `shutting_down` flag in `main.py` keeps shutdown idempotent across the WM-close-root and File > Exit paths.

**Transcript.** `TranscriptLogger` line-buffers `CDS.log` (or `CDS.log.1`, `.2`, … if the base is taken — see `next_free_path`) and tags every line with `INPUT`/`OUTPUT`/`MENU`. Menu actions are wrapped in `_menu(label, action)` in `CommandWindow` so the label is recorded before the action runs. The interpreter's log callback (`log_and_record` in `main.py`) writes to both the log widget and the transcript.

## Gotchas worth knowing

- **WSLg / X11 font scaling.** `TkFixedFont` can resolve to the legacy bitmap font `fixed`, which silently ignores size changes. `CommandWindow.__init__` substitutes `"monospace"` in that case. Don't "simplify" this back to `TkFixedFont`.
- **Font family + size are tracked manually** (`self._font_family`, `self._font_size`) and re-applied to each widget on resize via `_font_spec()`. Configuring a `tkfont.Font` object instead would change the contract — keep new widgets consistent by using `_font_spec()`.
- **`<FocusIn>` bubbles.** Tk's FocusIn event fires for any descendant gaining focus too. `SchematicWindow._handle_focus` filters with `event.widget is self.toplevel` so child widgets gaining focus don't spuriously re-activate the window's document. Preserve that check.
- **`load()` exceptions propagate.** `graphics_api.load` deliberately does not catch errors; the interpreter's `showtraceback` handler formats them into the log. The "no active schematic" `RuntimeError` from `move_to` propagates the same way and is pinned by a test.
- **`SyntaxError` filename rewrite.** `CommandInterpreter._showsyntaxerror` rewrites the filename in the `SyntaxError` args so user-facing errors point at the right file rather than `<console>`. Preserve this if refactoring the interpreter.
