# Review: pstack plugin (architecture, principles, and workflows)

Input: `https://github.com/cursor/plugins/tree/main/pstack`
Reference input: `https://github.com/github/spec-kit`. The owner named it as a reference for C7. C36 to C39 come from it.
Date: 2026-10-04

Write one decision in each `Decision:` line. Put an `x` in one box. For `edit`, write the new text after `edit:`.
Phase 2 stops if one or more `Decision:` lines have no mark.

Extraction: the skill read the README and the `SKILL.md` files of the pstack plugin from the `main` branch. For C36 to C39, the skill read the spec-kit README and `spec-driven.md`. A script compared each claim quote with the source file text. pstack is the personal style of one author. Many claims are recommendations, not measured facts. A Proposal says when no official source outside pstack states the same rule.

Owner direction: the note for C1 to C8 and C32 to C35 takes one idea as its center. The idea is to assign agents by role.

## Claims

### C1: "it reads your request, picks from a set of playbooks, and runs the other skills as the steps need them."
Kind: source
Status: ✅ correct
Proposal: The entry skill /poteto-mode reads the request, selects one playbook from a fixed set, and runs other skills when a playbook step needs them. This matches the routing workflow in Anthropic's guide, which classifies an input and sends it to a specialized follow-up task. The guide allows an LLM to do the classification. The guide also advises the simplest design that works, so the number of playbooks (twenty-three) is a cost to watch.
Sources: https://raw.githubusercontent.com/cursor/plugins/main/pstack/README.md (checked 2026-10-04), https://www.anthropic.com/engineering/building-effective-agents (checked 2026-10-04)
Decision: [x] accept  [ ] reject  [ ] edit: ...

### C2: "the matched playbook's steps, copied in verbatim, before any task-specific todos. ... A step you choose not to do stays in the list"
Kind: source
Status: ✅ correct
Proposal: The agent copies the matched playbook steps word for word into its todo list, before any task-specific item. A step the agent chooses not to do stays in the list with a one-line `skip: <reason>`. This keeps the plan visible and lets a reviewer see each omission. It agrees with Anthropic's principle to show the agent's planning steps explicitly. No official source outside pstack states the copy-verbatim rule.
Sources: https://raw.githubusercontent.com/cursor/plugins/main/pstack/skills/poteto-mode/SKILL.md (checked 2026-10-04), https://www.anthropic.com/engineering/building-effective-agents (checked 2026-10-04)
Decision: [x] accept  [ ] reject  [ ] edit: ...

### C3: "twenty-four short skills, one principle each. `poteto-mode` indexes them inline and reads that index at task start."
Kind: source
Status: ✅ correct
Proposal: Each principle is a short skill with one rule. poteto-mode holds an inline index of all principles and reads that index at the start of a task. The standalone files let other skills reference a principle by name and let the index point to the full rule. Claude Code best practices support this split. They say to put occasional knowledge in skills, which load on demand, and to keep always-loaded files short.
Sources: https://raw.githubusercontent.com/cursor/plugins/main/pstack/README.md (checked 2026-10-04), https://code.claude.com/docs/en/best-practices (checked 2026-10-04)
Decision: [x] accept  [ ] reject  [ ] edit: ...

### C4: "it reads `poteto-mode` in full, including its inline principles index, before doing any work. substituting `generalPurpose` skips that read and drifts."
Kind: source
Status: ⚠️ can be optimised
Proposal: The poteto-agent subagent instructs itself to read poteto-mode in full before any work. Claude Code docs say a subagent starts in a fresh context. It does not see invoked skills or earlier reads. So a general-purpose agent has no poteto-mode content unless the parent passes it. The `skills` frontmatter field can inject the full skill content at startup and would remove the dependence on an instruction to read the file. Plugin subagents support this field. No fetched source measures the "drifts" effect.
Sources: https://raw.githubusercontent.com/cursor/plugins/main/pstack/agents/poteto-agent.md (checked 2026-10-04), https://raw.githubusercontent.com/cursor/plugins/main/pstack/README.md (checked 2026-10-04), https://code.claude.com/docs/en/sub-agents (checked 2026-10-04)
Decision: [x] accept  [ ] reject  [ ] edit: ...

