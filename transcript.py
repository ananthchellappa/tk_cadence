from datetime import datetime
from pathlib import Path


def next_free_path(base: Path) -> Path:
    """Return `base` if free, otherwise `base.1`, `base.2`, … (first unused)."""
    if not base.exists():
        return base
    i = 1
    while True:
        candidate = base.with_name(base.name + f".{i}")
        if not candidate.exists():
            return candidate
        i += 1


class TranscriptLogger:
    def __init__(self, path: Path):
        self.path = path
        self._fp = path.open("a", buffering=1, encoding="utf-8")

    def record(self, event_type: str, payload: str) -> None:
        ts = datetime.now().isoformat(timespec="seconds")
        self._fp.write(f"[{ts}] {event_type}: {payload}\n")

    def close(self) -> None:
        if not self._fp.closed:
            self._fp.close()
