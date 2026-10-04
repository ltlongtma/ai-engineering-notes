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
