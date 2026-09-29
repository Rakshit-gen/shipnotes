from shipnotes.classify import Entry, Section
from shipnotes.gitlog import Commit
from shipnotes.render import render


def entry(sha_char, section, summary, scope=None):
    c = Commit(sha=sha_char * 40, author="Ana", subject=summary)
    return Entry(c, section, summary, scope)


def test_sections_render_in_fixed_order_and_skip_empty_ones():
    out = render(
        "v1.2.0",
        [
            entry("a", Section.FIX, "Fix crash"),
            entry("b", Section.BREAKING, "Drop Python 3.10", "build"),
        ],
    )
    assert out == (
        "## v1.2.0\n\n"
        "### Breaking changes\n\n"
        "- **build:** Drop Python 3.10 (bbbbbbb)\n\n"
        "### Fixes\n\n"
        "- Fix crash (aaaaaaa)\n\n"
        "### Contributors\n\n"
        "Ana\n"
    )


def test_no_entries_renders_only_the_title():
    assert render("v1.2.0", []) == "## v1.2.0\n"


def test_internal_changes_are_hidden_unless_asked_for():
    entries = [entry("a", Section.INTERNAL, "Bump ruff")]
    assert "Bump ruff" not in render("v1", entries)
    assert "### Internal" in render("v1", entries, include_internal=True)


def test_contributors_are_listed_once_in_order():
    a = entry("a", Section.FIX, "One")
    b = Entry(Commit("b" * 40, "Ben", "Two"), Section.FIX, "Two")
    c = Entry(Commit("c" * 40, "Ana", "Three"), Section.FIX, "Three")
    assert render("v1", [b, a, c]).endswith("### Contributors\n\nAna, Ben\n")
