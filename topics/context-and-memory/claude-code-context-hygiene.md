---
title: Keep the Claude Code context small
topics: [context-and-memory, tokens-and-cost]
sources:
  - url: https://www.youtube.com/watch?v=eAlXDUUDAx8
    accessed: 2026-10-04
  - url: https://code.claude.com/docs/en/costs
    accessed: 2026-10-04
  - url: https://code.claude.com/docs/en/sub-agents
    accessed: 2026-10-04
verified_at: 2026-10-04
confidence: high
last_reviewed: 2026-10-04
---

## Summary

Each turn sends the full context again, so each unnecessary token costs money in each turn. Keep CLAUDE.md short, load instructions only when necessary, filter command output, and start a new context for an unrelated task.

## Details

### CLAUDE.md and skills

> just don't keep anything in here that doesn't serve every task ... Those things usually you want to move to skills

CLAUDE.md loads at the start of each session. A skill loads only its name and description. It loads its full instructions only when Claude uses it.

### MCP servers

Claude Code defers MCP tool definitions by default. Only the tool names and the server instructions go into the context until Claude uses a tool. Use `/mcp` to disable a server that the session does not use. Use a CLI tool such as `gh` when it is available, because it adds no tool listing.

### Command output

Change the command so that it shows only the failed lines. Write that command in CLAUDE.md. A PreToolUse hook can also filter the test output to show only the failures, for each run.

### Subagents

> it does all the reading and all the tool calls over there and it only sends you the final conclusion back

A subagent also uses tokens. Use a smaller model for a subagent to decrease the cost.

### One task in each context

> the bottom session uses twice the amount of tokens as a top session

Use `/clear` between unrelated tasks. Use `/rename` before `/clear`, and use `/resume` to go back to the session.

<!-- ste:strict -->
1. Before a new task, use `/rename`.
2. Use `/clear`.
3. To go back to the earlier task, use `/resume`.
<!-- /ste:strict -->

## My takeaways

## Related

- [Claude Code cost depends on the prompt cache, the model, and the effort](../tokens-and-cost/claude-code-prompt-cache-cost.md)

## Sources

- Under30: Không hiểu cơ chế token, bạn còn bị Claude Code bào tiền. https://www.youtube.com/watch?v=eAlXDUUDAx8
- Claude Code: manage costs. https://code.claude.com/docs/en/costs
- Claude Code: subagents. https://code.claude.com/docs/en/sub-agents
