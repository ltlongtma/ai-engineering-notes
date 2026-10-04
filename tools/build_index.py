#!/usr/bin/env python3
"""Regenerate the note lists in topic READMEs and the topic index in the root README."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from notelib import REPO_ROOT, FrontmatterError, Note, load_notes, topic_names

START = "<!-- index:start -->"
END = "<!-- index:end -->"


class IndexMarkerError(Exception):
    """A README has no valid index markers or no scope line."""


def replace_section(text: str, content: str, rel: str) -> str:
    if text.count(START) != 1 or text.count(END) != 1 or text.index(START) > text.index(END):
        raise IndexMarkerError(f"{rel}: needs exactly one '{START}' line before one '{END}' line")
    head = text[: text.index(START) + len(START)]
    tail = text[text.index(END):]
    return f"{head}\n{content}{tail}"


def topic_scope(readme_text: str, rel: str) -> str:
    for line in readme_text.split("\n"):
        if line.startswith("Scope: "):
            return line[len("Scope: "):].strip()
    raise IndexMarkerError(f"{rel}: has no 'Scope: ' line")


def notes_for(topic: str, notes: list[Note]) -> list[Note]:
    return sorted((n for n in notes if topic in n.topics), key=lambda n: (n.title.casefold(), n.rel))


def render_topic_list(topic: str, notes: list[Note]) -> str:
    entries = notes_for(topic, notes)
    if not entries:
        return "No notes yet.\n"
    lines = []
    for note in entries:
        if note.folder == topic:
            lines.append(f"- [{note.title}]({note.slug}.md)")
        else:
            lines.append(f"- [{note.title}](../{note.folder}/{note.slug}.md) (primary topic: {note.folder})")
    return "\n".join(lines) + "\n"


def render_root_list(root: Path, notes: list[Note]) -> str:
    lines = []
    for topic in topic_names(root):
        rel = f"topics/{topic}/README.md"
        scope = topic_scope((root / rel).read_text(encoding="utf-8"), rel)
        lines.append(f"- [{topic}]({rel}): {scope} Notes: {len(notes_for(topic, notes))}.")
    return ("\n".join(lines) + "\n") if lines else "No topics yet.\n"


def expected_files(root: Path) -> dict[Path, str]:
    """Return the expected full text of each README that has a generated section."""
    notes = load_notes(root)
    result: dict[Path, str] = {}
    for topic in topic_names(root):
        path = root / "topics" / topic / "README.md"
        rel = path.relative_to(root).as_posix()
        if not path.is_file():
            raise IndexMarkerError(f"{rel}: is missing. Each topic folder needs a README.md")
        result[path] = replace_section(path.read_text(encoding="utf-8"), render_topic_list(topic, notes), rel)
    readme = root / "README.md"
    result[readme] = replace_section(readme.read_text(encoding="utf-8"), render_root_list(root, notes), "README.md")
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if a generated section is not current")
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help="repository root")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        expected = expected_files(root)
    except (IndexMarkerError, FrontmatterError) as error:
        print(f"error: {error}")
        return 1
    stale = [p for p, text in expected.items() if p.read_text(encoding="utf-8") != text]
    for path in stale:
        rel = path.relative_to(root).as_posix()
        if args.check:
            print(f"error: {rel}: the generated index is not current. Run 'make index'.")
        else:
            path.write_text(expected[path], encoding="utf-8")
            print(f"updated {rel}")
    if args.check:
        print(f"build_index --check: {len(expected)} files, {len(stale)} not current")
        return 1 if stale else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
