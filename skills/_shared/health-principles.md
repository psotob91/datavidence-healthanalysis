# Health-data skill principles (shared)

> A short reference read by the datavidence-healthanalysis domain skills alongside their paired
> policy. NOT a skill (no frontmatter, never auto-invoked). It states the cross-skill invariants so
> each SKILL.md can stay a thin verb and not restate them. The authoritative methodology lives in
> the child project, not here (see section 5).

## 1. Math by tool, never by model
Never compute a number, percentage, count, rate, CI, p-value, or table total in your head. Numeric
work goes to R code (run via the executor subagent or the analysis pipeline). Symbolic or algebraic
work goes to WolframAlpha MCP or sympy/Ryacas. You reason about method; when you need a figure you
delegate to code and cite the output. Enforces the child policy analysis/numeric-computation.md.

## 2. Claim to evidence (no invention)
Every factual claim points to a retrievable anchor: a file:line, a reproducible command output, or a
canonical source (DOI or spec section). Never invent a column, code, field, threshold, or citation
not in the data dictionary, code set, or protocol. A code set carries source + version + extraction
date; copy identifying metadata exactly. If you cannot anchor it, mark it unverified; do not assert it.

## 3. PENDING_LOCAL_DECISION, never a silent default
When a methodological choice has not been made by the local protocol or SAP (a threshold, a washout
length, a population frame, a recurrence model), return PENDING_LOCAL_DECISION and name the choice.
Do not invent it, and do not bury it in a default. This is the stop-signal the child checklist
(docs/health/checklists.md) expects on any "no" or "unknown".

## 4. Comprehension before code
For any time-based clinical logic, draw it before you code it (decision + temporal diagram, shared
notation in docs/health/ascii-timelines.md). If you cannot draw the rule on a timeline, you do not
understand it well enough to code it. Get explicit human sign-off; silence is not consent.

## 5. The methodology lives in the child, not the plugin
These skills operationalize policies that ship to the child from datavidence-template-project.
A skill points to child-relative paths; it must not bundle or restate them:
- Rules: .claude/policies/health/*.md and .claude/policies/analysis/*.md
- Runnable gates: docs/health/checklists.md
- Shared notation + worked cases: docs/health/ascii-timelines.md, phenotyping-examples.md, indicator-scenarios.md
A skill that hard-codes a project name, a path outside the child contract, or a command is misplaced.

## 6. Generator is not auditor
For verification, a fresh cold-read context tries to refute, not confirm (it did not see the
generation reasoning). Scale adversarial depth to stakes (analysis/verification-effort.md): light = 1
auditor; standard = 3 voters; deep = 5 + synthesis with an anti-sycophancy concede-only-at-4-of-5
gate. Default light; escalate for published numbers and key conclusions.

## Using this file
Each SKILL.md references ../_shared/health-principles.md once (resolves as a plugin and when vendored
into .claude/skills/). Keep the per-skill body a thin verb: what to do, in order, with the gate it
runs and the artifact it returns; the why is here.

## 7. Output artifact format
A sizeable spec follows the shared convention in `../_shared/spec-artifact.md`: split-when-large into an
indexed `<spec-dir>/` directory plus an academic + executive `index.qmd` render (copied from the child
scaffold). Reference that file instead of restating the layout.
