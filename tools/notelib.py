"""Shared helpers: frontmatter parser and note discovery. Standard library only."""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

_KEY_VALUE = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*):(?:\s+(.*))?$")


class FrontmatterError(ValueError):
    """The frontmatter is missing or uses syntax outside the supported subset."""

    def __init__(self, line: int, message: str):
        super().__init__(f"line {line}: {message}")
        self.line = line


def frontmatter_end(lines: list[str]) -> int | None:
    """Return the index of the closing '---' line, or None if no frontmatter block exists."""
    if not lines or lines[0].strip() != "---":
        return None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return index
    return None


def _scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Parse the YAML subset that notes use. Return (meta, body).

    Supported: `key: scalar`, `key: [a, b]`, and `key:` followed by a block
    list of scalars (`  - value`) or of mappings (`  - url: ...` / `    accessed: ...`).
    """
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        raise FrontmatterError(1, "the file does not start with a '---' frontmatter line")
    end = frontmatter_end(lines)
    if end is None:
        raise FrontmatterError(1, "the frontmatter has no closing '---' line")
    meta: dict = {}
    list_key: str | None = None
    for index in range(1, end):
        raw = lines[index]
        lineno = index + 1
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if not raw[0].isspace():
            match = _KEY_VALUE.match(raw.rstrip())
            if not match:
                raise FrontmatterError(lineno, f"expected 'key: value', got {raw.strip()!r}")
            key, value = match.group(1), (match.group(2) or "").strip()
            if value == "":
                meta[key] = []
                list_key = key
            elif value.startswith("["):
                if not value.endswith("]"):
                    raise FrontmatterError(lineno, f"the inline list for {key!r} has no closing ']'")
                meta[key] = [_scalar(item) for item in value[1:-1].split(",") if item.strip()]
                list_key = None
            else:
                meta[key] = _scalar(value)
                list_key = None
            continue
        if list_key is None:
            raise FrontmatterError(lineno, "an indented line has no parent key")
        stripped = raw.strip()
        items = meta[list_key]
        if stripped == "-" or stripped.startswith("- "):
            item = stripped[1:].strip()
            match = _KEY_VALUE.match(item)
            items.append({match.group(1): _scalar(match.group(2) or "")} if match else _scalar(item))
            continue
        match = _KEY_VALUE.match(stripped)
        if not match or not items or not isinstance(items[-1], dict):
            raise FrontmatterError(lineno, f"unexpected line in list {list_key!r}: {stripped!r}")
        items[-1][match.group(1)] = _scalar(match.group(2) or "")
    return meta, "\n".join(lines[end + 1:])


@dataclass(frozen=True)
class Note:
    path: Path  # absolute path
    rel: str  # repository-relative POSIX path, for example "topics/mcp/x.md"
    folder: str  # name of the topic folder that contains the file
    slug: str  # file name without ".md"
    meta: dict
    body: str

    @property
    def title(self) -> str:
        return str(self.meta.get("title", self.slug))

    @property
    def topics(self) -> list[str]:
        topics = self.meta.get("topics")
        return topics if isinstance(topics, list) else []


def topic_names(root: Path) -> list[str]:
    topics_dir = root / "topics"
    if not topics_dir.is_dir():
        return []
    return sorted(p.name for p in topics_dir.iterdir() if p.is_dir())


def note_paths(root: Path) -> list[Path]:
    return sorted(p for p in (root / "topics").glob("*/*.md") if p.name != "README.md")


def load_note(path: Path, root: Path) -> Note:
    meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
    return Note(
        path=path,
        rel=path.relative_to(root).as_posix(),
        folder=path.parent.name,
        slug=path.stem,
        meta=meta,
        body=body,
    )


def load_notes(root: Path) -> list[Note]:
    return [load_note(path, root) for path in note_paths(root)]
