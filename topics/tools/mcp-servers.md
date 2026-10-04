---
title: MCP servers
topics: [tools]
sources:
  - url: https://github.com/mksglu/context-mode
    accessed: 2026-10-04
  - url: https://github.com/upstash/context7
    accessed: 2026-10-04
verified_at: 2026-10-04
confidence: high
last_reviewed: 2026-10-04
---

## Summary

This file lists the MCP servers that the owner uses, with the opinion of the owner.

## Tools

### context-mode

- Type: MCP server
- Link: https://github.com/mksglu/context-mode
- Use for: Run commands and fetch pages in a sandbox. Keep the output in a search index, and give the agent only the necessary parts.
- Status: using
- My verdict: Keeps large command output and web pages out of the context window.

### Context7

- Type: MCP server
- Link: https://github.com/upstash/context7
- Use for: Give the agent current documentation and code examples for a library.
- Status: using
- My verdict: Gives the agent current library docs, so it does not guess old APIs.

## Related

- [Agent skills](agent-skills.md)
- [Keep the Claude Code context small](../context-and-memory/claude-code-context-hygiene.md)

## Sources

- https://github.com/mksglu/context-mode: the name, the type, the link, and the purpose of context-mode.
- https://github.com/upstash/context7: the name, the type, the link, and the purpose of Context7.
