---
name: method-audit
description: >-
  Orchestrates a voting panel of three independent reviewers (methodologist, statistician,
  reporting-reviewer) to audit the methods of a health-data analysis. Fans out cold-read
  evaluation across study-design validity, statistical correctness, and EQUATOR/reporting
  adherence; synthesizes a structured verdict; applies an anti-sycophancy gate. Use when
  the user asks to audit the methods, review the analysis (methods not results), check
  whether this analysis is sound, run a method audit, or request a methodological review.
  Pairs with analysis/verification-effort.md. NOT for results interpretation, data
  cleaning, or generating new analyses.
---

# /datavidence-healthanalysis:method-audit

> Operationalizes the `method-audit` orchestration described in `docs/DEVELOPMENT_GUIDE.md §5`
> and the child's `analysis/verification-effort.md`. Apply `../_shared/health-principles.md`
> (math-by-tool, claim-to-evidence, generator-is-not-auditor). Fan-out + synthesis happens here;
> each reviewer subagent is isolated.

## When to use / when NOT to use
- **Use**: user asks for methods audit, analysis review (methods, not results), soundness check,
  method audit, or methodological review of an existing analysis.
- **Do NOT use**: results interpretation (that is a different scope), data cleaning, producing new
  analyses, reviewing a literature source (no analysis files in scope), or reviewing code style only.

## Step 0 — Scope and depth
1. Identify the analysis files to audit: scripts (`analysis/`, `R/`), protocol/SAP, manuscript draft,
   tables. If none are named, ask the user to specify.
2. Determine depth from context or by asking:
   - **light** (exploratory / internal check) → spawn **1** reviewer (methodologist by default).
   - **standard** (pre-submission / peer-review prep) → spawn all **3** reviewers in parallel.
   - **deep** (publication numbers / key conclusions) → spawn all **3** reviewers in parallel + a
     synthesis pass; apply the full anti-sycophancy gate (concede only at evidence ≥4/5).
   Default = **light** unless the user names a publication, peer review, or high-stakes context.

## Step 1 — Fan-out (independent, parallel)
Spawn reviewers independently (no shared context between them):
- `methodologist` → study-design validity (estimand, DAG/confounding, immortal-time, selection bias,
  target-trial, transportability).
- `statistician` → statistical correctness (model vs estimand, assumptions, missing data, multiplicity,
  no-dichotomizing, calibration/discrimination for prediction, design-based variance for surveys).
- `reporting-reviewer` → EQUATOR/reporting adherence (guideline selection, checklist completeness,
  no-p-values-in-Table-1, flow-diagram count reconciliation, labels/units).

Each reviewer returns a set of structured verdicts:
```
FINDING:        <one-line>
SEVERITY:       critical | major | minor | informational
EVIDENCE:       <file:line or EQUATOR item>
RECOMMENDATION: <actionable fix>
```

## Step 2 — SubagentStop gate (before folding results)
Before folding any reviewer's output back, verify:
- [ ] No secrets or patient-identifiable data appear in the output.
- [ ] Reviewer made no writes to the analysis tree.
- [ ] Every asserted number was tool-computed (not stated as mental computation).
If any check fails, discard that reviewer's output and flag it.

## Step 3 — Synthesis (standard and deep only)
Collect all passing verdicts. For each unique finding topic:
1. Note whether multiple reviewers flagged it (convergence = higher confidence).
2. Assign final severity = worst across reviewers for that topic.
3. For **deep**: if a reviewer's finding is challenged in the synthesis, score the challenge 1–5;
   concede only at ≥4. State the score explicitly.

Produce a **Panel Verdict** with:
- An ordered finding table (critical → major → minor → informational).
- Convergence flags (which reviewers agreed).
- Overall soundness rating: **sound** / **conditionally sound** / **major revisions needed** /
  **do not proceed**.
- Every number in the verdict tool-computed (delegate to executor/R or WolframAlpha MCP); cite
  the output, never assert mentally.

## Step 4 — /cross-examine (optional, deep only)
For deep audits or if the user requests adversarial follow-up, route contested findings through
the generic `/cross-examine` machinery (psotobverse-utils). Pass the finding + evidence anchor;
the cross-examiner attempts refutation; apply the ≥4/5 concede gate.

## Output format
Emit the Panel Verdict as a fenced block:

```
## Method Audit — Panel Verdict

Depth: light | standard | deep
Reviewers: <list spawned>
Files audited: <list>

### Findings

| # | Finding | Severity | Reviewer(s) | Evidence | Recommendation |
|---|---------|----------|-------------|----------|----------------|
| 1 | ...     | critical | methodologist, statistician | file:line | ... |
...

### Overall soundness: <rating>
<1-2 sentence rationale anchored to the critical/major findings above>
```

## Invariants (from `../_shared/health-principles.md`)
- Math by tool: no number, count, percentage, or rate computed mentally.
- Claim to evidence: every finding anchored to file:line or EQUATOR item number.
- Generator is not auditor: reviewers read cold (no generation context shared with them).
- Anti-sycophancy: concede only at evidence ≥4/5; score stated explicitly.
- Methodology lives in the child: point to child-relative paths; never hard-code project names.
