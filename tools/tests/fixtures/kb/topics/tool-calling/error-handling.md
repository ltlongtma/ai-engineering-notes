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
