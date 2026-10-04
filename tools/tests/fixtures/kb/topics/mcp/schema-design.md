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