### C5: "Write `~/.cursor/rules/pstack-models.mdc`, an always-applied rule that sets pstack's model per role."
Kind: source
Status: ✅ correct
Proposal: setup-pstack detects the available models, asks for a reasoning budget, and writes one always-applied rule file with one line per role. Roles include bug-fix, judgment and prose, hardest tasks, and the arena runners list. Skills name a role, and the rule maps the role to a model. The values `inherit-parent` and `auto` mean the role runs on the parent chat model. Claude Code has a similar design. A subagent has a `model` field (alias, full ID, or `inherit`) and an `effort` field, and a fixed order decides which source wins.
Sources: https://raw.githubusercontent.com/cursor/plugins/main/pstack/skills/setup-pstack/SKILL.md (checked 2026-10-04), https://code.claude.com/docs/en/sub-agents (checked 2026-10-04)
Decision: [x] accept  [ ] reject  [ ] edit: ...

### C6: "The definition of done as a falsifiable predicate ... Build the verification harness before the work ... measure against the predicate on the real artifact"
Kind: source
Status: ✅ correct
Proposal: figure-it-out applies when no bundled playbook fits, such as a large migration. The agent first states done as a falsifiable predicate. It then builds the verification harness before the work, with a baseline from the pre-change state. It runs each unit as a hypothesis loop: make the smallest change, measure against the predicate, keep or revert. A final step checks the whole result against the predicate. Claude Code best practices agree. They say to give Claude a check it can run, and they offer /goal and Stop hooks to gate the stop on that check.
Sources: https://raw.githubusercontent.com/cursor/plugins/main/pstack/skills/figure-it-out/SKILL.md (checked 2026-10-04), https://code.claude.com/docs/en/best-practices (checked 2026-10-04)
Decision: [x] accept  [ ] reject  [ ] edit: ...

### C7: "i don't believe in planning. the best spec is code."
Kind: source
Status: ⚠️ not best practice
Proposal: The pstack README states this opinion and says Cursor's plan mode works with pstack. It also says poteto-mode covers planning on request, but not by default. Claude Code best practices recommend a different default: explore, plan, then code. They say planning helps most when the approach is uncertain, when the change touches multiple files, or when the code is unfamiliar. For a larger feature, they also say to let Claude interview you, write a complete spec to SPEC.md, and execute it in a fresh session. The note should record the pstack claim as a personal opinion that conflicts with the official advice for multi-file work.
Sources: https://raw.githubusercontent.com/cursor/plugins/main/pstack/README.md (checked 2026-10-04), https://code.claude.com/docs/en/best-practices (checked 2026-10-04)
Decision: [ ] accept  [ ] reject  [x] edit: The pstack author skips planning by default. The owner uses four steps: explore, spec, plan, then execute. The spec has higher trust than the plan, because the plan comes from the spec. C36 to C39 give the spec-kit view.

### C8: "Always pause for irreversible writes: force-push to shared branches, deploys, data deletion, customer messages."
Kind: source
Status: ⚠️ can be optimised
Proposal: pstack tells the agent to proceed without asking on reversible work and to pause for irreversible writes. The never-block-on-the-human principle states the same rule. This is a prompt instruction, so the model may ignore it. Claude Code docs say hooks are deterministic while instructions are advisory. Permission ask or deny rules, for example `Bash(git push *)`, enforce a pause. Reversibility also needs care. Checkpoint rewind does not undo Bash changes such as rm or mv, and it does not restore subagent edits. Only version control gives a dependable undo.
Sources: https://raw.githubusercontent.com/cursor/plugins/main/pstack/skills/poteto-mode/SKILL.md (checked 2026-10-04), https://raw.githubusercontent.com/cursor/plugins/main/pstack/skills/principle-never-block-on-the-human/SKILL.md (checked 2026-10-04), https://code.claude.com/docs/en/checkpointing (checked 2026-10-04), https://code.claude.com/docs/en/permission-modes (checked 2026-10-04), https://code.claude.com/docs/en/best-practices (checked 2026-10-04)
Decision: [x] accept  [ ] reject  [ ] edit: ...

