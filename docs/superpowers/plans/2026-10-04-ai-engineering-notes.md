# ai-engineering-notes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the private notebook repository from the spec. It includes the layout, the STE checks, the note checks, the index builder, the exports, the `kb-ingest` skill, and CI.

**Architecture:** Markdown notes in `topics/` are the source of truth. Four Python 3 scripts in `tools/` use the standard library only. They share one helper module (`tools/notelib.py`) for frontmatter and note discovery. `make check` runs the STE wrapper, the note checks, the index check, and the unit tests. A project skill in `.claude/skills/kb-ingest/` drives the two-phase ingest workflow. GitHub Actions run `make check` and publish Markdown exports.

**Tech Stack:** Python 3.10+ (standard library, `unittest`), GNU Make, GitHub Actions, and the vendored `ste-lint.py`. Local PDF exports use Pandoc, Google Chrome, and Mermaid 11.12.0 from jsDelivr. Optional diagrams use Archify 3.0.1.

**Spec:** `docs/superpowers/specs/2026-10-04-ai-engineering-notes-design.md`

## Global Constraints

- All repository content is in English and follows ASD-STE100 principles. Use the `asd-ste100` skill.
- Explanations use STE-flavored mode. Procedures, checklists, and prompt templates use Strict mode between `<!-- ste:strict -->` and `<!-- /ste:strict -->`.
- All tools in `tools/` use Python 3 and the standard library only. The floor is Python 3.10. CI runs Python 3.10.
- Do not change `tools/ste-lint.py`. It is a verbatim copy at commit `7d4a135a199a5d7447c4886bcd7ffe742a627bc9`.
- Generated sections sit between `<!-- index:start -->` and `<!-- index:end -->`. Nobody edits them by hand.
- Exported files go to `dist/`. Git ignores `dist/`.
- The `kb-ingest` skill does not commit and does not push. The owner commits notes.
- Keep the repo-local git identity (`ltlongtma` noreply). Do not change it.
- The active `gh` account is the work account. For this repository, prefix `gh` commands with `GH_TOKEN=$(gh auth token -u ltlongtma)`. Do not switch the active account.
- `~/.gitignore_global` ignores `docs/superpowers/`. The repository `.gitignore` keeps the line `!docs/superpowers/`. Do not remove it.
- Run all commands from the repository root: `/Users/longluu/Documents/Personal/ai-engineering-notes`.

## Resolved Open Items

### 1. Archify cannot export a static SVG from the command line

Evidence, collected on 2026-10-04 with Archify 3.0.1 (`~/.agents/skills/archify/skill-release.json`):

- `node bin/archify.mjs` lists these commands only: `render`, `compare`, `deliver`, `finalize`, `preview`, `validate`, `migrate`, `inspect`, `check`, `browser-check`, `visual-check`, `guide`, `brands`, `examples`, `doctor`, `demo`. No command writes SVG.
- The "Download SVG" function exists only in the viewer JavaScript in `assets/template.html`. It runs in a browser after a click.
- `visual-check` writes PNG screenshots of the viewport. These are review evidence, not diagram images.

Result: the spec section 7 fallback applies. A note with an Archify diagram also contains a short Mermaid diagram. The note links to the Archify HTML file.

A test run of `finalize` with `--out-dir .archify/<name>` showed these output files:

- `assets/<name>.html` (keep),
- `assets/<name>.json` (the source, keep),
- `assets/<name>.delivery.json` (delivery metadata, next to the HTML). Git ignores it.
- three receipt files in `.archify/<name>/`. Git ignores `.archify/`.

### 2. Vendored linter pin

| Item | Value |
|---|---|
| Repository | `danyuchn/asd-ste100-skill` (public, MIT, default branch `master`) |
| Commit | `7d4a135a199a5d7447c4886bcd7ffe742a627bc9` (2026-09-08, "fix: lint Markdown table cells as prose", the branch head on 2026-10-04) |
| File | `scripts/ste-lint.py`, SHA-256 `73bbd3de05b6517428ff6df73b789248a2d11f9eaf8d413fee56bbe71b5f863b` |
| License | `LICENSE`, SHA-256 `d3c674e8592076c9021a59b55177adbcba6fd7e1710082becb922522b22ec672`, "Copyright (c) 2026 Dustin Yuchen Teng" |

The installed skill copy at `~/.agents/skills/asd-ste100/scripts/ste-lint.py` has the same SHA-256.

## Plan Decisions

These decisions fill gaps in the spec. The owner can reject each one during plan review.

| # | Decision | Reason |
|---|---|---|
| D1 | `ste_check.py` with no arguments lints all Markdown files except `docs/superpowers/`, `inbox/`, `dist/`, `.archify/`, and `tools/tests/fixtures/`. | The spec says "all notes". The owner also requires STE for all repository content. The README, CONTRIBUTING, templates, and the skill pass today. |
| D2 | Severity mapping, outside Strict blocks: `semicolon`, `phrasal-verb`, `marketing-adjective`, `nominalization`, `long-sentence` (over 25 words), `dangling-conjunction` are errors. `passive-voice`, `present-perfect`, `synonym-rotation` are warnings. Inside Strict blocks: all findings are errors, and the cap is 20 words. | The linter marks `synonym-rotation` as hard. The spec says lexical rules are advisory in STE-flavored mode, and one word, one meaning is a lexical rule. |
| D3 | The STE-flavored pass removes the Strict blocks. Each Strict block is then linted alone. | A passive sentence in a Strict block gives one error, not one error plus one warning. |
| D4 | `notelib.py` parses a fixed YAML subset: `key: value`, `key: [a, b]`, and block lists of scalars or mappings. Other syntax is an error with a line number. | The standard library has no YAML parser. |
| D5 | `check_notes.py` also enforces three spec section 5 rules: `kebab-case` file names, `confidence` in `high`/`medium`/`low`, and `confidence: low` when the note contains `(unverified)`. | The spec states these rules. Each check is three lines. |
| D6 | Exports use explicit anchors `<a id="note-<folder>-<slug>"></a>`. A link to a note outside the export becomes text: `Title (not in this export: topics/x/y.md)`. Note headings move one level down. The exporter drops full-line HTML comments. | Explicit anchors do not depend on a slug algorithm. They work in GitHub, Pandoc, and MDX. |
| D7 | The PDF export renders Mermaid with `mermaid@11.12.0` from jsDelivr in headless Chrome. Without network access, the PDF shows the Mermaid source text. | The spec chose headless Chrome. Without this step, a shared PDF shows diagram source code. Tested on 2026-10-04 with Pandoc 3.12. |
| D8 | A claim with `Kind: experience` goes into the `Details` section in the words of the owner. The skill leaves `My takeaways` empty. | The spec says only the owner writes `My takeaways`, but it does not say where experience claims go. |
| D9 | `release.yml` runs `make check` before the export. A manual start needs a `tag` input. | A release must not publish notes that fail the checks. `gh release create` needs a tag. |

## Review Focus

1. A Strict marker without its pair, or a marker inside a fenced code block (for example in CONTRIBUTING). Expected: a missing pair is an error at the marker line, and a marker in code is plain text. Tests: Task 2.
2. A topic export where a `Related` link points to a note outside that topic. Expected: readable text that names the file, not a dead anchor. Test: Task 5.
3. A note that keeps an `(unverified)` claim but keeps `confidence: high`. Expected: `check_notes.py` reports an error. Test: Task 3.
4. A topic README with a hand edit inside the markers, or with no markers. Expected: `--check` fails, and the builder does not append a second list. Tests: Task 4.
5. MDX export of a note with braces in inline code and in fenced code. Expected: code stays unchanged, and only prose gets escapes. Test: Task 5.

## File Structure

| Path | Responsibility | Task |
|---|---|---|
| `.gitignore` | Ignore `dist/`, `.archify/`, Archify delivery files, `__pycache__/`. Keep `docs/superpowers/`. | 1 |
| `tools/ste-lint.py`, `tools/LICENSE.ste-lint` | Vendored linter and its license. | 1 |
| `tools/notelib.py` | Frontmatter parser, `Note` type, note and topic discovery. | 1 |
| `tools/tests/__init__.py`, `tools/tests/test_notelib.py` | Test package and parser tests. | 1 |
| `tools/ste_check.py` | STE wrapper: regions, modes, severity, line numbers. | 2 |
| `tools/tests/fixtures/ste/*.md`, `tools/tests/test_ste_check.py` | STE fixtures and tests. | 2 |
| `tools/check_notes.py` | Note checks from spec section 5. | 3 |
| `tools/tests/fixtures/kb/**`, `tools/tests/helpers.py`, `tools/tests/test_check_notes.py` | Fixture knowledge base, copy helper, tests. | 3 |
| `tools/build_index.py`, `tools/tests/test_build_index.py` | Index generation and `--check`. | 4 |
| `tools/export.py`, `tools/tests/test_export.py` | md, mdx, and pdf exports. | 5 |
| `README.md`, `CONTRIBUTING.md`, `Makefile`, `templates/*.md`, `topics/*/README.md`, `inbox/**` | Repository content and commands. | 6 |
| `.claude/skills/kb-ingest/SKILL.md` | The ingest skill. | 7 |
| `.github/workflows/check.yml`, `.github/workflows/release.yml` | CI and release. | 8 |

Test command for Tasks 1 to 5 (no Makefile yet):

