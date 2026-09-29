import pytest
from conftest import git

from shipnotes.gitlog import FIELD_SEP, RECORD_SEP, GitError, parse_log, read_commits


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


def test_read_commits_returns_range_oldest_first(repo):
    repo.commit("feat: first")
    repo.commit("fix: second")
    commits = read_commits(str(repo), "v0.1.0..HEAD")
    assert [c.subject for c in commits] == ["feat: first", "fix: second"]


def test_read_commits_bad_range_raises(repo):
    with pytest.raises(GitError):
        read_commits(str(repo), "nope..HEAD")


def test_range_is_never_read_as_a_git_option(repo, tmp_path):
    target = tmp_path / "written.txt"
    with pytest.raises(GitError):
        read_commits(str(repo), f"--output={target}")
    assert not target.exists()


def test_merge_commits_are_skipped(repo):
    git(repo.path, "checkout", "-q", "-b", "feature")
    repo.commit("feat: on a branch")
    git(repo.path, "checkout", "-q", "main")
    git(repo.path, "merge", "-q", "--no-ff", "feature", "-m", "Merge branch 'feature'")
    assert [c.subject for c in read_commits(str(repo), "v0.1.0..HEAD")] == ["feat: on a branch"]