### C9: "When you catch yourself writing the same instruction a second time ... If yes, encode it. Delete the instruction"
Kind: source
Status: ✅ correct
Proposal: When an agent writes the same instruction a second time, pstack says to replace it with a mechanism and delete the text. The file orders mechanisms from strongest to weakest. First comes a state that cannot compile, then a lint or banned API that fails CI, then a canonical helper, then a runtime check. The correct skill places docs and agent rules last, only for judgment calls. If a rule needs judgment, pstack keeps the text, makes it more prominent, and adds an example of the failure. Claude Code docs support the idea, because CLAUDE.md instructions are advisory and hooks are deterministic.
Sources: https://raw.githubusercontent.com/cursor/plugins/main/pstack/skills/principle-encode-lessons-in-structure/SKILL.md (checked 2026-10-04), https://raw.githubusercontent.com/cursor/plugins/main/pstack/skills/correct/SKILL.md (checked 2026-10-04), https://code.claude.com/docs/en/best-practices (checked 2026-10-04), https://code.claude.com/docs/en/hooks-guide (checked 2026-10-04)
Decision: [x] accept  [ ] reject  [ ] edit: ...

### C10: "A class counts once it has happened twice ... Fix each class at the highest level that works"
Kind: source
Status: ✅ correct
Proposal: The correct skill counts a mistake class once the same mistake happened twice. It fixes each class at the highest level that works. The order is architecture, then types, then a lint or CI check whose error names the replacement, then tests, then docs and agent rules. The skill writes docs last, only for judgment calls, because nothing fails when an agent skips them. Claude Code docs agree that CLAUDE.md instructions are advisory while hooks are deterministic.
Sources: https://raw.githubusercontent.com/cursor/plugins/main/pstack/skills/correct/SKILL.md (checked 2026-10-04), https://code.claude.com/docs/en/best-practices (checked 2026-10-04)
Decision: [x] accept  [ ] reject  [ ] edit: ...

### C11: "Prove each new check fails on a real past mistake. Run the same command locally and in CI."
Kind: source
Status: ✅ correct
Proposal: The correct skill requires proof that each new check works. The check must fail on a real past mistake. The same command runs locally and in CI. Exceptions go on the offending line with a reason, an expiry date, and a human's approval. No official source outside pstack states this rule.
Sources: https://raw.githubusercontent.com/cursor/plugins/main/pstack/skills/correct/SKILL.md (checked 2026-10-04)
Decision: [x] accept  [ ] reject  [ ] edit: ...

### C12: "keep a table in the agent instruction file that pairs each rule with what enforces it"
Kind: source
Status: ✅ correct
Proposal: The agent instruction file holds a table that pairs each rule with the mechanism that enforces it. When the operator corrects an agent, the agent fixes the mistake and adds the rule. If the rule already existed and nothing enforces it, the correction is a repeat. Then the agent fixes it at the highest level in the same change. The agent drops a rule once its mistake cannot happen. Claude Code docs call CLAUDE.md advisory and advise pruning it, which fits this table.
Sources: https://raw.githubusercontent.com/cursor/plugins/main/pstack/skills/correct/SKILL.md (checked 2026-10-04), https://code.claude.com/docs/en/best-practices (checked 2026-10-04)
Decision: [x] accept  [ ] reject  [ ] edit: ...

### C13: "Verify against the real artifact (run the feature, read the actual value, inspect the diff), not a proxy, self-report, or 'it compiles.'"
Kind: source
Status: ✅ correct
Proposal: pstack says to verify the real artifact before declaring a task done. A compile, file mtimes, output freshness, cached screenshots, and an agent self-report do not count as proof. When a check fails, the agent suspects the observation method before the system. The strongest proof is a deterministic script that reruns the same comparison. Claude Code docs agree. They advise giving Claude a check it can run and having it show evidence, such as test output, instead of asserting success.
Sources: https://raw.githubusercontent.com/cursor/plugins/main/pstack/skills/principle-prove-it-works/SKILL.md (checked 2026-10-04), https://code.claude.com/docs/en/best-practices (checked 2026-10-04)
Decision: [x] accept  [ ] reject  [ ] edit: ...

### C14: "When the work isn't trivial, build the tool that does it instead of doing it by hand."
Kind: source
Status: ✅ correct
Proposal: For non-trivial work, pstack builds a rerunnable tool, such as a codemod, script, or generator, instead of working by hand. The tool gives repeatable throughput and one artifact that a reviewer can read and rerun. The agent does the first unit by hand, builds the tool, and diffs the tool output against the hand result. The bar is triviality, not repetition, and the tool stays the smallest script that does the job. Claude Code docs list a script that diffs output against a fixture as a valid check. No official source outside pstack states the default of building a tool for all non-trivial work.
Sources: https://raw.githubusercontent.com/cursor/plugins/main/pstack/skills/principle-build-the-lever/SKILL.md (checked 2026-10-04), https://code.claude.com/docs/en/best-practices (checked 2026-10-04)
Decision: [x] accept  [ ] reject  [ ] edit: ...

