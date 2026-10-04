#!/usr/bin/env python3
"""Build the static site for GitHub Pages in dist/site/.

The home page shows the overview map and one card for each topic, grouped by layer.
A card with short content (MODAL_MAX_CHARS or less of Markdown) opens the content in a modal.
A card with long content opens the page of that content.
Each topic and each note also has its own page, so that each link works without the modal.
The browser renders the Markdown. The build uses the standard library only.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

from build_index import notes_for
from export import EXTERNAL, HEADING, LINK, MERMAID_VERSION, map_lines_outside_code, map_prose, mermaid_to_html
from notelib import REPO_ROOT, FrontmatterError, Note, load_notes, topic_names

MODAL_MAX_CHARS = 2000
MARKED_VERSION = "18.0.14"
MARKED_URL = f"https://cdn.jsdelivr.net/npm/marked@{MARKED_VERSION}/lib/marked.esm.js"
MERMAID_URL = f"https://cdn.jsdelivr.net/npm/mermaid@{MERMAID_VERSION}/dist/mermaid.esm.min.mjs"
SITE_TITLE = "AI engineering notes"
SITE_INTRO = "Notes about AI engineering, grouped by the layers of an agentic AI system."
STATIC_DIR = Path(__file__).with_name("site")
OVERVIEW = "OVERVIEW.md"
MAP_SOURCE = "assets/overview.html"
MAP_PAGE = "map.html"
OTHER_LAYER = "Other"
# A row of the OVERVIEW.md topic table: | Layer | [topic](topics/<topic>/README.md) | Scope |
TOPIC_ROW = re.compile(r"^\|\s*([^|]+?)\s*\|\s*\[[^\]]*\]\(topics/([^/)\s]+)/README\.md\)\s*\|\s*([^|]*?)\s*\|\s*$")
LAYER_LINE = re.compile(r"^- ([^:]+): (.+)$")
MARKDOWN_LINK_TEXT = re.compile(r"!?\[([^\]]*)\]\([^)]*\)")


class SiteError(Exception):
    """The site cannot build. The message tells the user what to do."""


@dataclass(frozen=True)
class Topic:
    name: str
    layer: str
    scope: str
    notes: tuple[Note, ...]


def read_overview(root: Path) -> tuple[dict[str, str], list[tuple[str, str, str]]]:
    """Return the layer descriptions and the (layer, topic, scope) rows of OVERVIEW.md, in file order."""
    path = root / OVERVIEW
    if not path.is_file():
        return {}, []
    layers: dict[str, str] = {}
    rows: list[tuple[str, str, str]] = []
    section = None
    for line in path.read_text(encoding="utf-8").split("\n"):
        if line.startswith("## "):
            section = line[3:].strip()
            continue
        layer = LAYER_LINE.match(line)
        if section == "Layers" and layer:
            layers[layer.group(1).strip()] = layer.group(2).strip()
        row = TOPIC_ROW.match(line)
        if row:
            rows.append(row.groups())
    return layers, rows


def load_topics(root: Path, notes: list[Note]) -> list[Topic]:
    """Return the topics in the order of the OVERVIEW.md table. A topic without a row goes to the Other layer."""
    _, rows = read_overview(root)
    names = set(topic_names(root))
    listed = [(layer, name, scope) for layer, name, scope in rows if name in names]
    seen = {name for _, name, _ in listed}
    listed += [(OTHER_LAYER, name, "") for name in sorted(names - seen)]
    return [Topic(name, layer, scope, tuple(notes_for(name, notes))) for layer, name, scope in listed]


def topic_url(name: str) -> str:
    return f"topics/{name}.html"


def note_url(note: Note) -> str:
    return f"notes/{note.folder}/{note.slug}.html"


def site_urls(notes: list[Note], topics: list[Topic]) -> dict[str, str]:
    """Map each repository Markdown file that has a site page to the URL of that page."""
    urls = {"README.md": "index.html", OVERVIEW: "index.html"}
    urls.update({f"topics/{topic.name}/README.md": topic_url(topic.name) for topic in topics})
    urls.update({note.rel: note_url(note) for note in notes})
    return urls


def site_markdown(note: Note, root: Path, urls: dict[str, str], copies: set[str]) -> str:
    """Return the note body with links that work on the site.

    A link to a page of the site points to that page. A link to another repository file
    (for example an image) points to a copy of the file; the path goes into `copies`.
    A link to a Markdown file without a site page becomes text.
    """
    def replace(match: re.Match) -> str:
        bang, text, target = match.groups()
        if EXTERNAL.match(target):
            return match.group(0)
        path, _, fragment = target.partition("#")
        suffix = f"#{fragment}" if fragment else ""
        if not path:
            return f"{bang}[{text}]({urls[note.rel]}{suffix})"
        resolved = (note.path.parent / path).resolve()
        try:
            rel = resolved.relative_to(root.resolve()).as_posix()
        except ValueError:
            return text
        if rel in urls:
            return f"{bang}[{text}]({urls[rel]}{suffix})"
        if resolved.is_file() and resolved.suffix != ".md":
            copies.add(rel)
            return f"{bang}[{text}]({rel}{suffix})"
        return text

    return mermaid_to_html(map_prose(note.body, lambda prose: LINK.sub(replace, prose)).strip("\n"))


def fits_modal(markdown: str) -> bool:
    return len(markdown) <= MODAL_MAX_CHARS


def topic_markdown(topic: Topic, bodies: dict[str, str]) -> str:
    """Return the full content of a topic: the scope, then each note with its headings one level down."""
    parts = [topic.scope] if topic.scope else []
    if not topic.notes:
        parts.append("No notes yet.")
    for note in topic.notes:
        body = map_lines_outside_code(bodies[note.rel], lambda line: HEADING.sub(r"#\1 ", line))
        parts.append(f"## [{note.title}]({note_url(note)})\n\n{body}")
    return "\n\n".join(parts)


def note_summary(note: Note) -> str:
    """Return the first paragraph of the Summary section as plain text."""
    lines: list[str] = []
    inside = False
    for line in note.body.split("\n"):
        if line.startswith("#"):
            if inside and lines:
                break
            inside = line.strip() == "## Summary"
            continue
        if not inside:
            continue
        if line.strip():
            lines.append(line.strip())
        elif lines:
            break
    return MARKDOWN_LINK_TEXT.sub(r"\1", " ".join(lines)).replace("`", "")


def note_facts(note: Note) -> str:
    meta = note.meta
    facts = [f"Confidence: {meta['confidence']}" if meta.get("confidence") else "",
             f"Verified: {meta['verified_at']}" if meta.get("verified_at") else "",
             f"Reviewed: {meta['last_reviewed']}" if meta.get("last_reviewed") else ""]
    return " · ".join(fact for fact in facts if fact)


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def plural(count: int, word: str) -> str:
    return f"{count} {word}" if count == 1 else f"{count} {word}s"


def card(href: str, title: str, text: str, foot: str, modal_key: str | None) -> str:
    attribute = f' data-modal="{html.escape(modal_key)}"' if modal_key else ""
    mode = "Quick view" if modal_key else "Open page →"
    return (f'<a class="card" href="{html.escape(href)}"{attribute}>'
            f'<span class="card-title">{html.escape(title)}</span>'
            f'<span class="card-text">{html.escape(text)}</span>'
            f'<span class="card-foot"><span>{html.escape(foot)}</span>'
            f'<span class="card-mode">{mode}</span></span></a>')


DIALOG = """<dialog id="modal" aria-labelledby="modal-title">
  <div class="modal-inner">
    <header class="modal-head">
      <h2 id="modal-title"></h2>
      <a id="modal-page" href="index.html">Open as page</a>
      <button type="button" id="modal-close" aria-label="Close">×</button>
    </header>
    <p class="meta" id="modal-meta"></p>
    <div class="md" id="modal-body"></div>
  </div>
