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
        "- Fix crash (aaaaaaa)\n"
    )


def test_no_entries_renders_only_the_title():
    assert render("v1.2.0", []) == "## v1.2.0\n"