### C15: "it would still pass if every function it imports returned `undefined`. If yes, it observes no behavior and cannot fail for a defect"
Kind: source
Status: ✅ correct
Proposal: pstack asks whether a test would still pass if every function it imports returned undefined. If yes, the test observes no behavior, so the author rewrites the assertion or deletes the test. The file lists five such shapes, including mock-only assertions such as toHaveBeenCalled and self-referential assertions such as expect(f(a)).toBe(f(a)). The fix calls the subject with one concrete input and asserts the literal output or the observable effect. Claude Code docs also give literal expected cases in a prompt, such as user@example.com is true. No official source outside pstack states the undefined check.
Sources: https://raw.githubusercontent.com/cursor/plugins/main/pstack/skills/principle-test-behavior-not-implementation/SKILL.md (checked 2026-10-04), https://code.claude.com/docs/en/best-practices (checked 2026-10-04)
Decision: [x] accept  [ ] reject  [ ] edit: ...

### C16: "When two or more fixes that share one premise have failed the same gate, suspect the premise, not the fixes."
Kind: source
Status: ✅ correct
Proposal: The file says two or more fixes, not exactly two, that share one premise and fail the same gate. The agent records the premise as one sentence that every failed fix assumed. Before the next fix, the agent counts the imbalance per actor with a rerunnable script. If the same few actors hold the imbalance on every run, the agent finds what assigns that role and removes the asymmetry. Claude Code docs address a related case. After two failed corrections, they advise running /clear and writing a better prompt. No official source outside pstack states the premise census.
Sources: https://raw.githubusercontent.com/cursor/plugins/main/pstack/skills/principle-attack-the-premise/SKILL.md (checked 2026-10-04), https://code.claude.com/docs/en/best-practices (checked 2026-10-04)
Decision: [x] accept  [ ] reject  [ ] edit: ...

### C17: "Route verbose outputs, screenshots, and large documents to subagents. The main context gets summaries, not raw data."
Kind: source
Status: ✅ correct
Proposal: pstack routes verbose outputs, screenshots, and large documents to subagents. The main context receives summaries instead of raw data. The file names subagents only, not files. Anthropic describes the same pattern. A subagent may use tens of thousands of tokens and returns a condensed summary, often 1,000 to 2,000 tokens. Anthropic also describes storing results in files and reading slices with head and tail, which keeps full data objects out of context.
Sources: https://raw.githubusercontent.com/cursor/plugins/main/pstack/skills/principle-guard-the-context-window/SKILL.md (checked 2026-10-04), https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents (checked 2026-10-04), https://code.claude.com/docs/en/best-practices (checked 2026-10-04)
Decision: [x] accept  [ ] reject  [ ] edit: ...

### C18: "For any item that would be enforced more reliably by a lint rule ... move it from Accepted to Backlog"
Kind: source
Status: ✅ correct
Proposal: The reflect skill starts three parallel reviewers over the active transcript, one each for the judgment, tooling, and divergent lenses. A synthesizer merges their findings into Accepted, Rejected, and Backlog lists. The parent then checks the Accepted list. An item that a lint rule, script, metadata flag, or runtime check would enforce more reliably moves from Accepted to Backlog. The file does not mention prompt text. The synthesizer says skill prose is for things that mechanisms cannot enforce. The user approves the Accepted list before the parent applies any edit. Claude Code docs agree that hooks enforce deterministically while CLAUDE.md instructions are advisory.
Sources: https://raw.githubusercontent.com/cursor/plugins/main/pstack/skills/reflect/SKILL.md (checked 2026-10-04), https://raw.githubusercontent.com/cursor/plugins/main/pstack/skills/reflect/references/synthesizer.md (checked 2026-10-04), https://code.claude.com/docs/en/best-practices (checked 2026-10-04)
Decision: [x] accept  [ ] reject  [ ] edit: ...

