import code
import contextlib
import sys
import traceback
from typing import Callable


class _LogSink:
    """File-like object that forwards complete lines to a log callback."""

    def __init__(self, log: Callable[[str], None]):
        self._log = log
        self._buf = ""

    def write(self, text: str) -> int:
        if not text:
            return 0
        self._buf += text
        while "\n" in self._buf:
            line, self._buf = self._buf.split("\n", 1)
            self._log(line)
        return len(text)

    def flush(self) -> None:
        if self._buf:
            self._log(self._buf)
            self._buf = ""


class CommandInterpreter:
    def __init__(self, namespace: dict, log_callback: Callable[[str], None]):
        self._log = log_callback
        self.namespace = namespace
        self.console = code.InteractiveConsole(locals=namespace)
        self.console.showtraceback = self._showtraceback
        self.console.showsyntaxerror = self._showsyntaxerror

    def execute(self, line: str) -> bool:
        sink = _LogSink(self._log)
        with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
            try:
                more = self.console.push(line)
            finally:
                sink.flush()
        return more

    def _showtraceback(self) -> None:
        typ, val, tb = sys.exc_info()
        sys.last_type, sys.last_value, sys.last_traceback = typ, val, tb
        # Skip the console's exec frame, matching stdlib behavior.
        skipped = tb.tb_next if tb is not None else None
        text = "".join(traceback.format_exception(typ, val, skipped))
        self._emit(text)

    def _showsyntaxerror(self, filename=None, **_kwargs) -> None:
        typ, val, tb = sys.exc_info()
        sys.last_type, sys.last_value, sys.last_traceback = typ, val, tb
        if filename and isinstance(val, SyntaxError):
            try:
                msg, (_f, lineno, offset, line) = val.args
                val = SyntaxError(msg, (filename, lineno, offset, line))
                sys.last_value = val
            except (ValueError, TypeError):
                pass
        text = "".join(traceback.format_exception_only(typ, val))
        self._emit(text)

    def _emit(self, text: str) -> None:
        for line in text.rstrip("\n").splitlines():
            self._log(line)
