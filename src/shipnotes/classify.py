"""Sort commits into release note sections."""

from dataclasses import dataclass
from enum import StrEnum

from shipnotes.conventional import parse_subject
from shipnotes.gitlog import Commit


class Section(StrEnum):
    BREAKING = "breaking"
    FEATURE = "feature"
    FIX = "fix"
    PERF = "perf"
    DOCS = "docs"
    INTERNAL = "internal"


TYPE_TO_SECTION = {
    "feat": Section.FEATURE,
    "fix": Section.FIX,
    "perf": Section.PERF,
    "docs": Section.DOCS,
    "chore": Section.INTERNAL,
    "ci": Section.INTERNAL,
    "build": Section.INTERNAL,
    "test": Section.INTERNAL,
    "style": Section.INTERNAL,
    "refactor": Section.INTERNAL,
}


@dataclass(frozen=True)
class Entry:
    commit: Commit
    section: Section
    summary: str
    scope: str | None = None


def classify_by_convention(commit: Commit) -> Entry | None:
    """Classify a commit from its subject alone. None means the subject gave no answer."""
    parsed = parse_subject(commit.subject)
    if parsed is None or parsed.type not in TYPE_TO_SECTION:
        return None
    return Entry(commit, TYPE_TO_SECTION[parsed.type], parsed.text, parsed.scope)
