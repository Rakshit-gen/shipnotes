import subprocess
from dataclasses import dataclass
from pathlib import Path

import pytest


def git(repo, *args):
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


@dataclass
class Repo:
    path: Path

    def __str__(self):
        return str(self.path)

    def commit(self, message):
        git(self.path, "commit", "-q", "--allow-empty", "-m", message)


@pytest.fixture
def repo(tmp_path):
    git(tmp_path, "init", "-q", "-b", "main")
    git(tmp_path, "config", "user.name", "Test")
    git(tmp_path, "config", "user.email", "test@example.com")
    r = Repo(tmp_path)
    r.commit("chore: initial commit")
    git(tmp_path, "tag", "v0.1.0")
    return r
