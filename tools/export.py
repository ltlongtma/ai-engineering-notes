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
# Any indentation: a fence inside a list item is still a fence. The vendored linter also strips indentation.
FENCE = re.compile(r"^\s*(`{3,}|~{3,})")
# A code span opens and closes with backtick runs of the same length.
INLINE_CODE = re.compile(r"(?<!`)(`+)(?!`).+?(?<!`)\1(?!`)")
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
