"""Classify free-text commit subjects with a chat model through LangChain."""

from typing import Literal

from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from pydantic import BaseModel, Field

from shipnotes.classify import Entry, Section
from shipnotes.gitlog import Commit

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


def format_commits(commits: list[Commit]) -> str:
    lines = []
    for c in commits:
        lines.append(f"- {c.short_sha}: {c.subject}")
        if c.body:
            # The first body line usually says why; the rest is noise for this task.
            lines.append(f"  {c.body.splitlines()[0]}")
    return "\n".join(lines)


def build_chain(model: BaseChatModel) -> Runnable:
    parser = PydanticOutputParser(pydantic_object=ClassifiedBatch)
    prompt = ChatPromptTemplate.from_messages(
        [("system", SYSTEM_PROMPT), ("human", HUMAN_PROMPT)]
    ).partial(format_instructions=parser.get_format_instructions())
    return prompt | model | parser


def classify_with_llm(commits: list[Commit], model: BaseChatModel) -> list[Entry]:
    """Classify commits with the model. Commits it skips land in Section.OTHER."""
    if not commits:
        return []
    result: ClassifiedBatch = build_chain(model).invoke({"commits": format_commits(commits)})
    by_sha = {item.sha[:7]: item for item in result.items}
    entries = []
    for c in commits:
        item = by_sha.get(c.short_sha)
        if item is None:
            entries.append(Entry(c, Section.OTHER, c.subject))
        else:
            entries.append(Entry(c, Section(item.section), item.summary))
    return entries