```bash
python3 -m unittest discover -s tools/tests -t tools
```

`-t tools` puts `tools/` on `sys.path`. Thus tests can `import notelib` and `from tests.helpers import ...`.

---

### Task 1: Tool foundation: vendored linter and frontmatter parser

**Files:**
- Modify: `.gitignore`
- Create: `tools/ste-lint.py`, `tools/LICENSE.ste-lint` (download, do not edit)
- Create: `tools/notelib.py`
- Test: `tools/tests/__init__.py` (empty), `tools/tests/test_notelib.py`

**Interfaces:**
- Consumes: nothing.
- Produces, in `tools/notelib.py`:
  - `REPO_ROOT: Path` (the repository root)
  - `class FrontmatterError(ValueError)` with attribute `line: int`
  - `frontmatter_end(lines: list[str]) -> int | None` (index of the closing `---` line)
  - `parse_frontmatter(text: str) -> tuple[dict, str]` (meta, body)
  - `@dataclass(frozen=True) class Note` with fields `path: Path`, `rel: str`, `folder: str`, `slug: str`, `meta: dict`, `body: str`, and properties `title: str`, `topics: list[str]`
  - `topic_names(root: Path) -> list[str]`, `note_paths(root: Path) -> list[Path]`, `load_note(path: Path, root: Path) -> Note`, `load_notes(root: Path) -> list[Note]`

- [ ] **Step 1: Replace `.gitignore`**

```gitignore
# Global gitignore excludes docs/superpowers/. This repo keeps its specs and plans.
!docs/superpowers/
dist/
.archify/
topics/*/assets/*.delivery.json
__pycache__/
```

- [ ] **Step 2: Download the pinned linter and its license**

```bash
SHA=7d4a135a199a5d7447c4886bcd7ffe742a627bc9
mkdir -p tools/tests
curl -sSfL -o tools/ste-lint.py "https://raw.githubusercontent.com/danyuchn/asd-ste100-skill/$SHA/scripts/ste-lint.py"
curl -sSfL -o tools/LICENSE.ste-lint "https://raw.githubusercontent.com/danyuchn/asd-ste100-skill/$SHA/LICENSE"
shasum -a 256 tools/ste-lint.py tools/LICENSE.ste-lint
python3 tools/ste-lint.py --selftest
```

Expected:

```
73bbd3de05b6517428ff6df73b789248a2d11f9eaf8d413fee56bbe71b5f863b  tools/ste-lint.py
d3c674e8592076c9021a59b55177adbcba6fd7e1710082becb922522b22ec672  tools/LICENSE.ste-lint
selftest OK
```

If a hash is different, stop and tell the owner.

- [ ] **Step 3: Write the failing parser tests**

Create the empty file `tools/tests/__init__.py`. Create `tools/tests/test_notelib.py`:

```python
import unittest

from notelib import FrontmatterError, parse_frontmatter


class ParseFrontmatterTest(unittest.TestCase):
    def test_parses_scalars_inline_lists_and_mapping_lists(self):
        text = (
            "---\n"
            "title: Design MCP: tool schemas\n"
            "topics: [mcp, tool-calling]\n"
            "sources:\n"
            "  - url: https://example.com/a\n"
            "    accessed: 2026-10-04\n"
            "confidence: 'high'\n"
            "---\n"
            "## Summary\n"
        )
        meta, body = parse_frontmatter(text)
        self.assertEqual(meta["title"], "Design MCP: tool schemas")
        self.assertEqual(meta["topics"], ["mcp", "tool-calling"])
        self.assertEqual(meta["sources"], [{"url": "https://example.com/a", "accessed": "2026-10-04"}])
        self.assertEqual(meta["confidence"], "high")
        self.assertEqual(body, "## Summary\n")

    def test_missing_closing_line_is_an_error(self):
        with self.assertRaises(FrontmatterError):
            parse_frontmatter("---\ntitle: x\n## Summary\n")

    def test_unsupported_line_reports_its_line_number(self):
        with self.assertRaises(FrontmatterError) as caught:
            parse_frontmatter("---\ntitle: x\nnot a key\n---\n")
        self.assertEqual(caught.exception.line, 3)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 4: Run the tests to make sure they fail**

Run: `python3 -m unittest discover -s tools/tests -t tools`
Expected: FAIL with `ModuleNotFoundError: No module named 'notelib'`.

- [ ] **Step 5: Write `tools/notelib.py`**

```python
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
```

- [ ] **Step 6: Run the tests to make sure they pass**

Run: `python3 -m unittest discover -s tools/tests -t tools`
Expected: `Ran 3 tests` and `OK`.

- [ ] **Step 7: Commit**

```bash
git add .gitignore tools/ste-lint.py tools/LICENSE.ste-lint tools/notelib.py tools/tests/__init__.py tools/tests/test_notelib.py
git commit -m "feat(tools): vendor ste-lint at 7d4a135 and add frontmatter parser"
```

---

### Task 2: STE wrapper `ste_check.py`

**Files:**
- Create: `tools/ste_check.py`
- Create: `tools/tests/fixtures/ste/blockquote.md`, `passive.md`, `length.md`, `line-numbers.md`
- Test: `tools/tests/test_ste_check.py`

**Interfaces:**
- Consumes: `notelib.REPO_ROOT`, `notelib.frontmatter_end`. The vendored module `tools/ste-lint.py`: `lint(text: str, filename: str) -> tuple[list[dict], int]` and the module global `MAX_WORDS: int`. Each finding dict has the keys `file`, `line`, `col`, `rule`, `level`, `match`, `message`.
- Produces, in `tools/ste_check.py`:
  - `@dataclass(frozen=True) class Finding` with fields `path: str`, `line: int`, `col: int`, `rule: str`, `severity: str` (`"error"` or `"warning"`), `message: str`, `match: str`, and method `format() -> str`
  - `check_text(text: str, path: str = "<text>") -> list[Finding]`
  - `default_paths(root: Path) -> list[Path]`
  - CLI: `python3 tools/ste_check.py [PATH ...]`. Exit 1 if one or more errors exist.

The file name `ste-lint.py` has a hyphen. Thus `ste_check.py` loads it with `importlib`. To set the 20-word cap, `ste_check.py` sets `MAX_WORDS` for one call and restores it after the call. The linter reads `MAX_WORDS` at call time.

- [ ] **Step 1: Write the fixtures**

`tools/tests/fixtures/ste/blockquote.md` (the frontmatter and the blockquote contain violations. The wrapper must remove both.):

```markdown
---
title: Blockquote fixture
summary: The cache is cleared; the worker is restarted.
---

The agent reads the source.

> The cache is invalidated; the old entries are removed by the worker after the queue was drained and the team has seen many more failures than it expected.
```

`tools/tests/fixtures/ste/passive.md`:

```markdown
The file is deleted by the agent.

<!-- ste:strict -->
1. The file is deleted by the agent.
<!-- /ste:strict -->
```

`tools/tests/fixtures/ste/length.md` (each sentence has 22 words):

```markdown
The agent reads each claim from the input file and writes one review block for each claim in the report file today.

<!-- ste:strict -->
The agent reads each claim from the input file and writes one review block for each claim in the report file today.
<!-- /ste:strict -->
```

`tools/tests/fixtures/ste/line-numbers.md` (the semicolon is on line 7 of the file):

```markdown
---
title: Line number fixture
topics: [mcp]
---