### C19: "For each fact the change's safety depends on, get it as far down this list as is cheap, and say where it stopped."
Kind: source
Status: ✅ correct
Proposal: For each fact that a change's safety rests on, blast-radius grades the evidence on a five-step ladder. The steps are: said so, pointed at the line, showed the bad case cannot reach, ran it, and reproduced it in the running app. Step 1 is worthless on its own. Step 4 is a script or test that calls the real code and fails loud if the claim is wrong. The writeup states which step the fact reached, or marks it unproven. Claude Code docs also advise showing evidence, such as test output, instead of asserting success. No official source outside pstack states this ladder.
Sources: https://raw.githubusercontent.com/cursor/plugins/main/pstack/skills/blast-radius/SKILL.md (checked 2026-10-04), https://code.claude.com/docs/en/best-practices (checked 2026-10-04)
Decision: [x] accept  [ ] reject  [ ] edit: ...

### C20: "Every claim in the final output must sit in one of these tiers. The tier determines which output section the claim goes in"
Kind: source
Status: ✅ correct
Proposal: The why skill sorts every claim into one of five confidence tiers: Direct, Supported, Inferred, Speculative, and Unknown. The tier decides the output section and the phrasing. Direct claims use confident present tense with a citation. Inferred claims use hedges such as "likely" or "suggests". Speculative claims usually appear in the "Competing Hypotheses" section. No official source outside pstack states this rule.
Sources: https://raw.githubusercontent.com/cursor/plugins/main/pstack/skills/why/references/epistemics.md (checked 2026-10-04)
Decision: [x] accept  [ ] reject  [ ] edit: ...

### C21: "Treat it as one candidate among others and check the evidence independently."
Kind: source
Status: ✅ correct
Proposal: A user often puts a hypothesis inside a why question, for example "I assume it's for performance?". The why skill calls this the sycophancy trap. The agent treats the guess as one candidate and checks the evidence independently. It reports support only when the evidence supports it. The paper "Towards Understanding Sycophancy in Language Models" shows that AI assistants can favor answers that match user beliefs. These answers can be less truthful. The paper supports the rule.
Sources: https://raw.githubusercontent.com/cursor/plugins/main/pstack/skills/why/references/epistemics.md (checked 2026-10-04), https://arxiv.org/abs/2310.13548 (checked 2026-10-04)
Decision: [x] accept  [ ] reject  [ ] edit: ...

### C22: "You looked and couldn't find out. A valid and important outcome. Document it."
Kind: source
Status: ✅ correct
Proposal: "Unknown" is the fifth tier and counts as a valid outcome. The agent must name what it searched, for example the trackers, the PRs, and the keywords. A vague "we couldn't find out" is less useful. The output also needs a "What We Don't Know" section, and a missing section is suspicious. No official source outside pstack states this rule.
Sources: https://raw.githubusercontent.com/cursor/plugins/main/pstack/skills/why/references/epistemics.md (checked 2026-10-04)
Decision: [x] accept  [ ] reject  [ ] edit: ...

### C23: "Every claim carries its evidence or its label in the same sentence."
Kind: source
Status: ✅ correct
Proposal: The poteto-mode reply rules require each claim to carry either its evidence or a label in the same sentence. The labels are measured, inferred, and guess. A prediction or an unseen cause counts as a guess. The same rule says the agent never hands the human a check it could run itself. The pstack text says "label", not "uncertainty label". No official source outside pstack states this rule.
Sources: https://raw.githubusercontent.com/cursor/plugins/main/pstack/skills/poteto-mode/SKILL.md (checked 2026-10-04)
Decision: [x] accept  [ ] reject  [ ] edit: ...

### C24: "Append-only. A wrong call gets a new row that supersedes it. Never edit or delete history."
Kind: source
Status: ✅ correct
Proposal: The show-me-your-work skill keeps one TSV decision log with six columns: ts, phase, decision, why, evidence, and result. The log is append-only, and a wrong call gets a new row that supersedes the old one. Before handback, the agent audits the log against its own run transcript. The audit adds superseding rows and never edits or removes rows. A cross-model subagent review follows the audit. No official source outside pstack states this rule.
Sources: https://raw.githubusercontent.com/cursor/plugins/main/pstack/skills/show-me-your-work/SKILL.md (checked 2026-10-04), https://raw.githubusercontent.com/cursor/plugins/main/pstack/skills/show-me-your-work/references/decision-log-template.tsv (checked 2026-10-04)
Decision: [x] accept  [ ] reject  [ ] edit: ...

