"""Parse Conventional Commits subjects like `feat(api)!: add paging`."""

import re
from dataclasses import dataclass

SUBJECT_RE = re.compile(
    r"^(?P<type>[a-zA-Z]+)(?:\((?P<scope>[^)]+)\))?(?P<bang>!)?:\s*(?P<text>.+)$"
)


@dataclass(frozen=True)
class Parsed:
    type: str
    scope: str | None
    text: str
    bang: bool


def parse_subject(subject: str) -> Parsed | None:
    """Return the parsed subject, or None when it does not follow the convention."""
    m = SUBJECT_RE.match(subject.strip())
    if not m:
        return None
    return Parsed(
        type=m["type"].lower(),
        scope=m["scope"],
        text=m["text"].strip(),
        bang=bool(m["bang"]),
    )
