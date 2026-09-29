from shipnotes.conventional import parse_subject


def test_plain_type():
    p = parse_subject("fix: handle empty config")
    assert (p.type, p.scope, p.text, p.bang) == ("fix", None, "handle empty config", False)


def test_scope_and_bang():
    p = parse_subject("feat(api)!: remove v1 endpoints")
    assert (p.type, p.scope, p.text, p.bang) == ("feat", "api", "remove v1 endpoints", True)


def test_type_is_lowercased():
    assert parse_subject("Fix: typo").type == "fix"


def test_non_conventional_returns_none():
    assert parse_subject("Update README") is None
    assert parse_subject("Merge branch 'main' into dev") is None
