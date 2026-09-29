"""Classify free-text commit subjects with a chat model through LangChain."""

from typing import Literal

from pydantic import BaseModel, Field

SectionName = Literal["breaking", "feature", "fix", "perf", "docs", "internal"]


class Classified(BaseModel):
    sha: str = Field(description="The short sha exactly as given")
    section: SectionName
    summary: str = Field(description="One line, user facing, present tense, no trailing period")


class ClassifiedBatch(BaseModel):
    items: list[Classified]


SYSTEM_PROMPT = """You sort git commits into release note sections.

Sections:
- breaking: users must change something when they upgrade
- feature: new behavior users can see or use
- fix: a bug that users could hit is gone
- perf: faster or lighter, same behavior
- docs: documentation only
- internal: tests, CI, refactors, dependency bumps, anything users never notice

Rewrite each subject as a short line a user would understand. Keep names of
flags, commands and config keys as they are. Do not invent details that are not
in the commit.

{format_instructions}"""

HUMAN_PROMPT = """Commits:
{commits}"""
