# Review: Under30 video "Không hiểu cơ chế token, bạn còn bị Claude Code bào tiền"

Input: `https://www.youtube.com/watch?v=eAlXDUUDAx8`
Date: 2026-10-04

Write one decision in each `Decision:` line. Put an `x` in one box. For `edit`, write the new text after `edit:`.
Phase 2 stops if one or more `Decision:` lines have no mark.

Extraction: the video has no human captions. The skill used the YouTube auto-generated Vietnamese captions (`yt-dlp --write-auto-subs`). The video is a Vietnamese commentary on an English talk by Lydia Hallie (Anthropic). Quotes in English come from the English clips. Quotes marked "(translated)" come from the Vietnamese commentary.

## Claims

### C1: "this entire bundle goes to the model as one request"
Kind: source
Status: ✅ correct
Proposal: Keep the claim. Each turn re-sends the system prompt, tool definitions, CLAUDE.md, skill and MCP listings, all earlier messages, and the new message.
Sources: https://code.claude.com/docs/en/prompt-caching (checked 2026-10-04)
Decision: [x] accept  [ ] reject  [ ] edit: ...

### C2: "only does all the recomputation ... on the point where this request starts to differ from the previous one"
Kind: source
Status: ✅ correct
Proposal: Keep the claim. Add the rule from the docs: the match is exact, so a change anywhere in the prefix recomputes everything after it.
Sources: https://code.claude.com/docs/en/prompt-caching (checked 2026-10-04)
Decision: [x] accept  [ ] reject  [ ] edit: ...

### C3: "model 5.5 costs 5 dollars per 1 million input tokens and 20 dollars per 1 million output tokens" (translated)
Kind: source
Status: ❌ incorrect
Proposal: Opus 5.5 costs $4 per million input tokens and $20 per million output tokens. $5 input is the Opus 5 price. Give prices with the date, because prices change.
Sources: https://www.anthropic.com/claude-opus-5-5 (checked 2026-10-04)
Decision: [x] accept  [ ] reject  [ ] edit: ...

### C4: "a cache read costs maybe only about 1/10 of a normal input token" (translated)
Kind: source
Status: ⚠️ outdated
Proposal: The standard cache read multiplier is 0.1x base input. Opus 5.5 uses 0.05x ($0.20 per million). Fable 5.1 uses 0.025x. Cache writes cost 1.25x (5-minute TTL) or 2x (1-hour TTL).
Sources: https://platform.claude.com/docs/en/build-with-claude/prompt-caching (checked 2026-10-04), https://www.anthropic.com/claude-opus-5-5 (checked 2026-10-04)
Decision: [x] accept  [ ] reject  [ ] edit: ...

### C5: "Sonnet is a really good generalist, Opus is the expert, and Fable is the specialist"
Kind: source
Status: ✅ correct
Proposal: Keep the claim as guidance from Anthropic. The cost docs say: Sonnet handles most coding tasks well and costs less. Use Opus for complex architecture or multi-step reasoning.
Sources: https://code.claude.com/docs/en/costs (checked 2026-10-04), https://claude.com/blog/claude-model-and-effort-level-in-claude-code (checked 2026-10-04)
Decision: [x] accept  [ ] reject  [ ] edit: ...

### C6: "effort goes along with your request and it just tells the model how thorough it should be"
Kind: source
Status: ✅ correct
Proposal: Keep the claim. Add: lower effort for simple tasks reduces cost, because higher effort gives more thinking and more output tokens.
Sources: https://code.claude.com/docs/en/costs (checked 2026-10-04)
Decision: [x] accept  [ ] reject  [ ] edit: ...

### C7: "did it not know enough or did it not try hard enough"
Kind: source
Status: ✅ correct
Proposal: Keep the claim as a rule of thumb from Lydia Hallie: missing knowledge means a stronger model, a lazy or incomplete result means more effort, too much work means less effort.
Sources: https://claude.com/blog/claude-model-and-effort-level-in-claude-code (checked 2026-10-04)
Decision: [x] accept  [ ] reject  [ ] edit: ...

### C8: "changing effort mid-session also breaks the cache on most models, only Fable 5.1 is the exception" (translated)
Kind: source
Status: ⚠️ outdated
Proposal: A model switch always starts a new cache. A change of effort keeps the cache on Opus 5.5, Sonnet 5.5, and Fable 5.1 with an API key or a Claude subscription. It does not keep the cache on Bedrock, Google Cloud Agent Platform, or a Claude apps gateway. Keep the advice: choose the model and effort at the start of the session.
Sources: https://code.claude.com/docs/en/prompt-caching (checked 2026-10-04)
Decision: [x] accept  [ ] reject  [ ] edit: ...

