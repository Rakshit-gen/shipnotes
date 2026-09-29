"""Command line entry point."""

import argparse
import sys

from shipnotes.gitlog import GitError, read_commits
from shipnotes.notes import build_entries
from shipnotes.render import render


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="shipnotes", description="Draft release notes from the git history between two refs."
    )
    parser.add_argument("range", help="revision range, for example v1.0.0..v1.1.0")
    parser.add_argument("--repo", default=".", help="path to the git repository")
    parser.add_argument("--title", help="heading for the notes (default: the end of the range)")
    parser.add_argument("--no-llm", action="store_true", help="classify by commit convention only")
    parser.add_argument("--internal", action="store_true", help="include internal changes")
    parser.add_argument("-o", "--output", help="write to this file instead of stdout")
    args = parser.parse_args(argv)

    try:
        commits = read_commits(args.repo, args.range)
    except GitError as e:
        print(f"shipnotes: {e}", file=sys.stderr)
        return 1

    model = None
    if not args.no_llm:
        from shipnotes.llm import groq_model

        model = groq_model()

    title = args.title or args.range.split("..")[-1] or "Unreleased"
    text = render(title, build_entries(commits, model), include_internal=args.internal)
    if args.output:
        with open(args.output, "w") as f:
            f.write(text)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
