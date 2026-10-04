# AI engineering notes

This repository is a personal notebook of AI engineering knowledge and experience.

- Goal 1: Keep knowledge so that the owner can read it again later.
- Goal 2: Share selected parts with other teams.

[OVERVIEW.md](OVERVIEW.md) shows the place of each topic in a map of an agentic AI system.

## How it works

1. The owner puts raw inputs in `inbox/`.
2. The `kb-ingest` skill extracts claims, verifies them, and writes a review report.
3. The owner records a decision for each claim in the report.
4. The skill writes or updates notes in `topics/`, then runs `make check`.
5. The owner reads the diff and commits.

`CONTRIBUTING.md` gives the full steps, the note template, and the writing rules.

## Website

The `pages` workflow publishes a website to GitHub Pages after each push to `main`.
The home page shows the overview map and one card for each topic, grouped by layer.
When the content of a card is short, a click opens the content in a modal.
When the content is long, a click opens a separate page.
Each topic and each note also has its own page.

To use the website, set the Pages source to "GitHub Actions" in the repository settings one time.

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
| `make site` | Writes the website to `dist/site/`. Open `dist/site/index.html` through a local HTTP server. |

## Topics

The tool `tools/build_index.py` writes this list. Do not edit it.

<!-- index:start -->
- [context-and-memory](topics/context-and-memory/README.md): Context windows, short-term and long-term memory, compaction, retrieval for agents. Notes: 2.
- [evals-and-observability](topics/evals-and-observability/README.md): Evaluation of agent output, traces, metrics, cost tracking. Notes: 0.
- [guardrails](topics/guardrails/README.md): Permissions, input and output checks, sandboxes, prompt injection. Notes: 0.
- [human-in-the-loop](topics/human-in-the-loop/README.md): Approval points, review steps, handoff between the agent and a person. Notes: 0.
- [mcp](topics/mcp/README.md): MCP servers, clients, transports, and security. Notes: 0.
- [tokens-and-cost](topics/tokens-and-cost/README.md): Token counting, prompt caching, model choice by cost. Notes: 2.
- [tool-calling](topics/tool-calling/README.md): Tool design, schemas, error handling. Notes: 0.
- [tools](topics/tools/README.md): Skills, plugins, MCP servers, and CLI tools that the owner uses, with the opinion of the owner. Notes: 2.
- [workflows](topics/workflows/README.md): Agent loops, planning, multi-agent patterns, long-running tasks. Notes: 0.
<!-- index:end -->