### C25: "The candidate prompt looks like an organic user request. State the goal, not the meta."
Kind: source
Status: ✅ correct
Proposal: The eval playbook blinds the candidate. No directory, file, or prompt that the candidate sees may contain the words eval, test, judge, experiment, rubric, score, compare, benchmark, candidate, or arena. The prompt reads like a normal user request. The agent also removes cues that ask the candidate to list the skills it applied, and it sanitizes directory names. No official source outside pstack states this rule.
Sources: https://raw.githubusercontent.com/cursor/plugins/main/pstack/skills/poteto-mode/playbooks/eval.md (checked 2026-10-04)
Decision: [x] accept  [ ] reject  [ ] edit: ...

### C26: "Spawn one blinded judge on a different model family ... Judge sees outputs by sanitized label and the rubric, never a model name."
Kind: source
Status: ✅ correct
Proposal: The eval playbook runs one judge on a different model family from the candidates. The judge sees outputs by sanitized label only and never sees a model name. To compare two variants, one judge scores both sets in a single pass on one scale, blind to the set of origin. This design may lower self-preference bias. Panickssery et al. show that LLM evaluators score their own outputs higher and that self-recognition correlates with this bias. Zheng et al. also name self-enhancement bias in LLM judges. Neither paper tests a judge from a different model family as the fix.
Sources: https://raw.githubusercontent.com/cursor/plugins/main/pstack/skills/poteto-mode/playbooks/eval.md (checked 2026-10-04), https://arxiv.org/abs/2404.13076 (checked 2026-10-04), https://arxiv.org/abs/2306.05685 (checked 2026-10-04)
Decision: [x] accept  [ ] reject  [ ] edit: ...

### C27: "Grade chain-following from the files it really read plus the shape of the code, never from the candidate's own claims."
Kind: source
Status: ✅ correct
Proposal: The eval playbook reads each candidate transcript in the active workspace and checks which files the candidate opened. It does not trust the candidate's self-report. Anthropic gives matching guidance. Its engineering post says that a grader needs checks against transcripts. The transcript shows whether a failure is a genuine mistake or a grader fault. The outcome in the environment can differ from what the agent says.
Sources: https://raw.githubusercontent.com/cursor/plugins/main/pstack/skills/poteto-mode/playbooks/eval.md (checked 2026-10-04), https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents (checked 2026-10-04)
Decision: [x] accept  [ ] reject  [ ] edit: ...

### C28: "Fan out N parallel attempts at the same task ... Pick the strongest as the base. Graft the best ideas from the others into it."
Kind: source
Status: ✅ correct
Proposal: The arena skill sends the same prompt to N candidates. By default the candidates run on three model families, each in its own git worktree or /tmp directory. The skill allows the same model N times when the work is generation-bound. After all candidates finish, one readonly cross-judge, preferably from a different family, scores them against a rubric of 3-6 criteria. The parent reads every candidate, picks a base, grafts the best ideas by hand, and verifies the result. No official source outside pstack states this rule.
Sources: https://raw.githubusercontent.com/cursor/plugins/main/pstack/skills/arena/SKILL.md (checked 2026-10-04)
Decision: [x] accept  [ ] reject  [ ] edit: ...

### C29: "Spawn one reviewer per configured model to adversarially review code changes."
Kind: source
Status: ✅ correct
Proposal: The interrogate skill runs a multi-model review panel. Each reviewer gets the same prompt and rubric, so the adversarial signal comes from model diversity and not from assigned personas. The lead then sorts every finding into four buckets: Act on, Consider, Noted, and Dismissed. The output also has an Agreement Map. The skill does not apply changes automatically. No official source outside pstack states this rule.
Sources: https://raw.githubusercontent.com/cursor/plugins/main/pstack/skills/interrogate/SKILL.md (checked 2026-10-04)
Decision: [x] accept  [ ] reject  [ ] edit: ...

### C30: "If you cannot say why the number is not twice as good, you do not know what you measured."
Kind: source
Status: ✅ correct
Proposal: A reported number needs three items of evidence: the limiter, the run count, and the spread. The limiter answers "why not double?" and comes from a profile or system counters, not from reading code. The notes or a linked artifact keep these items with the number. pstack counts a number without a run count, spread, or named limiter as a skipped check. No official source outside pstack states this rule.
Sources: https://raw.githubusercontent.com/cursor/plugins/main/pstack/skills/principle-explain-the-number/SKILL.md (checked 2026-10-04)
Decision: [x] accept  [ ] reject  [ ] edit: ...

