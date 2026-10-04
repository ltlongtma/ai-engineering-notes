#!/usr/bin/env python3
"""Check note frontmatter, placement, and Related links. Standard library only."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from notelib import REPO_ROOT, FrontmatterError, load_note, note_paths

REQUIRED_FIELDS = ("title", "topics", "verified_at", "confidence", "last_reviewed")
CONFIDENCE_VALUES = ("high", "medium", "low")
KEBAB_CASE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
EXTERNAL = re.compile(r"^(?:[a-z][a-z0-9+.-]*:|#)", re.I)


def related_section(body: str) -> str:
    """Return the text between '## Related' and the next level-2 heading."""
    lines = body.split("\n")
    collected: list[str] = []
    inside = False
    for line in lines:
        if line.startswith("## "):
            inside = line.strip() == "## Related"
            continue
        if inside:
            collected.append(line)
    return "\n".join(collected)


def check_note(path: Path, root: Path) -> list[str]:
    rel = path.relative_to(root).as_posix()
    try:
        note = load_note(path, root)
    except FrontmatterError as error:
        return [f"{rel}: frontmatter {error}"]
    errors: list[str] = []
    meta = note.meta
    if not KEBAB_CASE.match(path.name):
        errors.append(f"{rel}: the file name is not kebab-case")
    for field in REQUIRED_FIELDS:
        if field not in meta or meta[field] in ("", []):
            errors.append(f"{rel}: the required frontmatter field '{field}' is missing")
    if not isinstance(meta.get("sources"), list) or not meta["sources"]:
        errors.append(f"{rel}: 'sources' is missing or empty")
    topics = meta.get("topics")
    if isinstance(topics, list) and topics:
        if topics[0] != note.folder:
            errors.append(f"{rel}: topics[0] is '{topics[0]}', but the note is in the folder '{note.folder}'")
        for topic in topics:
            if not (root / "topics" / topic).is_dir():
                errors.append(f"{rel}: the topic '{topic}' has no folder topics/{topic}/")
    elif "topics" in meta:
        errors.append(f"{rel}: 'topics' must be a non-empty list")
    confidence = meta.get("confidence")
    if confidence and confidence not in CONFIDENCE_VALUES:
        errors.append(f"{rel}: 'confidence' is '{confidence}'. Use high, medium, or low")
    if "(unverified)" in note.body and confidence != "low":
        errors.append(f"{rel}: the note contains '(unverified)', so 'confidence' must be low")
    for target in LINK.findall(related_section(note.body)):
        if EXTERNAL.match(target):
            continue
        file_part = target.split("#", 1)[0]
        if not (path.parent / file_part).resolve().is_file():
            errors.append(f"{rel}: the Related link '{target}' does not resolve to a file")
    return errors


def check_repo(root: Path) -> list[str]:
    errors: list[str] = []
    for path in note_paths(root):
        errors.extend(check_note(path, root))
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help="repository root")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    errors = check_repo(root)
    for error in errors:
        print(f"error: {error}")
    print(f"check_notes: {len(note_paths(root))} notes, {len(errors)} errors")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
