from shipnotes.gitlog import FIELD_SEP, RECORD_SEP, parse_log


def record(sha, author, subject, body=""):
    return FIELD_SEP.join([sha, author, subject, body]) + RECORD_SEP


def test_parse_log_reads_each_record():
    raw = record("a" * 40, "Ana", "feat: add login") + "\n" + record("b" * 40, "Ben", "fix typo")
    commits = parse_log(raw)
    assert [c.subject for c in commits] == ["feat: add login", "fix typo"]
    assert commits[0].author == "Ana"
    assert commits[1].short_sha == "bbbbbbb"


def test_parse_log_keeps_multiline_body():
    raw = record("c" * 40, "Cy", "fix: crash", "First line\n\nBREAKING CHANGE: drops py3.10\n")
    (commit,) = parse_log(raw)
    assert commit.body == "First line\n\nBREAKING CHANGE: drops py3.10"


def test_parse_log_empty_input():
    assert parse_log("") == []