### C31: "Run each side at least 5 times, and alternate the sides (A, B, A, B, and so on)"
Kind: source
Status: ✅ correct
Proposal: The benchmark checklist requires at least 5 runs per side, with the sides alternating so that warmup and drift do not favor one side. The agent reports the median and the range. The verdict is one of four: faster, slower, no measurable difference, or inconclusive. A gap smaller than run-to-run variation counts as no measurable difference. A quick ballpark that the user requested may use one run if the report says so. No official source outside pstack states this rule.
Sources: https://raw.githubusercontent.com/cursor/plugins/main/pstack/skills/benchmark-checklist/SKILL.md (checked 2026-10-04)
Decision: [x] accept  [ ] reject  [ ] edit: ...

### C32: "explicit model per role (configurable via `/setup-pstack`. Defaults `grok-4.7-xhigh-fast` for code, `claude-opus-5-5-max` for prose and judgment)"
Kind: source
Status: ✅ correct
Proposal: Each subagent call in pstack names a role, and the role selects the model. The default roles are code, prose and judgment, and the review panels. Each skill names a role and not a model, so a model change touches one config file. The pstack README shows the cost of model names: a rule from before version 0.15.3 pins the old default models. Claude Code docs describe the same idea. Each subagent has its own context window, system prompt, tool access, and permissions. Its `model` field accepts an alias such as `sonnet`, `opus`, or `haiku`. The note should keep the role names and treat the model names as examples that expire.
Sources: https://raw.githubusercontent.com/cursor/plugins/main/pstack/skills/poteto-mode/SKILL.md (checked 2026-10-04), https://raw.githubusercontent.com/cursor/plugins/main/pstack/README.md (checked 2026-10-04), https://code.claude.com/docs/en/sub-agents (checked 2026-10-04)
Decision: [x] accept  [ ] reject  [ ] edit: ...

### C33: "A second opinion is the same prompt against a different model. Agreement is high-signal."
Kind: source
Status: ❓ unverified
Proposal: pstack gets a second opinion from a reviewer role that runs on a different model with the same prompt. It does not use a different persona. The interrogate and arena skills apply the same rule (C28, C29). The claim that agreement is high-signal has no measurement in pstack. Keep the mechanism. Mark the signal claim as unverified.
Sources: https://raw.githubusercontent.com/cursor/plugins/main/pstack/skills/poteto-mode/SKILL.md (checked 2026-10-04). Reason: no fetched official source measures how often agreement between models predicts a correct answer.
Decision: [x] accept  [ ] reject  [ ] edit: ...

### C34: "You own every subagent's work. Review the diff and write your own summary, don't pass through what it said."
Kind: source
Status: ✅ correct
Proposal: The coordinator role owns the result of each worker role. The coordinator reads the diff of each subagent and writes its own summary. It does not forward the report of the subagent to the human. This rule agrees with C27, which grades an agent on the transcript and not on its self-report. No official source outside pstack states this rule.
Sources: https://raw.githubusercontent.com/cursor/plugins/main/pstack/skills/poteto-mode/SKILL.md (checked 2026-10-04)
Decision: [x] accept  [ ] reject  [ ] edit: ...

### C35: "Fresh subagents by default. Give new work to a fresh subagent with consolidated scope"
Kind: source
Status: ✅ correct
Proposal: pstack gives each new piece of work to a fresh subagent. A fix round, a follow-up, a retry, and the next queue item each get a fresh subagent. The coordinator gives it the consolidated scope: the original brief, every later directive, and the report and branch of the prior agent. Claude Code docs give similar advice for a spec. They say to execute it in a fresh session with a clean context.
Sources: https://raw.githubusercontent.com/cursor/plugins/main/pstack/skills/poteto-mode/SKILL.md (checked 2026-10-04), https://code.claude.com/docs/en/best-practices (checked 2026-10-04)
Decision: [x] accept  [ ] reject  [ ] edit: ...