### C9: "Opus processed the 77-second clip in about 12 minutes for about 8 dollars, Sonnet for about 3.5 dollars, Sonnet with a prepared edit plan in 4 minutes for under 1 dollar" (translated)
Kind: source
Status: ❓ unverified
Proposal: This is a single test by the video author. No official source can confirm it. Keep only the general lesson, which the docs confirm: give Claude the plan or the domain knowledge, so that it explores less.
Sources: https://code.claude.com/docs/en/costs (checked 2026-10-04). Reason: a personal measurement with no published data.
Decision: [x] accept  [ ] reject  [ ] edit: ...

### C10: "just don't keep anything in here that doesn't serve every task ... Those things usually you want to move to skills"
Kind: source
Status: ✅ correct
Proposal: Keep the claim. CLAUDE.md loads at session start. A skill loads its name and description, and loads its full instructions only when Claude uses it.
Sources: https://code.claude.com/docs/en/costs (checked 2026-10-04)
Decision: [x] accept  [ ] reject  [ ] edit: ...

### C11: "each MCP can bring its tool descriptions into the context, so do not turn on a connection that the session does not need" (translated)
Kind: source
Status: ⚠️ outdated
Proposal: MCP tool definitions are deferred by default. Only tool names and server instructions enter the context until Claude uses a tool. Keep the advice to disable unused servers with `/mcp`. Add: prefer CLI tools such as `gh` when they exist, because they add no tool listing.
Sources: https://code.claude.com/docs/en/costs (checked 2026-10-04)
Decision: [x] accept  [ ] reject  [ ] edit: ...

### C12: "change the command so that it returns only the failed lines ... then write that command in CLAUDE.md" (translated)
Kind: source
Status: ⚠️ can be optimised
Proposal: Keep the claim. Add the option from the docs: a PreToolUse hook can filter test output to show only failures, for every run, without a CLAUDE.md instruction.
Sources: https://code.claude.com/docs/en/costs (checked 2026-10-04)
Decision: [x] accept  [ ] reject  [ ] edit: ...

### C13: "it does all the reading and all the tool calls over there and it only sends you the final conclusion back"
Kind: source
Status: ✅ correct
Proposal: Keep the claim. Add: a subagent still uses tokens. Choose a smaller model for a subagent to spend less.
Sources: https://code.claude.com/docs/en/costs (checked 2026-10-04), https://code.claude.com/docs/en/sub-agents (checked 2026-10-04)
Decision: [x] accept  [ ] reject  [ ] edit: ...

### C14: "the bottom session uses twice the amount of tokens as a top session"
Kind: source
Status: ✅ correct
Proposal: Keep the claim as the example from the talk. The docs confirm the rule: use `/clear` between unrelated tasks. Use `/rename` before `/clear`, and `/resume` to return.
Sources: https://code.claude.com/docs/en/costs (checked 2026-10-04)
Decision: [x] accept  [ ] reject  [ ] edit: ...

### C15: "on a monthly plan the cache lasts about 1 hour, with the API only about 5 minutes" (translated)
Kind: source
Status: ✅ correct
Proposal: Keep the claim with the exact rule: a Claude subscription within plan usage gets a one-hour TTL for the main conversation. An API key, usage credits, or a cloud provider get five minutes. Subagents and compaction get five minutes. Each cache hit resets the timer. `promptCacheTtl` can change the main TTL.
Sources: https://code.claude.com/docs/en/prompt-caching (checked 2026-10-04)
Decision: [x] accept  [ ] reject  [ ] edit: ...

### C16: "try to compact or change before you step away, not when you come back"
Kind: source
Status: ✅ correct
Proposal: Keep the claim. Add: `/rewind` keeps the cache, because it goes back to a prefix that is already cached. Use it instead of `/compact` to drop a failed path.
Sources: https://code.claude.com/docs/en/prompt-caching (checked 2026-10-04)
Decision: [x] accept  [ ] reject  [ ] edit: ...

### C17: "when a team spend is unexpectedly high, this usually traces back to just the biggest model just being left on as a default"
Kind: source
Status: ✅ correct
Proposal: Keep the claim. The docs give two causes: long sessions without `/clear`, and Opus left as the default model. Managed settings set the defaults for a team. `/usage` shows the cache hit line.
Sources: https://code.claude.com/docs/en/costs (checked 2026-10-04)
Decision: [x] accept  [ ] reject  [ ] edit: ...

## Placement

Primary topic: tokens-and-cost
Secondary topics: context-and-memory
New topic: none
Notes: two new notes. `tokens-and-cost/claude-code-prompt-cache-cost.md` (C1 to C9, C15, C16, C17) with secondary topic `context-and-memory`. `context-and-memory/claude-code-context-hygiene.md` (C10 to C14) with secondary topic `tokens-and-cost`. The notes link to each other in `Related`.
Diagram: one Mermaid diagram in `claude-code-prompt-cache-cost.md`: four turns, the cached prefix, and the point where a change recomputes the rest.
Decision: [x] accept  [ ] reject  [ ] edit: ...
