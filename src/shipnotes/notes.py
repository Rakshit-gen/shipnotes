"""Turn a list of commits into release note entries."""

from langchain_core.language_models import BaseChatModel

from shipnotes.classify import Entry, Section, classify_by_convention
from shipnotes.gitlog import Commit
from shipnotes.llm import classify_with_llm


def build_entries(commits: list[Commit], model: BaseChatModel | None) -> list[Entry]:
    """Classify by convention first and only ask the model about the rest.

    Without a model, commits the convention cannot place go to Section.OTHER.
    """
    known = {}
    unknown = []
    for c in commits:
        entry = classify_by_convention(c)
        if entry is None:
            unknown.append(c)
        else:
            known[c.sha] = entry
    if model is not None:
        guessed = classify_with_llm(unknown, model)
    else:
        guessed = [Entry(c, Section.OTHER, c.subject) for c in unknown]
    known.update({e.commit.sha: e for e in guessed})
    return [known[c.sha] for c in commits]
