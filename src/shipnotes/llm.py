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
