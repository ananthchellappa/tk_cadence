from typing import Optional


class CommandHistory:
    def __init__(self):
        self._entries: list[str] = []
        self._cursor: int = 0
        self._draft: str = ""

    def add(self, line: str) -> None:
        if line and (not self._entries or self._entries[-1] != line):
            self._entries.append(line)
        self._cursor = len(self._entries)
        self._draft = ""

    def prev(self, current: str) -> Optional[str]:
        if self._cursor == 0:
            return None
        if self._cursor == len(self._entries):
            self._draft = current
        self._cursor -= 1
        return self._entries[self._cursor]

    def next(self, current: str) -> Optional[str]:
        if self._cursor >= len(self._entries):
            return None
        self._cursor += 1
        if self._cursor == len(self._entries):
            return self._draft
        return self._entries[self._cursor]
