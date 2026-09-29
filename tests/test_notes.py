import json

from langchain_core.language_models.fake_chat_models import FakeListChatModel

from shipnotes.classify import Section
from shipnotes.gitlog import Commit
from shipnotes.notes import build_entries


def commit(sha_char, subject):
    return Commit(sha=sha_char * 40, author="Ana", subject=subject)


def test_only_unconventional_commits_reach_the_model():
    seen = []

    class Spy(FakeListChatModel):
        def _call(self, messages, *args, **kwargs):
            seen.append(messages[-1].content)
            return super()._call(messages, *args, **kwargs)

    answer = {"items": [{"id": 1, "section": "perf", "summary": "Faster start"}]}
    model = Spy(responses=[json.dumps(answer)])
    commits = [commit("a", "fix: crash on empty file"), commit("b", "Speed up startup")]
    entries = build_entries(commits, model)

    assert [e.section for e in entries] == [Section.FIX, Section.PERF]
    assert len(seen) == 1
    assert "Speed up startup" in seen[0]
    assert "crash on empty file" not in seen[0]


def test_without_a_model_unknown_commits_go_to_other():
    entries = build_entries([commit("a", "feat: x"), commit("b", "misc")], None)
    assert [e.section for e in entries] == [Section.FEATURE, Section.OTHER]
