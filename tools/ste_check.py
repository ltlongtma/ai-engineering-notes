#!/usr/bin/env python3
"""STE check for Markdown files. Wraps the vendored ste-lint.py.

1. Removes frontmatter, blockquotes, and Strict markers from the text.
2. Lints the remaining STE-flavored text. Hard findings are errors.
   Advisory findings and synonym rotation are warnings.
3. Lints each <!-- ste:strict --> block alone. The sentence cap is 20 words.
   Every finding is an error.
4. Reports line numbers of the original file.
"""
from __future__ import annotations

import importlib.util
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from notelib import REPO_ROOT, frontmatter_end

LINTER_PATH = Path(__file__).with_name("ste-lint.py")
STRICT_OPEN = "<!-- ste:strict -->"
STRICT_CLOSE = "<!-- /ste:strict -->"
FLAVORED_CAP = 25
STRICT_CAP = 20
# Advisory rules plus the lexical rule (one word, one meaning). Spec section 6: lexical rules are advisory.
FLAVORED_WARNINGS = {"passive-voice", "present-perfect", "synonym-rotation"}
FENCE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
BLOCKQUOTE = re.compile(r"^\s{0,3}>")
SKIP_DIRS = {".git", ".archify", "dist", "inbox", "node_modules"}
SKIP_PATHS = {"docs/superpowers", "tools/tests/fixtures"}


def _load_linter():
    spec = importlib.util.spec_from_file_location("ste_lint", LINTER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_LINTER = _load_linter()


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    col: int
    rule: str
    severity: str  # "error" or "warning"
    message: str
    match: str

    def format(self) -> str:
        return f"{self.path}:{self.line}:{self.col}: {self.severity}: {self.rule}: {self.message} [{self.match}]"


def _split_regions(lines: list[str], path: str):
    """Return (flavored_lines, strict_blocks, marker_findings).

    flavored_lines has the same length as lines. Removed lines are empty strings.
    strict_blocks is a list of (first_index, last_index) ranges of block content.
    """
    flavored = list(lines)
    blocks: list[tuple[int, int]] = []
    findings: list[Finding] = []
    end = frontmatter_end(lines)
    start = 0
    if end is not None:
        for index in range(end + 1):
            flavored[index] = ""
        start = end + 1
    fence: str | None = None
    open_index: int | None = None
    for index in range(start, len(lines)):
        line = lines[index]
        fence_match = FENCE.match(line)
        if fence is not None:
            if fence_match and fence_match.group(1)[0] == fence[0] and len(fence_match.group(1)) >= len(fence):
                fence = None
            if open_index is not None:
                flavored[index] = ""
            continue
        stripped = line.strip()
        if stripped == STRICT_OPEN:
            flavored[index] = ""
            if open_index is not None:
                findings.append(Finding(path, index + 1, 1, "strict-marker", "error",
                                        f"A Strict block opened at line {open_index + 1} is still open.",
                                        stripped))
            else:
                open_index = index
            continue
        if stripped == STRICT_CLOSE:
            flavored[index] = ""
            if open_index is None:
                findings.append(Finding(path, index + 1, 1, "strict-marker", "error",
                                        "This close marker has no open marker.", stripped))
            else:
                blocks.append((open_index + 1, index - 1))
                open_index = None
            continue
        if BLOCKQUOTE.match(line):
            flavored[index] = ""
            continue
        if fence_match:
            fence = fence_match.group(1)
        if open_index is not None:
            flavored[index] = ""
    if open_index is not None:
        findings.append(Finding(path, open_index + 1, 1, "strict-marker", "error",
                                "This Strict block has no close marker.", STRICT_OPEN))
    return flavored, blocks, findings


def _lint(lines: list[str], cap: int, path: str) -> list[dict]:
    previous = _LINTER.MAX_WORDS
    _LINTER.MAX_WORDS = cap
    try:
        findings, _ = _LINTER.lint("\n".join(lines), filename=path)
    finally:
        _LINTER.MAX_WORDS = previous
    return findings


def _to_finding(raw: dict, severity: str) -> Finding:
    return Finding(raw["file"], raw["line"], raw["col"], raw["rule"], severity, raw["message"], raw["match"])


def check_text(text: str, path: str = "<text>") -> list[Finding]:
    lines = text.split("\n")
    flavored, blocks, findings = _split_regions(lines, path)
    for raw in _lint(flavored, FLAVORED_CAP, path):
        severity = "warning" if raw["rule"] in FLAVORED_WARNINGS else "error"
        findings.append(_to_finding(raw, severity))
    for first, last in blocks:
        strict = [lines[i] if first <= i <= last and not BLOCKQUOTE.match(lines[i]) else ""
                  for i in range(len(lines))]
        findings.extend(_to_finding(raw, "error") for raw in _lint(strict, STRICT_CAP, path))
    return sorted(findings, key=lambda f: (f.line, f.col, f.rule))


def default_paths(root: Path) -> list[Path]:
    paths = []
    for path in sorted(root.rglob("*.md")):
        rel = path.relative_to(root)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if any(rel.as_posix().startswith(prefix + "/") for prefix in SKIP_PATHS):
            continue
        paths.append(path)
    return paths


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    paths = [Path(a) for a in args] if args else default_paths(REPO_ROOT)
    errors = warnings = 0
    for path in paths:
        try:
            shown = path.resolve().relative_to(REPO_ROOT).as_posix()
        except ValueError:
            shown = str(path)
        for finding in check_text(path.read_text(encoding="utf-8"), shown):
            print(finding.format())
            if finding.severity == "error":
                errors += 1
            else:
                warnings += 1
    print(f"ste_check: {len(paths)} files, {errors} errors, {warnings} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
