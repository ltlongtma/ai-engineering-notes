---
title: Blind evals for skills and models
topics: [evals-and-observability, workflows]
sources:
  - url: https://github.com/cursor/plugins/tree/main/pstack
    accessed: 2026-10-04
  - url: https://arxiv.org/abs/2404.13076
    accessed: 2026-10-04
  - url: https://arxiv.org/abs/2306.05685
    accessed: 2026-10-04
  - url: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
    accessed: 2026-10-04
verified_at: 2026-10-04
confidence: high
last_reviewed: 2026-10-04
---

## Summary

To measure a skill change, hide the eval from the candidate and hide the model names from the judge.
Use a judge from a different model family, and grade from the transcript, not from the self-report.
A number needs its limiter, its run count, and its spread.

## Details

### Blind the candidate

> The candidate prompt looks like an organic user request. State the goal, not the meta.

No directory, file, or prompt that the candidate sees contains the words eval, test, judge, experiment, rubric, score, compare, benchmark, candidate, or arena.
The agent also removes requests to list the skills that the candidate applied.

### Blind the judge

> Spawn one blinded judge on a different model family ... Judge sees outputs by sanitized label and the rubric, never a model name.

To compare two variants, one judge scores both sets in one pass on one scale.
This design can decrease self-preference bias.
Panickssery et al. show that LLM evaluators score their own outputs higher.
Zheng et al. also name self-enhancement bias in LLM judges.
Neither paper tests a judge from a different family as the fix.

### Grade from the transcript

> Grade chain-following from the files it really read plus the shape of the code, never from the candidate's own claims.

The playbook reads each candidate transcript and checks which files the candidate opened.
Anthropic gives the same advice: read transcripts, because the result in the environment can differ from what the agent says.

### Arena and review panel

> Fan out N parallel attempts at the same task ... Pick the strongest as the base. Graft the best ideas from the others into it.

The arena skill sends one prompt to N candidates on three model families, each in its own directory.
One read-only judge scores them against 3 to 6 criteria.
The parent reads every candidate, selects a base, adds the best ideas by hand, and verifies the result.

> Spawn one reviewer per configured model to adversarially review code changes.

The interrogate skill gives each reviewer the same prompt, so the signal comes from model diversity and not from personas.
The lead sorts each finding into Act on, Consider, Noted, or Dismissed, and adds an Agreement Map.

### Numbers

> If you cannot say why the number is not twice as good, you do not know what you measured.

A number needs the limiter, the run count, and the spread.
The limiter comes from a profile or system counters, not from code reading.

> Run each side at least 5 times, and alternate the sides (A, B, A, B, and so on)

The agent reports the median and the range.
The verdict is faster, slower, no measurable difference, or inconclusive.
A gap smaller than the variation between runs counts as no measurable difference.

## My takeaways

- Before I trust a change to a skill, I compare the old and the new skill on the same prompts.
- The judge must not see the model names, and it must come from a different model family.
- I grade the agent from its transcript, not from its own report.

## Related

- [Label the confidence of each claim](../human-in-the-loop/label-the-confidence-of-each-claim.md)
- [Prove the work on the real artifact](../workflows/prove-the-work-on-the-real-artifact.md)
- [Assign agents by role, not by model name](../workflows/assign-agents-by-role.md)

## Sources

- pstack plugin: `poteto-mode/playbooks/eval.md`, `arena`, `interrogate`, `principle-explain-the-number`, and `benchmark-checklist`. https://github.com/cursor/plugins/tree/main/pstack
- Panickssery et al.: LLM evaluators recognize and favor their own generations. https://arxiv.org/abs/2404.13076
- Zheng et al.: Judging LLM-as-a-judge with MT-Bench and Chatbot Arena. https://arxiv.org/abs/2306.05685
- Anthropic: demystifying evals for AI agents. https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
