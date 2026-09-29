"""Render release note entries as Markdown."""

from shipnotes.classify import Entry, Section

HEADINGS = {
    Section.BREAKING: "Breaking changes",
    Section.FEATURE: "Features",
    Section.FIX: "Fixes",
    Section.PERF: "Performance",
    Section.DOCS: "Docs",
    Section.OTHER: "Other changes",
    Section.INTERNAL: "Internal",
}


def render(title: str, entries: list[Entry], include_internal: bool = False) -> str:
    lines = [f"## {title}", ""]
    for section, heading in HEADINGS.items():
        if section is Section.INTERNAL and not include_internal:
            continue
        items = [e for e in entries if e.section is section]
        if not items:
            continue
        lines += [f"### {heading}", ""]
        for e in items:
            scope = f"**{e.scope}:** " if e.scope else ""
            lines.append(f"- {scope}{e.summary} ({e.commit.short_sha})")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