The agent reads the file.
The agent writes the report; the owner reads it.
```

- [ ] **Step 2: Make sure the raw linter flags the fixtures**

Run: `python3 tools/ste-lint.py tools/tests/fixtures/ste/blockquote.md | tail -2`
Expected: `9 violations (3 hard, baseline 0)`. This proves that the blockquote test is not empty.

- [ ] **Step 3: Write the failing tests**

````python
import unittest
from pathlib import Path

from ste_check import check_text

FIXTURES = Path(__file__).parent / "fixtures" / "ste"


def check_fixture(name):
    return check_text((FIXTURES / name).read_text(encoding="utf-8"), name)


class SteCheckTest(unittest.TestCase):
    def test_frontmatter_and_blockquote_produce_no_finding(self):
        self.assertEqual(check_fixture("blockquote.md"), [])

    def test_passive_is_warning_outside_strict_and_error_inside(self):
        found = [(f.line, f.rule, f.severity) for f in check_fixture("passive.md")]
        self.assertEqual(found, [(1, "passive-voice", "warning"), (4, "passive-voice", "error")])

    def test_22_word_sentence_passes_outside_strict_and_fails_inside(self):
        found = [(f.line, f.rule, f.severity) for f in check_fixture("length.md")]
        self.assertEqual(found, [(4, "long-sentence", "error")])

    def test_line_number_matches_original_note(self):
        found = [(f.line, f.rule) for f in check_fixture("line-numbers.md")]
        self.assertEqual(found, [(7, "semicolon")])

    def test_unclosed_strict_block_is_an_error(self):
        found = [(f.line, f.rule, f.severity) for f in check_text("Intro.\n<!-- ste:strict -->\n1. Read the file.\n")]
        self.assertEqual(found, [(2, "strict-marker", "error")])

    def test_close_marker_without_open_marker_is_an_error(self):
        found = [(f.line, f.rule) for f in check_text("Intro.\n<!-- /ste:strict -->\n")]
        self.assertEqual(found, [(2, "strict-marker")])

    def test_marker_inside_fenced_code_is_text(self):
        text = "Use this marker:\n\n```markdown\n<!-- ste:strict -->\nThe file is deleted.\n```\n"
        self.assertEqual(check_text(text), [])

    def test_synonym_rotation_is_warning_outside_strict_and_error_inside(self):
        flavored = check_text("Check the file. Verify the output.\n")
        self.assertEqual([(f.rule, f.severity) for f in flavored], [("synonym-rotation", "warning")])
        strict = check_text("<!-- ste:strict -->\nCheck the file. Verify the output.\n<!-- /ste:strict -->\n")
        self.assertEqual([(f.rule, f.severity) for f in strict], [("synonym-rotation", "error")])


if __name__ == "__main__":
    unittest.main()
````

- [ ] **Step 4: Run the tests to make sure they fail**

Run: `python3 -m unittest discover -s tools/tests -t tools`
Expected: FAIL with `ModuleNotFoundError: No module named 'ste_check'`.

- [ ] **Step 5: Write `tools/ste_check.py`**

```python
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
```

Make it executable: `chmod +x tools/ste_check.py`.

- [ ] **Step 6: Run the tests to make sure they pass**

Run: `python3 -m unittest discover -s tools/tests -t tools`
Expected: `Ran 11 tests` and `OK`.

- [ ] **Step 7: Commit**

```bash
git add tools/ste_check.py tools/tests/test_ste_check.py tools/tests/fixtures/ste
git commit -m "feat(tools): add ste_check wrapper with Strict blocks and severity mapping"
```

---

### Task 3: Note checks `check_notes.py`

**Files:**
- Create: `tools/check_notes.py`
- Create: `tools/tests/fixtures/kb/` (a small knowledge base, see Step 1)
- Create: `tools/tests/helpers.py`
- Test: `tools/tests/test_check_notes.py`

**Interfaces:**
- Consumes: `notelib.REPO_ROOT`, `FrontmatterError`, `load_note`, `note_paths`.
- Produces, in `tools/check_notes.py`:
  - `check_note(path: Path, root: Path) -> list[str]`. Each string is `"<repo-relative path>: <message>"`.
  - `check_repo(root: Path) -> list[str]`
  - `related_section(body: str) -> str`
  - CLI: `python3 tools/check_notes.py [--root DIR]`. Exit 1 if one or more errors exist.
- Produces, in `tools/tests/helpers.py`: `copy_kb(test: unittest.TestCase) -> Path` and `edit(path: Path, old: str, new: str) -> None`. Tasks 4 and 5 use them.
- Produces the fixture knowledge base. Tasks 4 and 5 use it:
  - `topics/mcp/schema-design.md`: topics `[mcp, tool-calling]`. Its `Related` link points to `../tool-calling/error-handling.md#details`.
  - `topics/tool-calling/error-handling.md`: topics `[tool-calling]`. It contains `{...}` and `<tool_result>` in prose, `{braces}` in inline code, and a fenced JSON block.
  - `topics/tokens-and-cost/`: no notes.

- [ ] **Step 1: Write the fixture knowledge base**

`tools/tests/fixtures/kb/README.md`:

```markdown
# Fixture knowledge base

## Topics

<!-- index:start -->
<!-- index:end -->
```

`tools/tests/fixtures/kb/topics/mcp/README.md`:

```markdown
# mcp

Scope: MCP servers, clients, transports, and security.

## Notes

<!-- index:start -->
<!-- index:end -->
```

`tools/tests/fixtures/kb/topics/tool-calling/README.md`:

```markdown
# tool-calling

Scope: Tool design, schemas, error handling.

## Notes

<!-- index:start -->
<!-- index:end -->
```

`tools/tests/fixtures/kb/topics/tokens-and-cost/README.md`:

```markdown
# tokens-and-cost

Scope: Token counting, prompt caching, model choice by cost.

## Notes

<!-- index:start -->
<!-- index:end -->
```

`tools/tests/fixtures/kb/topics/mcp/schema-design.md`:

```markdown
---
title: Design MCP tool schemas for low token cost
topics: [mcp, tool-calling]
sources:
  - url: https://modelcontextprotocol.io/specification
    accessed: 2026-10-04
verified_at: 2026-10-04
confidence: high
last_reviewed: 2026-10-04
---

## Summary

Short tool descriptions use fewer tokens.

## Details

A schema such as `{"type": "object"}` costs tokens in each request.

## Related

- [Handle tool errors](../tool-calling/error-handling.md#details)

## Sources

- MCP specification: tool definition format.
```

`tools/tests/fixtures/kb/topics/tool-calling/error-handling.md`:

````markdown
---
title: Handle tool errors
topics: [tool-calling]
sources:
  - url: https://docs.anthropic.com/en/docs/build-with-claude/tool-use
    accessed: 2026-10-04
verified_at: 2026-10-04
confidence: medium
last_reviewed: 2026-10-04
---

## Summary

Return the error text to the model in a {"is_error": true} result.

## Details

Use a <tool_result> block. Keep `{braces}` in inline code.

```json
{"is_error": true}
```

## Related

- [Design MCP tool schemas](../mcp/schema-design.md)

## Sources

- Tool use guide: error result format.
````

The generated sections in the fixture READMEs stay empty on purpose. Task 4 tests build them in a temporary copy.

- [ ] **Step 2: Write the test helpers**

`tools/tests/helpers.py`:

```python
import shutil
import tempfile
import unittest
from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures"


def copy_kb(test: unittest.TestCase) -> Path:
    """Copy fixtures/kb to a temporary directory that the test removes at cleanup."""
    tmp = tempfile.TemporaryDirectory()
    test.addCleanup(tmp.cleanup)
    root = Path(tmp.name) / "kb"
    shutil.copytree(FIXTURES / "kb", root)
    return root


def edit(path: Path, old: str, new: str) -> None:
    """Replace one exact substring in a fixture copy. Fail if the substring is absent."""
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise AssertionError(f"{old!r} not in {path}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
```

- [ ] **Step 3: Write the failing tests**

`tools/tests/test_check_notes.py`. There is one test for each error type in spec section 5, plus the three D5 rules and one test for broken frontmatter:

```python
import unittest

from check_notes import check_repo
from tests.helpers import copy_kb, edit

NOTE = "topics/mcp/schema-design.md"


class CheckNotesTest(unittest.TestCase):
    def setUp(self):
        self.root = copy_kb(self)
        self.note = self.root / NOTE

    def assertOneError(self, fragment):
        errors = check_repo(self.root)
        self.assertEqual(len(errors), 1, errors)
        self.assertIn(fragment, errors[0])

    def test_fixture_has_no_errors(self):
        self.assertEqual(check_repo(self.root), [])

    def test_primary_topic_must_match_folder(self):
        edit(self.note, "topics: [mcp, tool-calling]", "topics: [tool-calling, mcp]")
        self.assertOneError("topics[0] is 'tool-calling'")

    def test_each_topic_needs_a_folder(self):
        edit(self.note, "topics: [mcp, tool-calling]", "topics: [mcp, agents]")
        self.assertOneError("the topic 'agents' has no folder")

    def test_related_link_must_resolve(self):
        edit(self.note, "../tool-calling/error-handling.md", "../tool-calling/missing.md")
        self.assertOneError("the Related link '../tool-calling/missing.md#details' does not resolve")

    def test_sources_must_not_be_empty(self):
        edit(self.note, "sources:\n  - url: https://modelcontextprotocol.io/specification\n    accessed: 2026-10-04\n",
             "sources: []\n")
        self.assertOneError("'sources' is missing or empty")

    def test_required_field_must_exist(self):
        edit(self.note, "verified_at: 2026-10-04\n", "")
        self.assertOneError("the required frontmatter field 'verified_at' is missing")

    def test_confidence_must_be_high_medium_or_low(self):
        edit(self.note, "confidence: high", "confidence: certain")
        self.assertOneError("'confidence' is 'certain'")

    def test_unverified_claim_needs_low_confidence(self):
        edit(self.note, "use fewer tokens.", "use fewer tokens (unverified).")
        self.assertOneError("contains '(unverified)'")

    def test_file_name_must_be_kebab_case(self):
        self.note.rename(self.note.with_name("Schema_Design.md"))
        edit(self.root / "topics/tool-calling/error-handling.md", "../mcp/schema-design.md", "../mcp/Schema_Design.md")
        self.assertOneError("is not kebab-case")

    def test_broken_frontmatter_is_one_error(self):
        edit(self.note, "confidence: high\n", "confidence high\n")
        self.assertOneError("frontmatter line")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 4: Run the tests to make sure they fail**

Run: `python3 -m unittest discover -s tools/tests -t tools`
Expected: FAIL with `ModuleNotFoundError: No module named 'check_notes'`.

- [ ] **Step 5: Write `tools/check_notes.py`**

```python
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
```

Make it executable: `chmod +x tools/check_notes.py`.

- [ ] **Step 6: Run the tests to make sure they pass**

Run: `python3 -m unittest discover -s tools/tests -t tools`
Expected: `Ran 21 tests` and `OK`.

- [ ] **Step 7: Commit**

```bash
git add tools/check_notes.py tools/tests/helpers.py tools/tests/test_check_notes.py tools/tests/fixtures/kb
git commit -m "feat(tools): add check_notes with fixture knowledge base"
```

---

### Task 4: Index builder `build_index.py`

**Files:**
- Create: `tools/build_index.py`
- Test: `tools/tests/test_build_index.py`

**Interfaces:**
- Consumes: `notelib.REPO_ROOT`, `FrontmatterError`, `Note`, `load_notes`, `topic_names`. `tests.helpers.copy_kb`, `edit`.
- Produces, in `tools/build_index.py`:
  - `START = "<!-- index:start -->"`, `END = "<!-- index:end -->"`
  - `class IndexMarkerError(Exception)`
  - `replace_section(text: str, content: str, rel: str) -> str`
  - `topic_scope(readme_text: str, rel: str) -> str`. It reads the line that starts with `Scope: `.
  - `render_topic_list(topic: str, notes: list[Note]) -> str`, `render_root_list(root: Path, notes: list[Note]) -> str`
  - `expected_files(root: Path) -> dict[Path, str]`
  - CLI: `python3 tools/build_index.py [--check] [--root DIR]`
- Output format, which Task 6 and Task 7 rely on:
  - Topic list, primary note: `- [Title](slug.md)`
  - Topic list, secondary note: `- [Title](../<primary>/slug.md) (primary topic: <primary>)`
  - Topic list, no notes: `No notes yet.`
  - Root list: `- [<topic>](topics/<topic>/README.md): <scope> Notes: <N>.`

- [ ] **Step 1: Write the failing tests**

```python
import contextlib
import io
import unittest

