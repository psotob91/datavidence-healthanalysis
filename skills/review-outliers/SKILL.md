---
name: review-outliers
description: >-
  Detects, inspects, documents, and runs sensitivity analyses for outliers and
  implausible values in health datasets. Invokes for phrases such as: outliers,
  extreme values, implausible values, anomalies, winsorize, should I remove
  this point, flag extreme observations, screen for data errors. Follows a
  four-phase cycle — DETECT → INSPECT → DOCUMENT → SENSITIVITY — governed by
  the analysis/outliers policy. Distinguishes data errors (may be corrected)
  from genuine extremes (keep with justification) and marks unresolved choices
  PENDING. Does NOT cover missingness (use assess-missingness) or post-fit
  model-influence diagnostics (use validate-assumptions, though this skill
  complements it by flagging influential extreme values before modeling).
allowed-tools: Read Write Grep Glob Bash(Rscript *) Bash(python *) Bash(python3 *)
---

# /datavidence-healthanalysis:review-outliers

Implements the four-phase outlier workflow from `template/.claude/policies/analysis/outliers.md`.
Consult `../_shared/health-principles.md` for domain defaults and
`../_shared/spec-artifact.md` for the record format.

## When to use / when NOT to use

- Use when: screening variables for extreme or implausible values; deciding
  whether to remove, cap, impute, or keep a suspect observation; preparing a
  sensitivity analysis that compares results with and without an outlier;
  reporting robust summaries for skewed data.
- Do NOT use for: missing-data patterns or rates → `assess-missingness`.
- Do NOT use for: post-fit leverage / Cook's distance / DFBETA on a fitted
  model → `validate-assumptions` (this skill surfaces the raw candidates;
  validate-assumptions judges their influence on estimates).

## What it does (the procedure)

### Phase 1 — DETECT (distribution-aware)

1. Read the analysis goal from the user or the project data contract
   (`contracts/`). The detection rule must match the goal:
   - **Description:** MAD-based z-score (`|x − median| / (1.4826 · MAD) > 3.5`,
     Leys 2013), Tukey fences (1.5 × IQR), or Grubbs test (`outliers::grubbs.test()`)
     for a single suspected outlier in a near-normal variable. Never use mean ± k·SD
     -- SD is inflated by the very values being flagged.
   - **Causal / prediction:** use the same MAD/IQR screen as a flag; final
     handling is goal-specific (see Phase 2).
   - **Multivariate:** Mahalanobis distance or Local Outlier Factor when
     individual-variable screens are insufficient.
2. Pre-specify thresholds in a comment block before running detection code.
   Never tune thresholds after seeing which observations they flag.
3. Output a flagged-observations table: `outputs/outliers/flagged.csv`
   (columns: `id`, `variable`, `value`, `flag_rule`, `flag_value`).

### Phase 2 — INSPECT each flagged observation

For every flagged row, determine which category applies:

| Category | Definition | Default handling |
|---|---|---|
| **Data error** | Biologically/logically impossible (e.g., age = 300, SBP = 0) or transcription artefact confirmed by source check | Correct if source allows; otherwise set missing with audit trail |
| **Implausible but correctable** | Outside reference range; source record available to verify | Verify against source; correct or set PENDING |
| **Valid extreme** | Physiologically possible rare value; no evidence of error | Keep; report in sensitivity |
| **Undecidable** | Insufficient information to classify | Mark PENDING; do not remove |

Goal-specific rules (from policy):

- **Causal:** assess influence on the **exposure coefficient** (DFBETA /
  standardized DFBETAS), not on overall fit. Flag to validate-assumptions.
  Never drop to push a coefficient across significance. Under heavy tails,
  prefer robust regression (`MASS::rlm`) or quantile regression (`quantreg`)
  over deletion.
- **Prediction:** assess impact on calibration and discrimination.
  Winsorizing/transforming predictors is acceptable when thresholds are learned
  on development data only and frozen for deployment (Steyerberg 2019;
  Harrell RMS 2015).
- **Description:** prefer robust summaries (median & IQR, trimmed/winsorized
  means with fraction stated). Genuine extremes are part of the distribution —
  report, do not remove.

### Phase 3 — DOCUMENT every decision

Write one record per flagged observation to `outputs/outliers/decisions.yml`
using the spec-artifact format from `../_shared/spec-artifact.md`:

```yaml
- id: <row_id>
  variable: <variable>
  value: <raw_value>
  flag_rule: <rule used>
  category: data_error | implausible | valid_extreme | undecidable
  action: corrected | set_missing | kept | winsorized | PENDING
  justification: >-
    <one sentence — basis for the decision>
  analyst: <initials>
  date: <ISO date>
```

PENDING entries block downstream analysis steps that depend on the variable
until resolved. Never silently remove any observation.

### Phase 4 — SENSITIVITY (unconditional)

Whenever any value is excluded or modified:

1. Run the primary analysis twice: with the original value and with the
   modified/excluded value.
2. Compare key estimates (effect sizes, summary statistics, model performance).
3. Write results to `outputs/outliers/sensitivity.md` with a table:
   `estimand | with_outlier | without_outlier | delta | conclusion`.
4. If results differ materially, escalate to the analyst and report both
   versions in the deliverable. Do not choose the version that looks better.

## Pairs with (repo policy)

- Operationalizes `template/.claude/policies/analysis/outliers.md`.
- Complements `validate-assumptions` (post-fit influence) — this skill runs
  BEFORE fitting; validate-assumptions runs AFTER.
- Complements `assess-missingness` — when a data error is set missing here,
  assess-missingness governs its subsequent handling.

## Rules / invariants

- Pre-specify detection thresholds; never tune after seeing flagged rows.
- NEVER silently remove an observation — every action requires a decision record.
- PENDING is a valid output; leave it rather than forcing a premature decision.
- Sensitivity analysis is unconditional whenever any value is removed or modified.
- Delegate all computation to R or Python — never compute distribution
  statistics mentally.
- Anchor every decision to `file:line` or a reproducible script output.
- Read `../_shared/health-principles.md` before modifying domain-specific
  plausibility thresholds (e.g., clinical ranges for vital signs).

## Output

- `outputs/outliers/flagged.csv` — detection results.
- `outputs/outliers/decisions.yml` — one record per flagged observation.
- `outputs/outliers/sensitivity.md` — with/without comparison (when applicable).
- Inline summary to the analyst: counts by category, unresolved PENDING items,
  any material sensitivity finding.
