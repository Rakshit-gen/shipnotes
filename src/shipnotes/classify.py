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
    # Commits nothing could place. Kept so they are never silently dropped.
    OTHER = "other"


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

BREAKING_FOOTERS = ("BREAKING CHANGE:", "BREAKING-CHANGE:")


@dataclass(frozen=True)
class Entry:
    commit: Commit
    section: Section
    summary: str
    scope: str | None = None


def is_breaking(commit: Commit) -> bool:
    parsed = parse_subject(commit.subject)
    if parsed and parsed.bang:
        return True
    return any(line.startswith(BREAKING_FOOTERS) for line in commit.body.splitlines())


def classify_by_convention(commit: Commit) -> Entry | None:
    """Classify a commit from its subject and footer. None means neither gave an answer."""
    parsed = parse_subject(commit.subject)
    text = parsed.text if parsed else commit.subject
    scope = parsed.scope if parsed else None
    if is_breaking(commit):
        return Entry(commit, Section.BREAKING, text, scope)
    if parsed is None or parsed.type not in TYPE_TO_SECTION:
        return None
    return Entry(commit, TYPE_TO_SECTION[parsed.type], text, scope)
