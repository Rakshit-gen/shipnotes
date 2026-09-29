"""Classify free-text commit subjects with a chat model through LangChain."""

import os
from typing import Literal

from langchain_core.exceptions import OutputParserException
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
    # Models sometimes return broken JSON. A second try usually fixes it.
    return (prompt | model | parser).with_retry(
        retry_if_exception_type=(OutputParserException,), stop_after_attempt=2
    )


def classify_with_llm(
    commits: list[Commit], model: BaseChatModel, batch_size: int = 25
) -> list[Entry]:
    """Classify commits with the model. Commits it skips land in Section.OTHER."""
    if not commits:
        return []
    chunks = [commits[i : i + batch_size] for i in range(0, len(commits), batch_size)]
    results = build_chain(model).batch(
        [{"commits": format_commits(c)} for c in chunks], return_exceptions=True
    )
    # A batch that still fails after the retry falls through to Section.OTHER below
    # instead of losing the whole release.
    ok = [r for r in results if isinstance(r, ClassifiedBatch)]
    by_sha = {item.sha[:7]: item for batch in ok for item in batch.items}
    entries = []
    for c in commits:
        item = by_sha.get(c.short_sha)
        if item is None:
            entries.append(Entry(c, Section.OTHER, c.subject))
        else:
            entries.append(Entry(c, Section(item.section), item.summary))
    return entries


# Checked against Groq's model list on 2026-09-29. Override with SHIPNOTES_MODEL.
DEFAULT_MODEL = "openai/gpt-oss-20b"


def groq_model() -> BaseChatModel:
    from langchain_groq import ChatGroq

    # gpt-oss spends output tokens on reasoning first. With Groq's default cap the JSON
    # got cut off mid list, so keep reasoning short and leave room for the answer.
    return ChatGroq(
        model=os.environ.get("SHIPNOTES_MODEL", DEFAULT_MODEL),
        temperature=0,
        reasoning_effort="low",
        max_tokens=8192,
    )
