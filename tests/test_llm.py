import json

from langchain_core.language_models.fake_chat_models import FakeListChatModel

from shipnotes.classify import Section
from shipnotes.gitlog import Commit
from shipnotes.llm import classify_with_llm, format_commits


def commit(sha_char, subject, body=""):
    return Commit(sha=sha_char * 40, author="Ana", subject=subject, body=body)


def reply(*items):
    keys = ["id", "section", "summary"]
    return json.dumps({"items": [dict(zip(keys, i, strict=True)) for i in items]})


def test_format_commits_includes_first_body_line():
    text = format_commits([commit("a", "Speed up import", "Uses a single query now.\nMore detail")])
    assert text == "- 1: Speed up import\n  Uses a single query now."


def test_classify_uses_model_answer():
    model = FakeListChatModel(responses=[reply((1, "perf", "Faster CSV import"))])
    (entry,) = classify_with_llm([commit("a", "Speed up import")], model)
    assert entry.section is Section.PERF
    assert entry.summary == "Faster CSV import"


def test_commit_the_model_skipped_goes_to_other():
    model = FakeListChatModel(responses=[reply((1, "fix", "Fix crash"))])
    entries = classify_with_llm([commit("a", "Fix crash"), commit("b", "Tweak thing")], model)
    assert [e.section for e in entries] == [Section.FIX, Section.OTHER]
    assert entries[1].summary == "Tweak thing"


def test_no_commits_skips_the_model():
    model = FakeListChatModel(responses=[])
    assert classify_with_llm([], model) == []


def test_long_ranges_are_split_into_batches():
    class ByContent(FakeListChatModel):
        """Answers each batch from its own prompt, so thread order does not matter."""

        def _call(self, messages, *args, **kwargs):
            prompt = messages[-1].content
            if "- 1: 3" in prompt:
                return reply((1, "docs", "Three"))
            return reply((1, "fix", "One"), (2, "fix", "Two"))

    commits = [commit("a", "1"), commit("b", "2"), commit("c", "3")]
    entries = classify_with_llm(commits, ByContent(responses=[]), batch_size=2)
    assert [e.summary for e in entries] == ["One", "Two", "Three"]


def test_broken_json_is_retried():
    model = FakeListChatModel(responses=["not json", reply((1, "feature", "Add x"))])
    (entry,) = classify_with_llm([commit("a", "add x")], model)
    assert entry.section is Section.FEATURE


def test_batch_that_keeps_failing_falls_back_to_other():
    model = FakeListChatModel(responses=["not json", "still not json"])
    (entry,) = classify_with_llm([commit("a", "add x")], model)
    assert entry.section is Section.OTHER
    assert entry.summary == "add x"


def test_commits_sharing_a_short_sha_prefix_get_their_own_answers():
    a = Commit(sha="abcdef1" + "0" * 33, author="Ana", subject="Speed up import")
    b = Commit(sha="abcdef1" + "1" * 33, author="Ana", subject="Fix login redirect")
    model = FakeListChatModel(
        responses=[reply((1, "perf", "Faster import"), (2, "fix", "Fix login"))]
    )
    entries = classify_with_llm([a, b], model)
    assert [(e.section, e.summary) for e in entries] == [
        (Section.PERF, "Faster import"),
        (Section.FIX, "Fix login"),
    ]


def test_blank_summary_falls_back_to_the_subject():
    model = FakeListChatModel(responses=[reply((1, "fix", "   "))])
    (entry,) = classify_with_llm([commit("a", "Fix crash on empty config")], model)
    assert entry.section is Section.FIX
    assert entry.summary == "Fix crash on empty config"


def test_multi_line_summary_is_kept_on_one_line():
    model = FakeListChatModel(responses=[reply((1, "fix", "Fix crash\n  on empty config"))])
    (entry,) = classify_with_llm([commit("a", "fix it")], model)
    assert entry.summary == "Fix crash on empty config"