from build_index import IndexMarkerError, expected_files, main
from tests.helpers import copy_kb, edit


class BuildIndexTest(unittest.TestCase):
    def setUp(self):
        self.root = copy_kb(self)

    def run_main(self, *args):
        with contextlib.redirect_stdout(io.StringIO()):
            return main([*args, "--root", str(self.root)])

    def read(self, rel):
        return (self.root / rel).read_text(encoding="utf-8")

    def test_secondary_topic_note_appears_in_both_topic_indexes(self):
        self.assertEqual(self.run_main(), 0)
        self.assertIn("- [Design MCP tool schemas for low token cost](schema-design.md)\n",
                      self.read("topics/mcp/README.md"))
        self.assertIn("- [Design MCP tool schemas for low token cost](../mcp/schema-design.md) (primary topic: mcp)\n",
                      self.read("topics/tool-calling/README.md"))

    def test_root_index_lists_scope_and_note_count(self):
        self.run_main()
        root_readme = self.read("README.md")
        self.assertIn("- [tool-calling](topics/tool-calling/README.md): Tool design, schemas, error handling. Notes: 2.\n",
                      root_readme)
        self.assertIn("Notes: 0.\n", root_readme)

    def test_topic_without_notes_says_so(self):
        self.run_main()
        self.assertIn("<!-- index:start -->\nNo notes yet.\n<!-- index:end -->",
                      self.read("topics/tokens-and-cost/README.md"))

    def test_check_fails_when_stale_and_passes_after_build(self):
        self.assertEqual(self.run_main("--check"), 1)
        self.assertEqual(self.run_main(), 0)
        self.assertEqual(self.run_main("--check"), 0)

    def test_hand_edit_inside_markers_makes_check_fail(self):
        self.run_main()
        edit(self.root / "topics/mcp/README.md", "<!-- index:end -->", "- extra line\n<!-- index:end -->")
        self.assertEqual(self.run_main("--check"), 1)

    def test_missing_markers_is_an_error_not_a_silent_append(self):
        edit(self.root / "topics/mcp/README.md", "<!-- index:start -->\n", "")
        with self.assertRaises(IndexMarkerError):
            expected_files(self.root)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tests to make sure they fail**

Run: `python3 -m unittest discover -s tools/tests -t tools`
Expected: FAIL with `ModuleNotFoundError: No module named 'build_index'`.

- [ ] **Step 3: Write `tools/build_index.py`**

```python
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
```

Make it executable: `chmod +x tools/build_index.py`.

- [ ] **Step 4: Run the tests to make sure they pass**

Run: `python3 -m unittest discover -s tools/tests -t tools`
Expected: `Ran 27 tests` and `OK`.

- [ ] **Step 5: Commit**

```bash
git add tools/build_index.py tools/tests/test_build_index.py
git commit -m "feat(tools): add build_index with --check"
```

---

### Task 5: Exports `export.py` (md, mdx, pdf)

**Files:**
- Create: `tools/export.py`
- Test: `tools/tests/test_export.py`

**Interfaces:**
- Consumes: `notelib.REPO_ROOT`, `FrontmatterError`, `Note`, `load_notes`, `topic_names`. `tests.helpers.copy_kb`.
- Produces, in `tools/export.py`:
  - `class ExportError(Exception)`
  - `select_notes(notes: list[Note], topic: str) -> list[Note]`. `topic` is a folder name or `"all"`.
  - `anchor_id(note: Note) -> str`. It returns `"note-<folder>-<slug>"`.
  - `render_md(notes: list[Note], topic: str, root: Path) -> str`
  - `render_mdx(notes: list[Note], topic: str, root: Path) -> str`
  - `escape_mdx(text: str) -> str`
  - `render_pdf(markdown: str, pdf_path: Path, title: str) -> None`
  - `export(root: Path, fmt: str, topic: str, out_dir: Path) -> Path`. It writes `out_dir/<topic>.<md|mdx|pdf>`.
  - CLI: `python3 tools/export.py --format md|mdx|pdf --topic <name>|all [--root DIR]`. The output goes to `<root>/dist/`.
- The environment variable `CHROME` can give the browser path for the PDF export.

- [ ] **Step 1: Write the failing tests**

````python
import re
import unittest

from export import ExportError, export, render_md, render_mdx
from notelib import load_notes
from tests.helpers import copy_kb


