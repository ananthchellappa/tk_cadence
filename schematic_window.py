import tkinter as tk
from typing import Callable

from command_context import CommandContext
from document import Document

DEFAULT_GEOMETRY = "1000x700"
DEFAULT_BACKGROUND = "#000000"


class SchematicWindow:
    def __init__(
        self,
        parent: tk.Misc,
        title: str,
        on_close: Callable[["SchematicWindow"], None],
        on_focus: Callable[["SchematicWindow"], None],
        background: str = DEFAULT_BACKGROUND,
    ):
        self.document = Document()
        self._on_close = on_close
        self.toplevel = tk.Toplevel(parent)
        self.toplevel.title(title)
        self.toplevel.geometry(DEFAULT_GEOMETRY)
        self.canvas = tk.Canvas(
            self.toplevel, background=background, highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.toplevel.protocol("WM_DELETE_WINDOW", self._handle_close)
        # FocusIn fires on the Toplevel itself, not child widgets, so binding
        # here is sufficient for the "user clicked on this window" signal.
        self.toplevel.bind("<FocusIn>", self._handle_focus)
        self._on_focus = on_focus

    def _handle_close(self) -> None:
        self.toplevel.destroy()
        self._on_close(self)

    def _handle_focus(self, event) -> None:
        # FocusIn bubbles from child widgets; ignore those — only react when
        # the Toplevel itself is the focus target.
        if event.widget is self.toplevel:
            self._on_focus(self)


class SchematicManager:
    """Tracks open schematic windows and keeps CommandContext.active_document
    pointed at whichever one the user last interacted with.

    Pure Python — no Tk dependency — so the active-window state machine can
    be unit-tested with fake windows.
    """

    def __init__(self, context: CommandContext):
        self._context = context
        self._windows: list = []

    @property
    def windows(self) -> list:
        return list(self._windows)

    def register(self, window) -> None:
        self._windows.append(window)
        self._context.active_document = window.document

    def focus(self, window) -> None:
        # Move to end so _windows[-1] is always "most recently focused".
        # The unregister fallback uses that ordering.
        if window in self._windows:
            self._windows.remove(window)
            self._windows.append(window)
        self._context.active_document = window.document

    def unregister(self, window) -> None:
        if window in self._windows:
            self._windows.remove(window)
        if self._context.active_document is window.document:
            self._context.active_document = (
                self._windows[-1].document if self._windows else None
            )
