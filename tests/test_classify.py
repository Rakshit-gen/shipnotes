from shipnotes.classify import Section, classify_by_convention
from shipnotes.gitlog import Commit


def make(subject, body=""):
    return Commit(sha="f" * 40, author="Ana", subject=subject, body=body)


def test_feat_goes_to_features():
    entry = classify_by_convention(make("feat(cli): add --since flag"))
    assert entry.section is Section.FEATURE
    assert entry.summary == "add --since flag"
    assert entry.scope == "cli"


def test_chore_types_are_internal():
    for t in ["chore", "ci", "build", "test", "style", "refactor"]:
        assert classify_by_convention(make(f"{t}: tidy")).section is Section.INTERNAL


def test_unknown_type_is_left_unclassified():
    assert classify_by_convention(make("wip: stuff")) is None


def test_free_text_subject_is_left_unclassified():
    assert classify_by_convention(make("Speed up the importer")) is None


def test_bang_marks_breaking():
    entry = classify_by_convention(make("feat(api)!: drop v1 routes"))
    assert entry.section is Section.BREAKING
    assert entry.summary == "drop v1 routes"


def test_footer_marks_breaking_even_without_convention():
    commit = make("Rename config keys", "BREAKING CHANGE: `port` is now `listen`")
    entry = classify_by_convention(commit)
    assert entry.section is Section.BREAKING
    assert entry.summary == "Rename config keys"


def test_breaking_text_in_middle_of_line_does_not_count():
    entry = classify_by_convention(make("fix: typo", "mentions BREAKING CHANGE: in passing"))
    assert entry.section is Section.FIX
