---
title: Prove the work on the real artifact
topics: [workflows, evals-and-observability, context-and-memory]
sources:
  - url: https://github.com/cursor/plugins/tree/main/pstack
    accessed: 2026-10-04
  - url: https://code.claude.com/docs/en/best-practices
    accessed: 2026-10-04
  - url: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
    accessed: 2026-10-04
verified_at: 2026-10-04
confidence: high
last_reviewed: 2026-10-04
---

## Summary

A task is done only when the agent observes the real artifact.
A compile, a self-report, or a test that cannot fail is not proof.
After repeated failed fixes, examine the shared premise.
Keep bulk output out of the main context.

## Details

### Verify the real artifact

> Verify against the real artifact (run the feature, read the actual value, inspect the diff), not a proxy, self-report, or 'it compiles.'

File times, cached screenshots, and the report of an agent do not count as proof.
When a check fails, the agent first suspects its method of observation, then the system.
The strongest proof is a deterministic script that runs the same comparison again.
Claude Code best practices agree: give Claude a check that it can run, and ask for evidence such as test output.

### Grade the evidence for each safety fact

> For each fact the change's safety depends on, get it as far down this list as is cheap, and say where it stopped.

The blast-radius skill grades each fact on five steps:

<!-- ste:strict -->
1. Said so.
2. Pointed at the line.
3. Showed that the bad case cannot reach the line.
4. Ran a script or a test on the real code.
5. Reproduced it in the running app.
<!-- /ste:strict -->

Step 1 has no value alone.
The writeup states the step that each fact reached, or marks the fact as unproven.

### A test must be able to fail

> it would still pass if every function it imports returned `undefined`. If yes, it observes no behavior and cannot fail for a defect

If a test passes when every imported function returns `undefined`, the author rewrites the assertion or deletes the test.
Examples are assertions on mocks only, such as `toHaveBeenCalled`, and assertions that compare a value with itself, such as `expect(f(a)).toBe(f(a))`.
The fix calls the subject with one concrete input and asserts the literal output or the visible effect.

### Attack the premise

> When two or more fixes that share one premise have failed the same gate, suspect the premise, not the fixes.

The agent writes the premise as one sentence that every failed fix assumed.
Before the next fix, it measures the problem with a script that it can run again.
Claude Code docs give related advice: after two failed corrections, use `/clear` and write a better prompt.

### Guard the context window

> Route verbose outputs, screenshots, and large documents to subagents. The main context gets summaries, not raw data.

Anthropic describes the same pattern.
A subagent can use tens of thousands of tokens and returns a summary of often 1,000 to 2,000 tokens.
An agent can also keep results in files and read slices with `head` and `tail`.

## My takeaways

- I do not accept "done" from an agent without evidence: command output, a diff, or the running result.
- After two failed fixes, I stop and examine the shared premise before the third fix.

## Related

- [Encode lessons in checks, not in instructions](../guardrails/encode-lessons-in-checks.md)
- [Assign agents by role, not by model name](assign-agents-by-role.md)
- [Keep the Claude Code context small](../context-and-memory/claude-code-context-hygiene.md)
- [Blind evals for skills and models](../evals-and-observability/blind-evals-for-skills-and-models.md)

## Sources

- pstack plugin: `principle-prove-it-works`, `blast-radius`, `principle-test-behavior-not-implementation`, `principle-attack-the-premise`, and `principle-guard-the-context-window`. https://github.com/cursor/plugins/tree/main/pstack
- Claude Code: best practices, checks and evidence. https://code.claude.com/docs/en/best-practices
- Anthropic: effective context engineering for AI agents, subagent summaries. https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
