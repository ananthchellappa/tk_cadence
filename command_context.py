from dataclasses import dataclass, field
from typing import Callable, NamedTuple, Optional

from document import Document


class FontTarget(NamedTuple):
    get: Callable[[], int]
    set: Callable[[int], None]


@dataclass
class CommandContext:
    active_document: Optional[Document] = None
    font_targets: dict[str, FontTarget] = field(default_factory=dict)