class ExportTest(unittest.TestCase):
    def setUp(self):
        self.root = copy_kb(self)
        self.notes = load_notes(self.root)

    def test_internal_links_point_to_note_anchors(self):
        text = render_md(self.notes, "all", self.root)
        self.assertIn('<a id="note-tool-calling-error-handling"></a>', text)
        self.assertIn("- [Handle tool errors](#note-tool-calling-error-handling)", text)
        self.assertIn("- [Design MCP tool schemas](#note-mcp-schema-design)", text)
        for target in re.findall(r"\]\(#([^)]+)\)", text):
            self.assertIn(f'<a id="{target}"></a>', text)

    def test_link_to_note_outside_the_export_becomes_text(self):
        text = render_md(self.notes, "mcp", self.root)
        self.assertIn("Handle tool errors (not in this export: topics/tool-calling/error-handling.md)", text)

    def test_note_headings_move_one_level_down(self):
        text = render_md(self.notes, "mcp", self.root)
        self.assertIn("## Design MCP tool schemas for low token cost\n", text)
        self.assertIn("\n### Summary\n", text)
        self.assertNotIn("\n## Summary\n", text)

    def test_topic_export_includes_cross_listed_notes(self):
        text = render_md(self.notes, "tool-calling", self.root)
        self.assertIn("## Handle tool errors\n", text)
        self.assertIn("## Design MCP tool schemas for low token cost\n", text)

    def test_all_export_contains_each_note_one_time(self):
        text = render_md(self.notes, "all", self.root)
        self.assertEqual(text.count('<a id="note-mcp-schema-design"></a>'), 1)
        self.assertEqual(text.count('<a id="note-tool-calling-error-handling"></a>'), 1)

    def test_mdx_escapes_braces_and_angle_brackets_outside_code(self):
        text = render_mdx(self.notes, "tool-calling", self.root)
        self.assertIn('in a \\{"is_error": true\\} result.', text)
        self.assertIn("Use a \\<tool_result> block.", text)
        self.assertIn("Keep `{braces}` in inline code.", text)
        self.assertIn('```json\n{"is_error": true}\n```', text)
        self.assertIn('A schema such as `{"type": "object"}` costs', text)
        self.assertTrue(text.startswith('---\ntitle: "AI engineering notes: tool-calling"\n---\n'))
        self.assertIn('<a id="note-mcp-schema-design"></a>', text)

    def test_unknown_topic_is_an_error(self):
        with self.assertRaises(ExportError):
            export(self.root, "md", "agents", self.root / "dist")

    def test_topic_without_notes_writes_a_short_file(self):
        path = export(self.root, "md", "tokens-and-cost", self.root / "dist")
        self.assertEqual(path.name, "tokens-and-cost.md")
        self.assertIn("No notes for this topic.", path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
````

- [ ] **Step 2: Run the tests to make sure they fail**

Run: `python3 -m unittest discover -s tools/tests -t tools`
Expected: FAIL with `ModuleNotFoundError: No module named 'export'`.

- [ ] **Step 3: Write `tools/export.py`**

````python
#!/usr/bin/env python3
"""Export notes as one combined file: md (default), mdx, or pdf.

md and mdx use the standard library only. pdf needs Pandoc and Google Chrome or Chromium.
"""
from __future__ import annotations

import argparse
import html
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from notelib import REPO_ROOT, FrontmatterError, Note, load_notes, topic_names

FORMATS = ("md", "mdx", "pdf")
MERMAID_VERSION = "11.12.0"
FENCE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
INLINE_CODE = re.compile(r"`[^`\n]*`")
LINK = re.compile(r"(!?)\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
EXTERNAL = re.compile(r"^[a-z][a-z0-9+.-]*:", re.I)
HEADING = re.compile(r"^(#{1,5}) ")
COMMENT_LINE = re.compile(r"^\s*<!--.*-->\s*$")
MDX_SPECIAL = re.compile(r"(?<!\\)([{}<])")
CHROME_CANDIDATES = (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "google-chrome",
    "google-chrome-stable",
    "chromium",
    "chromium-browser",
)


class ExportError(Exception):
    """The export cannot run. The message tells the user what to do."""


def map_prose(text: str, fn) -> str:
    """Apply fn to text outside fenced code blocks and inline code spans."""
    out: list[str] = []
    fence: str | None = None
    for line in text.split("\n"):
        match = FENCE.match(line)
        if fence is not None:
            if match and match.group(1)[0] == fence[0] and len(match.group(1)) >= len(fence):
                fence = None
            out.append(line)
            continue
        if match:
            fence = match.group(1)
            out.append(line)
            continue
        parts: list[str] = []
        position = 0
        for code in INLINE_CODE.finditer(line):
            parts.append(fn(line[position:code.start()]))
            parts.append(code.group(0))
            position = code.end()
        parts.append(fn(line[position:]))
        out.append("".join(parts))
    return "\n".join(out)


def map_lines_outside_code(text: str, fn) -> str:
    """Apply fn to whole lines outside fenced code blocks. fn returns None to drop the line."""
    out: list[str] = []
    fence: str | None = None
    for line in text.split("\n"):
        match = FENCE.match(line)
        if fence is not None:
            if match and match.group(1)[0] == fence[0] and len(match.group(1)) >= len(fence):
                fence = None
            out.append(line)
            continue
        if match:
            fence = match.group(1)
            out.append(line)
            continue
        result = fn(line)
        if result is not None:
            out.append(result)
    return "\n".join(out)


def anchor_id(note: Note) -> str:
    return f"note-{note.folder}-{note.slug}"


def select_notes(notes: list[Note], topic: str) -> list[Note]:
    chosen = notes if topic == "all" else [n for n in notes if topic in n.topics]
    return sorted(chosen, key=lambda n: (n.folder, n.title.casefold(), n.rel))


def rewrite_links(note: Note, root: Path, anchors: dict[str, str]) -> str:
    def replace(match: re.Match) -> str:
        bang, text, target = match.groups()
        if EXTERNAL.match(target):
            return match.group(0)
        if target.startswith("#"):
            return f"{bang}[{text}](#{anchor_id(note)})"
        resolved = (note.path.parent / target.split("#", 1)[0]).resolve()
        try:
            rel = resolved.relative_to(root.resolve()).as_posix()
        except ValueError:
            rel = target
        if rel in anchors and not bang:
            return f"[{text}](#{anchors[rel]})"
        return f"{text} (not in this export: {rel})"

    return map_prose(note.body, lambda prose: LINK.sub(replace, prose))


def note_section(note: Note, root: Path, anchors: dict[str, str], escape) -> str:
    body = rewrite_links(note, root, anchors)
    body = map_lines_outside_code(body, lambda line: None if COMMENT_LINE.match(line) else HEADING.sub(r"#\1 ", line))
    body = escape(body).strip("\n")
    meta = note.meta
    facts = (f"Topics: {', '.join(note.topics)}. Confidence: {meta.get('confidence', '')}. "
             f"Verified: {meta.get('verified_at', '')}.")
    return f'<a id="{anchor_id(note)}"></a>\n\n## {escape(note.title)}\n\n{escape(facts)}\n\n{body}\n'


def render(notes: list[Note], topic: str, root: Path, escape=lambda text: text) -> str:
    chosen = select_notes(notes, topic)
    label = "all topics" if topic == "all" else topic
    parts = [f"# AI engineering notes: {label}\n"]
    if not chosen:
        parts.append("No notes for this topic.\n")
        return "\n".join(parts)
    anchors = {n.rel: anchor_id(n) for n in chosen}
    contents = "\n".join(f"- [{escape(n.title)}](#{anchor_id(n)})" for n in chosen)
    parts.append(f"## Contents\n\n{contents}\n")
    parts.extend(note_section(n, root, anchors, escape) for n in chosen)
    return "\n".join(parts)


def render_md(notes: list[Note], topic: str, root: Path) -> str:
    return render(notes, topic, root)


def escape_mdx(text: str) -> str:
    return map_prose(text, lambda prose: MDX_SPECIAL.sub(r"\\\1", prose))


def render_mdx(notes: list[Note], topic: str, root: Path) -> str:
    label = "all topics" if topic == "all" else topic
    frontmatter = f'---\ntitle: "AI engineering notes: {label}"\n---\n\n'
    return frontmatter + render(notes, topic, root, escape=escape_mdx)


def mermaid_to_html(markdown: str) -> str:
    """Replace ```mermaid fences with <pre class="mermaid"> blocks for the browser to render."""
    out: list[str] = []
    block: list[str] | None = None
    for line in markdown.split("\n"):
        if block is None and line.strip() == "```mermaid":
            block = []
        elif block is not None and line.strip() == "```":
            out.append('<pre class="mermaid">' + html.escape("\n".join(block), quote=False) + "</pre>")
            block = None
        elif block is not None:
            block.append(line)
        else:
            out.append(line)
    if block is not None:
        out.append("```mermaid")
        out.extend(block)
    return "\n".join(out)


MERMAID_HEAD = f"""<script type="module">
import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@{MERMAID_VERSION}/dist/mermaid.esm.min.mjs";
mermaid.initialize({{ startOnLoad: false, theme: "neutral" }});
await mermaid.run({{ querySelector: "pre.mermaid" }});
</script>
<style>body {{ max-width: 46rem; margin: 2rem auto; font-family: sans-serif; line-height: 1.5; }}
pre {{ white-space: pre-wrap; }}</style>
"""


def find_chrome() -> str | None:
    configured = os.environ.get("CHROME")
    if configured:
        return configured
    for candidate in CHROME_CANDIDATES:
        if Path(candidate).is_file():
            return candidate
        found = shutil.which(candidate)
        if found:
            return found
    return None


def render_pdf(markdown: str, pdf_path: Path, title: str) -> None:
    pandoc = shutil.which("pandoc")
    if not pandoc:
        raise ExportError("Pandoc is not installed. Install Pandoc, then run the export again.")
    chrome = find_chrome()
    if not chrome:
        raise ExportError("Chrome is not found. Set the CHROME variable to the browser path.")
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        (work / "in.md").write_text(mermaid_to_html(markdown), encoding="utf-8")
        (work / "head.html").write_text(MERMAID_HEAD, encoding="utf-8")
        page = work / "out.html"
        subprocess.run([pandoc, str(work / "in.md"), "--from", "markdown", "--standalone",
                        "--metadata", f"pagetitle={title}", "--include-in-header", str(work / "head.html"),
                        "--output", str(page)], check=True)
        pdf_path.unlink(missing_ok=True)
        subprocess.run([chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                        "--virtual-time-budget=15000", f"--print-to-pdf={pdf_path}", page.as_uri()],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if not pdf_path.is_file() or pdf_path.stat().st_size == 0:
        raise ExportError(f"Chrome did not write {pdf_path}.")


def export(root: Path, fmt: str, topic: str, out_dir: Path) -> Path:
    if topic != "all" and topic not in topic_names(root):
        known = ", ".join(topic_names(root))
        raise ExportError(f"The topic '{topic}' does not exist. Known topics: {known}, all.")
    notes = load_notes(root)
    out_dir.mkdir(parents=True, exist_ok=True)
    if fmt == "mdx":
        path = out_dir / f"{topic}.mdx"
        path.write_text(render_mdx(notes, topic, root), encoding="utf-8")
        return path
    markdown = render_md(notes, topic, root)
    if fmt == "pdf":
        path = out_dir / f"{topic}.pdf"
        render_pdf(markdown, path, f"AI engineering notes: {topic}")
        return path
    path = out_dir / f"{topic}.md"
    path.write_text(markdown, encoding="utf-8")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--format", choices=FORMATS, default="md")
    parser.add_argument("--topic", required=True, help="a topic folder name, or 'all'")
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help="repository root")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        path = export(root, args.format, args.topic, root / "dist")
    except (ExportError, FrontmatterError, subprocess.CalledProcessError) as error:
        print(f"error: {error}")
        return 1
    print(f"wrote {path.relative_to(root).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
````

Make it executable: `chmod +x tools/export.py`.

- [ ] **Step 4: Run the tests to make sure they pass**

Run: `python3 -m unittest discover -s tools/tests -t tools`
Expected: `Ran 35 tests` and `OK`.

- [ ] **Step 5: Smoke-test the PDF export with a Mermaid diagram**

The PDF path has no unit test, because it needs Pandoc, Chrome, and network access. Run it on a fixture copy that contains a Mermaid block with a blank line:

```bash
rm -rf /tmp/kb-pdf && cp -R tools/tests/fixtures/kb /tmp/kb-pdf
python3 - <<'EOF'
from pathlib import Path
p = Path("/tmp/kb-pdf/topics/mcp/schema-design.md")
p.write_text(p.read_text().replace("## Related", "```mermaid\nflowchart LR\n  A[Client] --> B[Server]\n\n  B --> C[Tool]\n```\n\n## Related", 1))
EOF
python3 tools/export.py --format pdf --topic mcp --root /tmp/kb-pdf
sips -s format png /tmp/kb-pdf/dist/mcp.pdf --out /tmp/kb-pdf/page.png
```

Expected: `wrote dist/mcp.pdf`. Open `/tmp/kb-pdf/page.png`. The page shows three boxes (Client, Server, Tool) with arrows, not Mermaid source text. The Related item reads `Handle tool errors (not in this export: topics/tool-calling/error-handling.md)`.

- [ ] **Step 6: Smoke-test the CLI errors and the MDX file**

```bash
python3 tools/export.py --format md --topic bogus --root /tmp/kb-pdf; echo "exit=$?"
python3 tools/export.py --format mdx --topic all --root /tmp/kb-pdf
```

Expected: `error: The topic 'bogus' does not exist. Known topics: mcp, tokens-and-cost, tool-calling, all.`, then `exit=1`, then `wrote dist/all.mdx`.

- [ ] **Step 7: Commit**

```bash
git add tools/export.py tools/tests/test_export.py
git commit -m "feat(tools): add md, mdx, and pdf exports"
```

---

### Task 6: Repository content, Makefile, and the first green `make check`

**Files:**
- Create: `Makefile`, `README.md`, `CONTRIBUTING.md`
- Create: `templates/note.md`, `templates/review.md`
- Create: `topics/context-and-memory/README.md`, `topics/tokens-and-cost/README.md`, `topics/tool-calling/README.md`, `topics/mcp/README.md`
- Create: `inbox/links.md`, `inbox/notes/.gitkeep`, `inbox/archive/.gitkeep`

**Interfaces:**
- Consumes: all four tools. The `build_index.py` output format from Task 4. The `Scope: ` line rule from Task 4.
- Produces: the Make targets `check`, `lint`, `notes`, `index-check`, `test`, `index`, `export-md`. Task 7 and Task 8 use `make check` and `make export-md`. The skill in Task 7 uses `make index` and `make check`.

- [ ] **Step 1: Write the topic READMEs**

Each topic README has the same form. Only the name and the scope change. Create the four files with this command:

```bash
write_topic() {
  mkdir -p "topics/$1"
  printf '# %s\n\nScope: %s\n\n## Notes\n\nThe tool `tools/build_index.py` writes this list. Do not edit it.\n\n<!-- index:start -->\n<!-- index:end -->\n' "$1" "$2" > "topics/$1/README.md"
}
write_topic context-and-memory "Context windows, short-term and long-term memory, compaction, retrieval for agents."
write_topic tokens-and-cost "Token counting, prompt caching, model choice by cost."
write_topic tool-calling "Tool design, schemas, error handling."
write_topic mcp "MCP servers, clients, transports, and security."
```

Result for `topics/mcp/README.md`, before `make index`:

```markdown
# mcp

Scope: MCP servers, clients, transports, and security.

## Notes

The tool `tools/build_index.py` writes this list. Do not edit it.

<!-- index:start -->
<!-- index:end -->
```

- [ ] **Step 2: Write the inbox**

```bash
mkdir -p inbox/notes inbox/archive
touch inbox/notes/.gitkeep inbox/archive/.gitkeep
printf '# Links to ingest\n\nWrite one URL on each line. You can add a comment after "#".\n\n' > inbox/links.md
```

- [ ] **Step 3: Write the templates**

`templates/note.md`:

```markdown
---
title: Write the title as one clear statement
topics: [primary-topic, secondary-topic]
sources:
  - url: https://example.com/source
    accessed: 2026-10-04
verified_at: 2026-10-04
confidence: high
last_reviewed: 2026-10-04
---

## Summary

## Details

## My takeaways

## Related

## Sources
```

`templates/review.md`:

```markdown
# Review: <input name>

Input: `<path or URL>`
Date: <YYYY-MM-DD>

Write one decision in each `Decision:` line. Put an `x` in one box. For `edit`, write the new text after `edit:`.
Phase 2 stops if one or more `Decision:` lines have no mark.

## Claims

### C1: "<short quote from the input>"
Kind: source
Status: ✅ correct
Proposal: Keep the claim.
Sources: <url> (checked <YYYY-MM-DD>)
Decision: [ ] accept  [ ] reject  [ ] edit: ...

## Placement

Primary topic: <topic>
Secondary topics: <topic>, <topic>
New topic: none
Notes: one new note `<topic>/<note-slug>.md`
Diagram: none
Decision: [ ] accept  [ ] reject  [ ] edit: ...
```

- [ ] **Step 4: Write `README.md`**

```markdown
# AI engineering notes

This repository is a personal notebook of AI engineering knowledge and experience.

- Goal 1: Keep knowledge so that the owner can read it again later.
- Goal 2: Share selected parts with other teams.

## How it works

1. The owner puts raw inputs in `inbox/`.
2. The `kb-ingest` skill extracts claims, verifies them, and writes a review report.
3. The owner records a decision for each claim in the report.
4. The skill writes or updates notes in `topics/`, then runs `make check`.
5. The owner reads the diff and commits.

`CONTRIBUTING.md` gives the full steps, the note template, and the writing rules.

## Writing standard

The text in this repository follows the principles of ASD-STE100 Simplified Technical English.
The repository does not claim certified STE compliance.
The linter does not contain the official ASD dictionary.

## Commands

| Command | Result |
|---|---|
| `make check` | Runs the STE linter, the note checks, the index check, and the unit tests. |
| `make index` | Writes the note lists in this file and in each topic README. |
| `python3 tools/export.py --format md --topic mcp` | Writes `dist/mcp.md`. Use `--topic all` for all notes. |
| `python3 tools/export.py --format mdx --topic all` | Writes `dist/all.mdx`. |
| `python3 tools/export.py --format pdf --topic all` | Writes `dist/all.pdf`. Needs Pandoc and Google Chrome. |

## Topics

The tool `tools/build_index.py` writes this list. Do not edit it.

<!-- index:start -->
- [context-and-memory](topics/context-and-memory/README.md): Context windows, short-term and long-term memory, compaction, retrieval for agents. Notes: 0.
- [mcp](topics/mcp/README.md): MCP servers, clients, transports, and security. Notes: 0.
- [tokens-and-cost](topics/tokens-and-cost/README.md): Token counting, prompt caching, model choice by cost. Notes: 0.
- [tool-calling](topics/tool-calling/README.md): Tool design, schemas, error handling. Notes: 0.
<!-- index:end -->
```

- [ ] **Step 5: Write `CONTRIBUTING.md`**

````markdown
# Contributing

This file tells you how to add knowledge to the repository.

## Before you start

1. Install Python 3.10 or later.
2. Install the STE skill: `npx skills add danyuchn/asd-ste100-skill`.
3. For PDF exports, install Pandoc and Google Chrome.

## Add an input

Put each input in `inbox/`:

| Input | Location |
|---|---|
| A web page | Add the URL as one line in `inbox/links.md`. You can add a comment after `#`. |
| An article or a document | Copy the `.pdf`, `.md`, or `.txt` file to `inbox/`. |
| Your own insight | Write a `.md` file in `inbox/notes/`. |

## Run phase 1: ingest

Ask the agent: "Run kb-ingest phase 1."

The skill writes one review report for each input: `inbox/<slug>.review.md`.
The skill does not change notes in phase 1.

## Review the report

Each claim has one block. Each block has a `Decision:` line.

<!-- ste:strict -->
1. Open the report.
2. Read the status, the proposal, and the sources of each claim.
3. Put an `x` in one box of each `Decision:` line.
4. For `edit`, write the new text after `edit:`.
5. Make a decision for the Placement block.
6. Save the report.
<!-- /ste:strict -->

Status marks:

| Mark | Meaning |
|---|---|
| ✅ | Correct and current. |
| ⚠️ | Outdated, or not best practice, or the skill knows a better approach. |
| ❌ | Incorrect. |
| ❓ | Unverified. The block gives the reason. |

## Run phase 2: apply

Ask the agent: "Run kb-ingest phase 2 for `inbox/<slug>.review.md`."

The skill writes the notes, runs `make check`, and moves the input to `inbox/archive/`.
The skill does not commit. Read the diff, then commit.

## Note format

Copy `templates/note.md`. Obey these rules:

- `topics[0]` is the primary topic. Put the file in `topics/<topics[0]>/`.
- Write the file name in English `kebab-case`, for example `tool-schema-cost.md`.
- Set `confidence` to `high`, `medium`, or `low`.
- If you keep an unverified claim, write `(unverified)` in the same sentence. Set `confidence` to `low`.
- Only the owner writes the `My takeaways` section.
- In `Related`, use relative links to other notes.
- In `Sources`, list each source and what the note takes from it.

## Writing rules

All text is in English and follows ASD-STE100 principles.

- Normal text uses STE-flavored mode. Errors: semicolons, sentences of more than 25 words, soft phrasal verbs, marketing adjectives, and nominalization.
- Passive voice, compound tenses, and synonyms for one action give warnings only.
- Put steps, checklists, and prompt templates between Strict markers. In a Strict block, the sentence limit is 20 words and all findings are errors.
- Write each sentence on one line. The linter counts words on each line.
- Put verbatim quotes from sources in blockquotes (`>`). Start each quote line with `>`. The linter ignores blockquotes.

Strict markers:

```markdown
<!-- ste:strict -->
1. Open the file.
2. Read line 3.
<!-- /ste:strict -->
```

## Diagrams

- Use a fenced `mermaid` block by default.
- Use Archify only for a complex diagram and only after the owner accepts the diagram proposal.
- Archify cannot write a static SVG from the command line. Thus a note with an Archify diagram also contains a short Mermaid diagram. The note links to the Archify HTML file in `assets/`.

## Checks

Run `make check` before each commit. It runs these steps:

1. `tools/ste_check.py` on the Markdown files.
2. `tools/check_notes.py`.
3. `tools/build_index.py --check`. If it fails, run `make index`.
4. The unit tests in `tools/tests/`.

## Vendored linter

`tools/ste-lint.py` is a copy of `scripts/ste-lint.py` from `danyuchn/asd-ste100-skill` at commit `7d4a135a199a5d7447c4886bcd7ffe742a627bc9`.
Do not change this file. `tools/LICENSE.ste-lint` contains its MIT license.
To update the linter, copy the file from a new commit, update the commit here, and run `make check`.
````

- [ ] **Step 6: Write the `Makefile`**

Use tab characters for the recipe lines.

```make
PYTHON ?= python3
TOPICS := $(notdir $(wildcard topics/*))

.PHONY: check lint notes index-check test index export-md

check: lint notes index-check test

lint:
	$(PYTHON) tools/ste_check.py

notes:
	$(PYTHON) tools/check_notes.py

index-check:
	$(PYTHON) tools/build_index.py --check

test:
	$(PYTHON) -m unittest discover -s tools/tests -t tools

index:
	$(PYTHON) tools/build_index.py

export-md:
	for topic in $(TOPICS) all; do $(PYTHON) tools/export.py --format md --topic $$topic || exit 1; done
```

- [ ] **Step 7: Make sure the index check fails before the first build**

Run: `make index-check`
Expected: FAIL. Five lines `error: ... the generated index is not current. Run 'make index'.` and `build_index --check: 5 files, 5 not current`.

- [ ] **Step 8: Build the index and run all checks**

Run: `make index && make check`
Expected:

```
ste_check: 8 files, 0 errors, 0 warnings
check_notes: 0 notes, 0 errors
build_index --check: 5 files, 0 not current
Ran 35 tests
OK
```

The root README now lists each topic with `Notes: 0.` Each topic README shows `No notes yet.`

If `ste_check` reports an error in your text, rewrite the sentence with the `asd-ste100` skill rules. Do not change the tools.

- [ ] **Step 9: Make sure the linter checks the docs**

```bash
cp README.md /tmp/README.md.bak
printf '\nThe file is removed; the agent stops.\n' >> README.md
make lint; echo "exit=$?"
cp /tmp/README.md.bak README.md
```

Expected: one `error: semicolon` line for `README.md` and `exit=2` (Make reports the failed recipe). After the restore, `make check` passes again.

- [ ] **Step 10: Smoke-test the Markdown export target**

Run: `make export-md && ls dist`
Expected: `all.md context-and-memory.md mcp.md tokens-and-cost.md tool-calling.md`. Each file contains `No notes for this topic.` `git status --short` does not show `dist/`.

- [ ] **Step 11: Commit**

```bash
git add Makefile README.md CONTRIBUTING.md templates topics inbox
git commit -m "feat: add repository layout, docs, templates, and make check"
```

---

### Task 7: The `kb-ingest` skill

**Files:**
- Create: `.claude/skills/kb-ingest/SKILL.md`

**Interfaces:**
- Consumes: `templates/review.md` and `templates/note.md` (Task 6). `make index` and `make check` (Task 6). The topic README form with a `Scope: ` line (Task 4 and Task 6). The Archify command and output files from "Resolved Open Items".
- Produces: the review report format and the phase 2 behavior. Task 9 tests them with the owner.

The skill has no unit tests (spec section 11). Task 9 is its acceptance test.

- [ ] **Step 1: Write `.claude/skills/kb-ingest/SKILL.md`**

````markdown
---
name: kb-ingest
description: Turns inputs in inbox/ into verified notes in topics/. Phase 1 writes a review report. Phase 2 applies the decisions of the owner. Use only when the owner asks for kb-ingest phase 1 or phase 2.
---

# kb-ingest

This skill has two phases. Start a phase only when the owner asks for it.

- Phase 1 reads inputs and writes review reports. It does not change notes.
- Phase 2 reads one review report and writes notes.

## Rules for both phases

<!-- ste:strict -->
- Do not commit. Do not push.
- Do not write the `My takeaways` section of a note.
- Do not use model training knowledge as proof of a claim.
- Write all text in English.
- Write all text with the rules of the `asd-ste100` skill.
- Do not change the opinion of the owner.
<!-- /ste:strict -->

## Phase 1: ingest

### Inputs

| Input | Location |
|---|---|
| URL | Each line in `inbox/links.md` that starts with `http://` or `https://`. Text after ` #` is a comment. |
| Document | `inbox/*.pdf`, `inbox/*.md`, `inbox/*.txt`. Ignore `inbox/*.review.md`. |
| Owner insight | `inbox/notes/*.md`. Each claim from this input has `Kind: experience`. |

The slug of a file input is its file name without the extension, in `kebab-case`.
The slug of a URL is the last part of the URL path, in `kebab-case`. If the path is empty, use the host name.

### Procedure

<!-- ste:strict -->
1. Make a list of the inputs.
2. Remove each input that has a report in `inbox/` from the list.
3. Search `inbox/archive/` for each URL. If you find the URL, remove the input from the list. Tell the owner about the skip.
4. Read each input. For a URL, get the page text. For a PDF, get the text of the file.
5. If you cannot get the text, write an `extract failed` block in the report. Give the reason. Keep the input in `inbox/`.
6. Divide the text into atomic claims. An atomic claim states one fact or one recommendation.
7. For each claim, keep a short verbatim quote from the input. Use 25 words or fewer.
8. Search `topics/` for a note on the same subject. If a note exists, propose an update to that note.
9. Verify each claim against the four criteria in the next section.
10. Write the report `inbox/<slug>.review.md` from `templates/review.md`.
11. Tell the owner the path of each report and the number of claims for each status.
12. Stop. Do not start phase 2.
<!-- /ste:strict -->

### Verification

Use these four criteria for each claim:

| Criterion | Question |
|---|---|
| Correctness | Is the claim correct, incorrect, or unverified? |
| Freshness | Does the claim agree with the current version of the API, model, or tool? |
| Best practice | Does the claim agree with the current recommended practice? |
| Optimisation | Is a simpler, cheaper, or safer approach available? |

Use these sources:

<!-- ste:strict -->
1. For a claim about a library or an SDK, use Context7.
2. Run `npx ctx7@latest library <name> "<question>"` to find the library ID.
3. Run `npx ctx7@latest docs <library-id> "<question>"` to get the documentation.
4. For a conceptual claim, use web search.
5. Use only official sources: vendor documentation, changelogs, papers, and vendor engineering blogs.
6. If you cannot verify a claim, set the status to unverified. Write the reason.
7. For a claim with `Kind: experience`, verify only the factual parts. Propose corrections to the facts only.
<!-- /ste:strict -->

### Report format

Use one block for each claim:

```markdown
### C3: "Claude context window is 100k tokens"
Kind: source
Status: ⚠️ outdated
Proposal: Replace with the current limit for each model. Cite the model page.
Sources: <url> (checked 2026-10-04)
Decision: [ ] accept  [ ] reject  [ ] edit: ...
```

Status values:

| Status line | Meaning |
|---|---|
| `✅ correct` | The claim is correct and current. |
| `⚠️ outdated` | The claim is not current. |
| `⚠️ not best practice` | A better recommended practice exists. |
| `⚠️ can be optimised` | A simpler, cheaper, or safer approach exists. |
| `❌ incorrect` | The claim is incorrect. |
| `❓ unverified` | No official source confirms the claim. The block gives the reason. |

For an input that you cannot read, use this block:

```markdown
### extract failed: <input>
Reason: <paywall, dead link, scanned PDF, or other reason>
Next step: Paste the text into a .md file in inbox/ and run phase 1 again.
```

The report has one Placement block. The Placement block contains these items:

- the primary topic and the secondary topics,
- each proposed new topic, with a one-line scope,
- each proposal to divide the input into more than one note,
- each proposed diagram, with the tool: Mermaid or Archify.

Propose Archify only for a complex diagram, for example an architecture or a long sequence.

## Phase 2: apply

The owner gives the path of one report.

### Decisions

A decision is valid when exactly one box in the `Decision:` line has an `x`.

| Decision | Result |
|---|---|
| accept on a ✅ claim | Keep the claim. |
| accept on a ⚠️ or ❌ claim | Apply the proposal. |
| accept on a ❓ claim | Keep the claim. Add `(unverified)` in the same sentence. Set `confidence: low`. |
| reject | Drop the claim. |
| edit | Use the text of the owner. |

### Procedure

<!-- ste:strict -->
1. Read the report.
2. Find each block that has no valid decision.
3. If you find one or more of these blocks, list them. Then stop.
4. If the owner rejects the Placement block, stop. Ask the owner for the placement.
5. For each accepted new topic, make the folder `topics/<topic>/`.
6. Copy `README.md` from an existing topic folder into the new folder. Write the new name and scope.
7. Write each new note from `templates/note.md`.
8. Update each existing note that the report names.
9. Put each claim with `Kind: experience` in the `Details` section. Keep the words of the owner.
10. Leave the `My takeaways` section empty for the owner.
11. Put procedures, checklists, and prompt templates between Strict markers.
12. Put verbatim quotes from sources in blockquotes.
13. Add each source to `sources` in the frontmatter and to the `Sources` section.
14. Set `verified_at` and `last_reviewed` to the date of today.
15. Set `confidence` to `low` if the note contains `(unverified)`.
16. Make each accepted diagram. Use the next section.
17. Add links in `Related` between the new note and the notes on the same subject.
18. Run `make index`.
19. Run `make check`.
20. If `make check` shows an error, correct the error. Run `make check` again.
21. Make a maximum of two correction attempts. Then tell the owner about each error that remains.
22. Move the input and its report to `inbox/archive/<YYYY-MM-DD>-<slug>/`.
23. For a URL input, remove the line from `inbox/links.md`.
24. Tell the owner which files changed. Do not commit.
<!-- /ste:strict -->

### Diagrams

Mermaid is the default. Put the diagram in a fenced `mermaid` block in the note.

For an accepted Archify diagram, do these steps:

<!-- ste:strict -->
1. Read the `archify` skill.
2. Write the diagram source to `topics/<topic>/assets/<name>.json`.
3. Set `meta.output` in the source to `topics/<topic>/assets/<name>.html`.
4. Run this command from the repository root.
5. Do not keep other files from Archify in `topics/`.
6. Add a link to the HTML file in the note.
7. Add a short Mermaid diagram of the same subject to the note.
<!-- /ste:strict -->

```bash
node ~/.agents/skills/archify/bin/archify.mjs finalize <type> topics/<topic>/assets/<name>.json topics/<topic>/assets/<name>.html --quality showcase --out-dir .archify/<name> --json
```

Archify cannot write a static SVG from the command line. The short Mermaid diagram gives exports a static diagram.
````

- [ ] **Step 2: Lint the skill**

Run: `python3 tools/ste_check.py .claude/skills/kb-ingest/SKILL.md`
Expected: `ste_check: 1 files, 0 errors, 0 warnings`.

- [ ] **Step 3: Make sure Strict mode applies in the skill**

```bash
python3 - <<'EOF'
import sys
sys.path.insert(0, "tools")
from ste_check import check_text
text = open(".claude/skills/kb-ingest/SKILL.md").read().replace("Do not commit. Do not push.", "The files are committed by the skill.")
print([f.format() for f in check_text(text, "SKILL.md")])
EOF
```

Expected: one `error: passive-voice` finding at line 16. The file on disk does not change.

- [ ] **Step 4: Run all checks**

Run: `make check`
Expected: `ste_check: 9 files, 0 errors, 0 warnings` and all other steps pass.

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/kb-ingest/SKILL.md
git commit -m "feat: add kb-ingest skill"
```

---

### Task 8: CI and release workflows

**Files:**
- Create: `.github/workflows/check.yml`
- Create: `.github/workflows/release.yml`

**Interfaces:**
- Consumes: `make check` and `make export-md` (Task 6).
- Produces: a `check` run on each push and pull request, and a `release` workflow. Task 9 starts the release workflow.

- [ ] **Step 1: Write `.github/workflows/check.yml`**

```yaml
name: check

on:
  push:
  pull_request:

permissions:
  contents: read

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.10"
      - run: make check
```

- [ ] **Step 2: Write `.github/workflows/release.yml`**

```yaml
name: release

on:
  push:
    tags: ["v*"]
  workflow_dispatch:
    inputs:
      tag:
        description: "Release tag, for example v0.1.0"
        required: true

permissions:
  contents: write

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.10"
      - run: make check
      - run: make export-md
      - name: Create the release
        env:
          GH_TOKEN: ${{ github.token }}
          TAG: ${{ github.event_name == 'workflow_dispatch' && inputs.tag || github.ref_name }}
        run: >-
          gh release create "$TAG" dist/*.md
          --target "$GITHUB_SHA"
          --title "$TAG"
          --notes "Markdown exports for each topic and for all topics."
```

- [ ] **Step 3: Lint the workflows**

Run: `actionlint .github/workflows/check.yml .github/workflows/release.yml`
Expected: no output and exit 0.

- [ ] **Step 4: Commit and push**

```bash
git add .github/workflows
git commit -m "ci: add check and release workflows"
git push origin main
```

If the push fails with an authentication error, stop and tell the owner. Do not change the active `gh` account.

- [ ] **Step 5: Make sure CI passes**

```bash
export GH_TOKEN=$(gh auth token -u ltlongtma)
gh run list --repo ltlongtma/ai-engineering-notes --workflow check.yml --limit 1
gh run watch --repo ltlongtma/ai-engineering-notes --exit-status "$(gh run list --repo ltlongtma/ai-engineering-notes --workflow check.yml --limit 1 --json databaseId --jq '.[0].databaseId')"
```

Expected: the run for the last commit ends with `completed success`. This is spec acceptance criterion 2.

---

### Task 9: Acceptance run with the owner

This task needs the owner. The owner supplies one URL and one insight note, and the owner records the decisions. Start each phase in a new agent session that has the repository as its working directory, so that the agent loads the project skill.

**Files:**
- Modify: `inbox/links.md`. Create: `inbox/notes/<owner-slug>.md`.
- The skill creates the reports, the notes, and the archive folders.

**Interfaces:**
- Consumes: everything from Tasks 1 to 8.
- Produces: the first real notes, and evidence for spec acceptance criteria 3 to 7.

- [ ] **Step 1: Owner: add the inputs**

Add one URL line to `inbox/links.md`. Write one insight file in `inbox/notes/`. Choose a URL about an AI engineering subject in one of the four topics, so that the run can propose a secondary topic.

- [ ] **Step 2: Run phase 1**

Ask the agent: "Run kb-ingest phase 1."
Expected (acceptance criterion 3):
- `inbox/<url-slug>.review.md` and `inbox/<note-slug>.review.md` exist.
- Each report has one or more `### C<n>:` blocks with `Kind:`, `Status:`, `Proposal:`, `Sources:`, and `Decision:` lines.
- Each report has one `## Placement` block with a `Decision:` line.
- Claims from the insight file have `Kind: experience`.
- No file in `topics/` changed: `git status --short topics` shows nothing.

- [ ] **Step 3: Owner: record all decisions except one**

In one report, record a decision in each block except one claim block.

- [ ] **Step 4: Make sure phase 2 stops on a missing decision**

Ask the agent: "Run kb-ingest phase 2 for `inbox/<slug>.review.md`."
Expected (acceptance criterion 5): the agent lists the block without a decision and stops. `git status --short topics` shows nothing.

- [ ] **Step 5: Owner: record the last decision, then run phase 2 for both reports**

Ask the agent to run phase 2 for each report.
Expected (acceptance criterion 4):
- New or updated notes in `topics/`.
- `make check` passes.
- The topic READMEs and the root README list the new notes.
- The inputs and reports are in `inbox/archive/<YYYY-MM-DD>-<slug>/`.
- The URL line is no longer in `inbox/links.md`.
- `git log -1` shows no new commit from the agent.

- [ ] **Step 6: Make sure topic exports include cross-listed notes**

If a new note has a secondary topic, run `python3 tools/export.py --format md --topic <secondary>`. Make sure the note is in `dist/<secondary>.md`.
If no new note has a secondary topic, run `python3 tools/export.py --format md --topic tool-calling --root tools/tests/fixtures/kb`. Make sure `tools/tests/fixtures/kb/dist/tool-calling.md` contains `## Design MCP tool schemas for low token cost`. Then remove `tools/tests/fixtures/kb/dist/`.
Expected: acceptance criterion 6.

- [ ] **Step 7: Run the local MDX and PDF exports**

```bash
python3 tools/export.py --format mdx --topic all
python3 tools/export.py --format pdf --topic all
ls -la dist/all.mdx dist/all.pdf
```

Expected (acceptance criterion 7): both files exist and are not empty. Open `dist/all.pdf` and make sure the Mermaid diagrams show as images.

- [ ] **Step 8: Owner: commit and push the notes**

The owner reads the diff, commits, and pushes. Then check CI as in Task 8 Step 5.

- [ ] **Step 9: Owner decision: publish the first release**

Ask the owner for approval and a tag name, for example `v0.1.0`. After approval, run:

```bash
GH_TOKEN=$(gh auth token -u ltlongtma) gh workflow run release.yml --repo ltlongtma/ai-engineering-notes -f tag=v0.1.0
```

Expected: the release `v0.1.0` exists with one `.md` file for each topic and `all.md`.

---

## Spec Coverage

| Spec section | Task |
|---|---|
| 2 Decisions, 3 Layout | 1, 6, 7, 8 |
| 4 Ingest workflow, 4.5 Extraction errors | 7, 9 |
| 5 Note format and checks | 3, 6 (template) |
| 6 Writing standard | 2, 6, 7 |
| 7 Diagrams | Resolved Open Items, 6 (CONTRIBUTING), 7 (skill) |
| 8 Index generation | 4, 6 |
| 9 Exports | 5, 6 (`export-md`), 9 |
| 10 Checks and CI | 6 (`make check`), 8 |
| 11 Tests | 1 to 5 |
| 12 Vendored linter | 1, 6 (CONTRIBUTING) |
| 13 Acceptance criteria | 1: 6 to 8. 2: 8. 3 to 7: 9. |
