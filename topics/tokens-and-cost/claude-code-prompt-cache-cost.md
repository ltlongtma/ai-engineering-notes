---
title: Claude Code cost depends on the prompt cache, the model, and the effort
topics: [tokens-and-cost, context-and-memory]
sources:
  - url: https://www.youtube.com/watch?v=eAlXDUUDAx8
    accessed: 2026-10-04
  - url: https://code.claude.com/docs/en/prompt-caching
    accessed: 2026-10-04
  - url: https://platform.claude.com/docs/en/build-with-claude/prompt-caching
    accessed: 2026-10-04
  - url: https://www.anthropic.com/claude-opus-5-5
    accessed: 2026-10-04
  - url: https://code.claude.com/docs/en/costs
    accessed: 2026-10-04
  - url: https://claude.com/blog/claude-model-and-effort-level-in-claude-code
    accessed: 2026-10-04
verified_at: 2026-10-04
confidence: low
last_reviewed: 2026-10-04
---

## Summary

Each turn sends the full context to the model again. The prompt cache makes the repeated prefix cheap. A change in the prefix, a model switch, or an expired cache makes the model process the full context again at full price.

## Details

### Each turn sends the full context

Each turn sends the system prompt, the tool definitions, CLAUDE.md, the skill and MCP listings, all earlier messages, and the new message. The talk by Lydia Hallie (Anthropic) says:

> this entire bundle goes to the model as one request

### The cache matches the prefix exactly

The model processes again only the part after the first difference from the earlier request.

> only does all the recomputation ... on the point where this request starts to differ from the previous one

The match is exact. A change at one position in the prefix makes the model process all the text after that position again.

```mermaid
flowchart LR
  T1[Turn 1: prefix written to cache] --> T2[Turn 2: prefix read from cache]
  T2 --> T3[Turn 3: prefix read from cache]
  T3 --> X[Change in the prefix]
  X --> T4[Turn 4: full price after the change]
```

### Prices on 2026-10-04

Prices change. Examine the source before you use a value.

| Item | Value |
|---|---|
| Opus 5.5 input | $4 for each million tokens |
| Opus 5.5 output | $20 for each million tokens |
| Cache read, standard | 0.1 x base input |
| Cache read, Opus 5.5 | 0.05 x base input ($0.20 for each million tokens) |
| Cache read, Fable 5.1 | 0.025 x base input |
| Cache write, 5-minute TTL | 1.25 x base input |
| Cache write, 1-hour TTL | 2 x base input |

### Cache lifetime

A Claude subscription within plan usage gets a one-hour TTL for the main conversation. An API key, usage credits, or a cloud provider get a five-minute TTL. Subagents and compaction get five minutes. Each cache hit starts the timer again. The `promptCacheTtl` setting changes the TTL of the main conversation.

> try to compact or change before you step away, not when you come back

The `/rewind` command keeps the cache, because it goes back to a prefix that is in the cache. Use `/rewind` and not `/compact` to remove a failed path.

### Model and effort

> Sonnet is a really good generalist, Opus is the expert, and Fable is the specialist

Sonnet does most coding tasks well and costs less. Use Opus for complex architecture or for reasoning in many steps.

> effort goes along with your request and it just tells the model how thorough it should be

Higher effort gives more thinking and more output tokens. Lower effort for a simple task costs less. To find the correct setting after a bad result, ask this question:

> did it not know enough or did it not try hard enough

If the model did not know enough, use a stronger model. If the result is lazy or incomplete, use more effort. If the model did too much work, use less effort.

A model switch always starts a new cache. A change of effort keeps the cache on Opus 5.5, Sonnet 5.5, and Fable 5.1 with an API key or a Claude subscription. It does not keep the cache on Bedrock, Google Cloud Agent Platform, or a Claude apps gateway. Choose the model and the effort at the start of the session.

### Team cost

> when a team spend is unexpectedly high, this usually traces back to just the biggest model just being left on as a default

The cost docs give two causes: long sessions without `/clear`, and Opus as the default model. Use managed settings to set the defaults for a team. The `/usage` command shows the cache hit line.

### A test by the video author

The video author made a 77-second clip with Claude Code (unverified). Opus used approximately 12 minutes and $8. Sonnet used approximately $3.50. Sonnet with a prepared edit plan used 4 minutes and less than $1. The general lesson agrees with the cost docs: give Claude the plan or the domain knowledge, so that it explores less.

## My takeaways

## Related

- [Keep the Claude Code context small](../context-and-memory/claude-code-context-hygiene.md)

## Sources

- Under30: Không hiểu cơ chế token, bạn còn bị Claude Code bào tiền. https://www.youtube.com/watch?v=eAlXDUUDAx8
- Claude Code: prompt caching. https://code.claude.com/docs/en/prompt-caching
- Claude API: prompt caching and pricing. https://platform.claude.com/docs/en/build-with-claude/prompt-caching
- Anthropic: Claude Opus 5.5. https://www.anthropic.com/claude-opus-5-5
- Claude Code: manage costs. https://code.claude.com/docs/en/costs
- Claude blog: model and effort level in Claude Code. https://claude.com/blog/claude-model-and-effort-level-in-claude-code
