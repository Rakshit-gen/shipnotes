# shipnotes

Draft release notes from the git history between two refs.

Commits that follow Conventional Commits (`feat:`, `fix(api)!:` and so on) are
sorted without any model call. Everything else goes to a chat model through
LangChain, which picks a section and rewrites the subject into a line a user
would understand.

## Quickstart

```
uv sync
export GROQ_API_KEY=...
uv run shipnotes v1.2.0..v1.3.0 --repo path/to/repo
```

Options:

| Flag | What it does |
|---|---|
| `--no-llm` | Sort by commit convention only. Needs no API key. |
| `--internal` | Also list tests, CI, refactors and other internal changes. |
| `--title` | Heading for the notes. Defaults to the end of the range. |
| `-o FILE` | Write to a file instead of stdout. |

The model defaults to `openai/gpt-oss-20b` on Groq. Set `SHIPNOTES_MODEL` to use
another one.

## How it works

1. `git log --reverse` reads the range. Fields are split on ASCII unit and
   record separators so multi-line bodies survive.
2. Each subject is matched against the Conventional Commits pattern. A `!` or
   a `BREAKING CHANGE:` footer puts the commit under breaking changes, even if
   the subject is free text.
3. The leftovers are sent to the model in batches of 25 with the chain
   `prompt | ChatGroq | PydanticOutputParser`. Batches run in parallel through
   LangChain's `batch`.
4. Broken JSON is retried once. If a batch still fails, or the model skips a
   commit, that commit shows up under "Other changes" with its original
   subject. Nothing is dropped.
5. Entries are rendered as Markdown in a fixed section order, followed by the
   list of contributors.

Tests use LangChain's `FakeListChatModel`, so `uv run pytest` needs no key and
no network.

## Measured vs Claimed

| Claim | Value | How measured | Date |
|---|---|---|---|
| Commits placed in a real section (not "Other") | 40 of 40, on 3 of 3 runs | `shipnotes HEAD~40..HEAD --internal` on a 40 commit range of a side project with free text subjects, `openai/gpt-oss-20b` on Groq | 2026-09-29 |
| Wall time for 40 free text commits | 16 to 35 s | Same 3 runs, timed from the shell on a laptop | 2026-09-29 |
| Wall time with `--no-llm` | 0.49 s | Same 40 commit range, `time` from the shell, includes `uv run` startup | 2026-09-29 |

Whether a section is the *right* one was checked by reading the output, not
scored against a labeled set.
