"""Read commits from a git repository."""

import subprocess
from dataclasses import dataclass

# Unit and record separators keep multi-line bodies intact when parsing.
FIELD_SEP = "\x1f"
RECORD_SEP = "\x1e"
LOG_FORMAT = FIELD_SEP.join(["%H", "%an", "%s", "%b"]) + RECORD_SEP


@dataclass(frozen=True)
class Commit:
    sha: str
    author: str
    subject: str
    body: str = ""

    @property
    def short_sha(self) -> str:
        return self.sha[:7]


def parse_log(raw: str) -> list[Commit]:
    commits = []
    for record in raw.split(RECORD_SEP):
        record = record.strip("\n")
        if not record:
            continue
        sha, author, subject, body = record.split(FIELD_SEP, 3)
        commits.append(Commit(sha=sha, author=author, subject=subject, body=body.strip()))
    return commits


class GitError(RuntimeError):
    pass


def read_commits(repo: str, rev_range: str) -> list[Commit]:
    """Return commits in rev_range (for example v1.0..v1.1), oldest first."""
    result = subprocess.run(
        # --end-of-options stops a range like "--output=x" from being read as a git
        # option, which would let the argument write arbitrary files.
        [
            "git",
            "-C",
            repo,
            "log",
            "--reverse",
            f"--format={LOG_FORMAT}",
            "--end-of-options",
            rev_range,
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise GitError(result.stderr.strip() or f"git log failed for {rev_range}")
    return parse_log(result.stdout)
