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