### C36: "Define what and why before deciding how to build it."
Kind: source
Status: ✅ correct
Proposal: GitHub spec-kit puts the spec before the plan. A project writes a constitution one time. Each feature then goes through specify, plan, tasks, implement, and converge. The agent repeats implement and converge until the converge step reports "Converged". Clarification, checklists, and consistency analysis are optional quality gates. Claude Code best practices give a similar order for larger features: an interview, then a spec in SPEC.md, then execution in a fresh session.
Sources: https://raw.githubusercontent.com/github/spec-kit/main/README.md (checked 2026-10-04), https://code.claude.com/docs/en/best-practices (checked 2026-10-04)
Decision: [x] accept  [ ] reject  [ ] edit: ...

### C37: "specifications as the central source of truth, with implementation plans and code as the continuously regenerated output"
Kind: source
Status: ✅ correct
Proposal: spec-kit calls this idea the power inversion: code serves the specification. The specification is the source of truth. The implementation plan and the code come from the specification, and the team can make them again. The plan maps each requirement to a technical decision, and each decision traces back to a requirement. Thus a change starts in the spec, and the plan follows. This is the philosophy of spec-kit, not a measured result.
Sources: https://raw.githubusercontent.com/github/spec-kit/main/spec-driven.md (checked 2026-10-04)
Decision: [x] accept  [ ] reject  [ ] edit: ...

### C38: "Instead of guessing that a "login system" uses email/password authentication, the LLM must mark it as"
Kind: source
Status: ✅ correct
Proposal: The spec-kit templates make the agent mark each ambiguity as `[NEEDS CLARIFICATION: <specific question>]`. The agent does not fill a gap with a guess. A spec is not complete while one marker remains. spec-kit says that this rule prevents plausible but incorrect assumptions. No fetched source measures this effect. The rule agrees with C22, where "Unknown" is a valid outcome.
Sources: https://raw.githubusercontent.com/github/spec-kit/main/spec-driven.md (checked 2026-10-04)
Decision: [x] accept  [ ] reject  [ ] edit: ...

### C39: "At the heart of SDD lies a constitution—a set of immutable principles that govern how specifications become code."
Kind: source
Status: ✅ correct
Proposal: The spec-kit constitution is a file of fixed project principles in `memory/constitution.md`. The plan step checks each plan against the constitution through gates, for example the Simplicity Gate (Article VII) and the Anti-Abstraction Gate (Article VIII). The implementation template also enforces test-first development. These gates are checks in the template text. They are not code that fails a build, so C9 applies to them.
Sources: https://raw.githubusercontent.com/github/spec-kit/main/spec-driven.md (checked 2026-10-04)
Decision: [x] accept  [ ] reject  [ ] edit: ...

## Placement

Primary topic: workflows
Secondary topics: guardrails, human-in-the-loop, evals-and-observability, context-and-memory
New topic: none
Overview: none
Notes: six new notes. `workflows/assign-agents-by-role.md` (C1 to C6, C8, C32 to C35) with the title "Assign agents by role, not by model name" and secondary topic `human-in-the-loop`. Its Summary starts from the role idea: a coordinator, worker roles, review roles, and a config that maps each role to a model. The playbook router and the principles index are details of how pstack gives each role its rules. `workflows/spec-is-the-source-of-truth.md` (C7, C36 to C39) with secondary topic `human-in-the-loop`. `guardrails/encode-lessons-in-checks.md` (C9 to C12, C14, C18) with secondary topic `workflows`. `workflows/prove-the-work-on-the-real-artifact.md` (C13, C15, C16, C17, C19) with secondary topics `evals-and-observability` and `context-and-memory`. `human-in-the-loop/label-the-confidence-of-each-claim.md` (C20 to C24) with secondary topic `evals-and-observability`. `evals-and-observability/blind-evals-for-skills-and-models.md` (C25 to C31) with secondary topic `workflows`. The notes link to each other in `Related`. This report does not propose a `tools/agent-skills.md` entry, because a tool entry needs the verdict of the owner. To add the entry, write a `# tool: <verdict>` line in `inbox/links.md`.
Diagram: three Mermaid diagrams. In `assign-agents-by-role.md`: the coordinator, the code, judgment, and review roles, the role config, and the models. In `spec-is-the-source-of-truth.md`: explore, spec, plan, tasks, and execute, with an arrow from the spec to the plan and the code. In `encode-lessons-in-checks.md`: the levels from architecture to docs, with the strongest level at the top.
Decision: [x] accept  [ ] reject  [ ] edit: ...