</dialog>"""


def page(prefix: str, title: str, body: str, store: dict[str, dict]) -> str:
    """Return one HTML page. All URLs in the page are relative to the site root through <base>."""
    data = json.dumps(store, ensure_ascii=False).replace("<", "\\u003c")
    full_title = SITE_TITLE if title == SITE_TITLE else f"{title} · {SITE_TITLE}"
    return f"""<!doctype html>
<html lang="en" data-marked="{MARKED_URL}" data-mermaid="{MERMAID_URL}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<base href="{prefix}">
<title>{html.escape(full_title)}</title>
<link rel="stylesheet" href="assets/site.css">
<script type="module" src="assets/site.js"></script>
</head>
<body>
<header class="site-header"><a class="brand" href="index.html">{SITE_TITLE}</a><nav><a href="index.html#layers">Topics</a><a href="{MAP_PAGE}">Map</a></nav></header>
<main>
{body}
</main>
{DIALOG}
<script type="application/json" id="store">{data}</script>
</body>
</html>
"""


def entry(title: str, meta: str, markdown: str, href: str) -> dict:
    return {"title": title, "meta": meta, "md": markdown, "href": href}


def render_index(topics: list[Topic], layers: dict[str, str], topic_bodies: dict[str, str], has_map: bool) -> str:
    store: dict[str, dict] = {}
    sections: list[str] = []
    order = list(dict.fromkeys(topic.layer for topic in topics))
    for layer in order:
        cards: list[str] = []
        for topic in (t for t in topics if t.layer == layer):
            key = None
            if fits_modal(topic_bodies[topic.name]):
                key = f"topic:{topic.name}"
                store[key] = entry(topic.name, f"{layer} · {plural(len(topic.notes), 'note')}",
                                   topic_bodies[topic.name], topic_url(topic.name))
            cards.append(card(topic_url(topic.name), topic.name, topic.scope,
                              plural(len(topic.notes), "note"), key))
        description = f"<p>{html.escape(layers[layer])}</p>" if layer in layers else ""
        sections.append(f'<section class="layer layer-{slug(layer)}" id="layer-{slug(layer)}"><div class="layer-head">'
                        f'<h2>{html.escape(layer)}</h2>{description}</div>'
                        f'<div class="cards">{"".join(cards)}</div></section>')
    note_count = len({note.rel for topic in topics for note in topic.notes})
    map_section = ("" if not has_map else
                   f'<section class="map"><div class="section-head"><h2>Map of an agentic AI system</h2>'
                   f'<a href="{MAP_PAGE}">Open the full map →</a></div>'
                   f'<iframe src="{MAP_PAGE}" title="Map of an agentic AI system" loading="lazy"></iframe></section>')
    body = (f'<section class="hero"><h1>{SITE_TITLE}</h1><p>{SITE_INTRO}</p>'
            f'<p class="meta">{plural(len(topics), "topic")} · {plural(note_count, "note")}</p></section>'
            f'{map_section}<div id="layers">{"".join(sections)}</div>')
    return page("./", SITE_TITLE, body, store)


def render_topic(topic: Topic, bodies: dict[str, str]) -> str:
    store: dict[str, dict] = {}
    cards: list[str] = []
    for note in topic.notes:
        key = None
        if fits_modal(bodies[note.rel]):
            key = f"note:{note.rel}"
            store[key] = entry(note.title, note_facts(note), bodies[note.rel], note_url(note))
        others = [name for name in note.topics if name != topic.name]
        foot = note_facts(note) + (f" · Also in: {', '.join(others)}" if others else "")
        cards.append(card(note_url(note), note.title, note_summary(note), foot, key))
    notes = f'<div class="cards cards-wide">{"".join(cards)}</div>' if cards else '<p class="empty">No notes yet.</p>'
    scope = f'<p class="lead">{html.escape(topic.scope)}</p>' if topic.scope else ""
    body = (f'<nav class="crumbs"><a href="index.html">Home</a> / '
            f'<a href="index.html#layer-{slug(topic.layer)}">{html.escape(topic.layer)}</a></nav>'
            f'<h1>{html.escape(topic.name)}</h1>{scope}<h2>{plural(len(topic.notes), "note")}</h2>{notes}')
    return page("../", topic.name, body, store)


def render_note(note: Note, markdown: str) -> str:
    store = {"note": entry(note.title, note_facts(note), markdown, note_url(note))}
    topics = " ".join(f'<a class="chip" href="{topic_url(name)}">{html.escape(name)}</a>' for name in note.topics)
    primary = note.topics[0] if note.topics else note.folder
    body = (f'<nav class="crumbs"><a href="index.html">Home</a> / '
            f'<a href="{topic_url(primary)}">{html.escape(primary)}</a></nav>'
            f'<h1>{html.escape(note.title)}</h1><p class="meta">{topics} {html.escape(note_facts(note))}</p>'
            f'<article class="md" data-md="note"></article>')
    return page("../../", note.title, body, store)


def check_out_dir(root: Path, out: Path) -> None:
    if out == root or out in root.parents:
        raise SiteError(f"The output folder {out} contains the repository. Use a folder such as dist/site.")


def build(root: Path, out: Path) -> int:
    """Write the site to `out`. Return the number of pages."""
    root, out = root.resolve(), out.resolve()
    check_out_dir(root, out)
    notes = load_notes(root)
    topics = load_topics(root, notes)
    layers, _ = read_overview(root)
    urls = site_urls(notes, topics)
    copies: set[str] = set()
    bodies = {note.rel: site_markdown(note, root, urls, copies) for note in notes}
    topic_bodies = {topic.name: topic_markdown(topic, bodies) for topic in topics}
    map_source = root / MAP_SOURCE
    pages = {"index.html": render_index(topics, layers, topic_bodies, map_source.is_file())}
    pages.update({topic_url(topic.name): render_topic(topic, bodies) for topic in topics})
    pages.update({note_url(note): render_note(note, bodies[note.rel]) for note in notes})
    if out.exists():
        shutil.rmtree(out)
    for rel, text in pages.items():
        path = out / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    shutil.copytree(STATIC_DIR, out / "assets")
    if map_source.is_file():
        shutil.copyfile(map_source, out / MAP_PAGE)
    for rel in sorted(copies):
        (out / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / rel, out / rel)
    return len(pages)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help="repository root")
    parser.add_argument("--out", type=Path, help="output folder (default: <root>/dist/site)")
    args = parser.parse_args(argv)
    out = args.out or args.root / "dist" / "site"
    try:
        count = build(args.root, out)
    except (SiteError, FrontmatterError) as error:
        print(f"error: {error}")
        return 1
    print(f"wrote {count} pages to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
