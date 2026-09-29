from shipnotes.cli import main


def test_cli_prints_notes_without_the_model(repo, capsys):
    repo.commit("feat(cli): add --since flag")
    repo.commit("fix: crash on empty repo")
    repo.commit("ci: cache uv")
    assert main(["v0.1.0..HEAD", "--repo", str(repo), "--no-llm", "--title", "v0.2.0"]) == 0
    out = capsys.readouterr().out
    assert out.startswith("## v0.2.0\n")
    assert "- **cli:** add --since flag" in out
    assert "- crash on empty repo" in out
    assert "cache uv" not in out


def test_cli_writes_to_a_file(repo, tmp_path):
    repo.commit("docs: explain ranges")
    target = tmp_path / "NOTES.md"
    assert main(["v0.1.0..HEAD", "--repo", str(repo), "--no-llm", "-o", str(target)]) == 0
    assert "explain ranges" in target.read_text()


def test_cli_reports_bad_ranges(repo, capsys):
    assert main(["nope..HEAD", "--repo", str(repo), "--no-llm"]) == 1
    assert capsys.readouterr().err.startswith("shipnotes: ")


def test_missing_api_key_is_a_clear_error(repo, capsys, monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    assert main(["v0.1.0..HEAD", "--repo", str(repo)]) == 1
    assert "GROQ_API_KEY is not set" in capsys.readouterr().err
