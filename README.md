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
