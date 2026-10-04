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
| Tool | A URL line in `inbox/links.md` with a `# tool: <verdict>` comment. Read the "Tool inputs" section. |

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

### Tool inputs

A tool input is a line in `inbox/links.md` with a `# tool:` comment, for example:

```text
https://github.com/BurntSushi/ripgrep # tool: Faster than grep, and it skips gitignored files by default.
```

The text after `# tool:` is the verdict of the owner.

<!-- ste:strict -->
1. Write one claim block for the tool. Use the verdict as the quote. Write `Kind: experience`.
2. Verify only the name, the type, the link, and the purpose of the tool.
3. Do not verify the verdict. Do not change its words.
4. In the `Proposal:` line, write the entry fields: `Type`, `Link`, `Use for`, and `Status`.
5. Use the words of the verdict to select the status: `using`, `tried`, or `dropped`.
6. If the verdict does not show the status, propose `using`. Write "The verdict does not show the status" in the proposal.
7. Search `topics/tools/` for the link. If an entry has the link, propose an update to that entry.
8. In the Placement block, write `Primary topic: tools`. Write the category file in the `Notes:` line.
9. If no category file agrees with the type of the tool, propose a new category file.
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
- for each proposed new topic, the overview update: the layer, the table row, and the place in the Mermaid map,
- for a tool input, the category file in `topics/tools/`,
- each proposal to divide the input into more than one note,
- each proposed diagram, with the tool: Mermaid or Archify.

The `Overview:` line of the Placement block holds the overview update, or `none`.

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
7. For each accepted new topic, add the accepted row to the topic table in `OVERVIEW.md`.
8. Add the new topic to the Mermaid map in `OVERVIEW.md`, in the accepted layer. Do not change other text in `OVERVIEW.md`.
9. Write each new note from `templates/note.md`.
10. Write each new tool category file from `templates/tools.md`.
11. Update each existing note and each tool entry that the report names.
12. Put each claim with `Kind: experience` in the `Details` section. Keep the words of the owner.
13. For a tool input, write one `###` entry in the `Tools` section of the category file.
14. Write the verdict of the owner in the `My verdict:` line. Do not change its words.
15. Leave the `My takeaways` section empty for the owner.
16. Put procedures, checklists, and prompt templates between Strict markers.
17. Put verbatim quotes from sources in blockquotes.
18. Add each source to `sources` in the frontmatter and to the `Sources` section. For a tool, the source is the link of the tool.
19. Set `verified_at` and `last_reviewed` to the date of today.
20. Set `confidence` to `low` if the note contains `(unverified)`.
21. Make each accepted diagram. Use the next section.
22. Add links in `Related` between the new note and the notes on the same subject.
23. Run `make index`.
24. Run `make check`.
25. If `make check` shows an error, correct the error. Run `make check` again.
26. Make a maximum of two correction attempts. Then tell the owner about each error that remains.
27. Move the input and its report to `inbox/archive/<YYYY-MM-DD>-<slug>/`.
28. For a URL input, remove the line from `inbox/links.md`.
29. Tell the owner which files changed. Do not commit.
30. If you added a topic to `OVERVIEW.md`, tell the owner to update `assets/overview.json` and the HTML file.
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
