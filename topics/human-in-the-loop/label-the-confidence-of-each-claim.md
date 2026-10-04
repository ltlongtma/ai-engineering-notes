---
title: Label the confidence of each claim
topics: [human-in-the-loop, evals-and-observability]
sources:
  - url: https://github.com/cursor/plugins/tree/main/pstack
    accessed: 2026-10-04
  - url: https://arxiv.org/abs/2310.13548
    accessed: 2026-10-04
verified_at: 2026-10-04
confidence: high
last_reviewed: 2026-10-04
---

## Summary

A person can trust an agent report only when each claim shows its evidence or its confidence.
pstack sorts claims into five tiers, treats the guess of the user as one candidate, and accepts "Unknown" as a valid result.
An append-only decision log keeps the trail for an audit.

## Details

### Five tiers

> Every claim in the final output must sit in one of these tiers. The tier determines which output section the claim goes in

| Tier | How the agent writes it |
|---|---|
| Direct | Confident present tense, with a citation. |
| Supported | Several sources agree. |
| Inferred | A hedge such as "likely" or "suggests". |
| Speculative | Usually in the "Competing Hypotheses" section. |
| Unknown | The agent names where it searched. |

### The sycophancy trap

> Treat it as one candidate among others and check the evidence independently.

A user often puts a guess in a question, for example "I assume it's for performance?".
The agent checks the evidence independently and reports support only when the evidence supports the guess.
The paper "Towards Understanding Sycophancy in Language Models" shows that AI assistants can favor answers that match user beliefs.
These answers can be less truthful.

### Unknown is a result

> You looked and couldn't find out. A valid and important outcome. Document it.

The agent names what it searched, for example the trackers, the PRs, and the keywords.
The output has a "What We Don't Know" section, and a missing section is suspicious.

### Evidence in the same sentence

> Every claim carries its evidence or its label in the same sentence.

The labels are measured, inferred, and guess.
A prediction or a cause that the agent did not see counts as a guess.
The agent never gives the human a check that it can run itself.

### Decision log

> Append-only. A wrong call gets a new row that supersedes it. Never edit or delete history.

The show-me-your-work skill keeps one TSV log with six columns: `ts`, `phase`, `decision`, `why`, `evidence`, and `result`.
Before handback, the agent compares the log with its run transcript and adds rows to correct it.
A review subagent on a different model follows.

## My takeaways

- My kb-ingest review report is a human-in-the-loop gate of the same type: each claim has a status, a source, and my decision.
- I ask the agent to keep a hypothesis from me as one candidate, not as the answer.
- "Unknown" with a list of the searched places is a better result than a confident guess.

## Related

- [Treat the spec as the source of truth](../workflows/spec-is-the-source-of-truth.md)
- [Prove the work on the real artifact](../workflows/prove-the-work-on-the-real-artifact.md)
- [Blind evals for skills and models](../evals-and-observability/blind-evals-for-skills-and-models.md)

## Sources

- pstack plugin: `why/references/epistemics.md`, `poteto-mode` reply rules, and `show-me-your-work`. https://github.com/cursor/plugins/tree/main/pstack
- Sharma et al.: Towards Understanding Sycophancy in Language Models. https://arxiv.org/abs/2310.13548
