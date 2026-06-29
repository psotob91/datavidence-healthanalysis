---
name: assess-missingness
description: >-
  Profiles missingness in a health dataset, reasons about the missing-data mechanism
  (MCAR / MAR / MNAR), proposes a handling strategy matched to the analysis goal
  (multiple imputation via mice, MMRM for longitudinal continuous endpoints, or
  confirmed-MCAR complete-case), and drafts a pre-specified MNAR sensitivity plan.
  Applies to any stage where missing values, NA patterns, imputation strategy,
  MICE setup, or MCAR/MAR/MNAR reasoning is at stake.
  Use when the user asks about missing data, missingness patterns, NA values,
  imputation, multiple imputation, MICE, MCAR, MAR, MNAR, how to handle missing,
  or whether complete-case analysis is appropriate.
  NOT for generic schema or referential-integrity validation -- use validate-data-contract for that.
  Operationalizes analysis/missingness.md.
---

# /datavidence-healthanalysis:assess-missingness

> Operationalizes `.claude/policies/analysis/missingness.md`. Apply
> `../_shared/health-principles.md` (math-by-tool, claim-to-evidence,
> PENDING_LOCAL_DECISION) and emit the report per `../_shared/spec-artifact.md`
> (single focused document + optional small render for the R stack).

## Boundary vs run-ida

This skill is the full standalone missingness analysis (mechanism reasoning, imputation
strategy, MNAR sensitivity plan). run-ida's Domain 2 is only a scoped IDA screen
(counts and patterns) -- it is not a substitute for this skill.

## When to use / when NOT to use

- **Use it when:** the user asks about missing data in a dataset -- patterns, extent,
  mechanism (MCAR/MAR/MNAR), imputation approach, MICE configuration, or sensitivity
  to MNAR; or when a descriptive, causal, or prediction analysis needs a pre-specified
  missingness strategy before coding begins.
- **Do NOT use it when:** the task is schema validation, type checking, or
  referential-integrity auditing -- those belong to `validate-data-contract`. A useful
  heuristic: if the question is "are these values missing?" that is assess-missingness;
  if the question is "do these columns exist and have the right type?" that is
  validate-data-contract.

## What it does: detect -> inspect -> reason -> handle (in order, no skipping)

Produce the four sections below, then surface any PENDING_LOCAL_DECISION items for
human resolution before code is written.

### 1. Missingness profile (detect + inspect)

Delegate all numeric work to R/naniar code (math-by-tool). The profile covers:

- **Per-variable completeness:** N and % missing per column; flag variables above
  the project missingness threshold (default PENDING_LOCAL_DECISION -- the child
  protocol sets it; do not invent a number).
- **Co-missingness / shadow matrix:** identify variables that tend to be missing
  together (e.g. `naniar::gg_miss_upset` or `vis_miss`); name every cluster.
- **Row-level accounting:** report N at each pipeline stage and explain every dropped
  or excluded record -- a reconciled flow, not a vanishing count. Account for every row.
- **Subgroup completeness:** where the SAP specifies subgroups (by site, time period,
  exposure arm, or covariate), report completeness within each.

Never hide missingness; always surface it in the descriptive output.

### 2. Mechanism reasoning (MCAR / MAR / MNAR)

State the assumed mechanism for each variable or cluster and give a reasoned
justification -- not a label without a why. Apply the following decision logic:

| Mechanism | What it means | Testable signal | Policy implication |
|---|---|---|---|
| MCAR | Missing completely at random -- no relationship to observed or unobserved data | Little's MCAR test (indicative only, not sufficient); missingness uncorrelated with any observed variable | Complete-case valid only if loss is minimal AND mechanism is confirmed; cite evidence |
| MAR | Missingness is explained by observed data (conditionally random given covariates) | Missingness associated with observed covariates but not with unobserved values | Multiple imputation (mice, M >= 20, pmm for non-normal); MMRM for longitudinal continuous |
| MNAR | Missingness depends on the unobserved value itself | Cannot be proven from data alone; must rely on domain knowledge + sensitivity analysis | MNAR => pre-specified sensitivity (reference-based MI or tipping-point); best/worst single imputation is deprecated |

For MNAR: if domain knowledge makes MNAR plausible (e.g. a lab value missing because
it is out of range, a hospitalization record absent because of care-avoidance), name
the mechanism explicitly, do not default to MAR, and flag PENDING_LOCAL_DECISION for
the MNAR sensitivity parameters.

### 3. Handling proposal

Match the method to the mechanism and the analysis goal:

- **Descriptive analysis:** for prevalence, incidence, or means meant to generalize,
  use MI or IP weighting -- not complete-case (unbiased only under MCAR). Report
  completeness and, where feasible, both complete-case and MI estimates.
- **Causal analysis:** the imputation model must be congenial with the substantive
  model -- include exposure, outcome, all confounders, and any interactions/splines in
  the same form. Use SMC-FCS when the analysis model has interactions or splines.
  Impute missing confounders (do not drop them). Impute the outcome with caution
  ("impute then delete") and always run an MNAR sensitivity analysis -- MAR-based MI
  alone is not sufficient. Basis: Sterne et al. BMJ 2009; White, Royston and Wood
  Stat Med 2011; Bartlett et al. (SMC-FCS) Stat Methods Med Res 2015.
- **Prediction:** match development-time and deployment-time handling. The deployed
  model must return a prediction for a single new patient with missing predictors
  without using the outcome or post-baseline data. Use pattern submodels or
  deployment-ready conditional imputation. The missing-indicator method is defensible
  in prediction only if the missingness mechanism is stable between development and
  deployment; flag PENDING_LOCAL_DECISION if stability is uncertain. Basis: Hoogland
  et al. Stat Med 2020; Sisk et al. Stat Methods Med Res 2023; Steyerberg 2019.
- **Longitudinal continuous endpoint with MAR dropout:** use MMRM -- it handles MAR
  dropout without explicit imputation. LOCF / BOCF / WOCF are deprecated; do not use.
- **mice configuration (when MI applies):** M >= 20 (the package default of 5 is too
  few); `pmm` for non-normal continuous variables; include the analysis model right-
  hand side plus auxiliary variables with >= 0.4 correlation with either the incomplete
  variable or its missingness indicator; pool with Rubin's rules.
- **Complete-case:** only if mechanism is confirmed MCAR AND loss is minimal. Requires
  explicit justification; silence is not justification.

LOCF, BOCF, WOCF, and best-/worst-case single imputation are deprecated.
Do not propose them.

### 4. Sensitivity plan (for MNAR)

When MNAR is plausible for any variable, pre-specify a sensitivity analysis before
results are reported:

- **Reference-based MI (primary MNAR tool):** use the `rbmi` package; specify the
  reference arm and the departure assumption (jump-to-reference, copy-reference,
  copy-increments-in-reference). The departure parameters require
  PENDING_LOCAL_DECISION from the local protocol or SAP.
- **Tipping-point analysis:** vary the MNAR departure parameter (delta) over a
  clinically plausible range and identify the threshold at which the primary conclusion
  reverses. Report this threshold alongside the primary result.
- Sensitivity scope: at minimum cover the primary endpoint and any missing confounder
  for which MNAR is mechanistically plausible.

## Rules / invariants

- **Account for every row.** N must reconcile from raw input to analytic dataset;
  every exclusion is explained.
- **Detect -> inspect -> reason -> handle, in order.** Never jump to a handling method
  without first profiling patterns and reasoning about mechanism.
- **No silent listwise deletion.** Complete-case requires explicit MCAR evidence and
  minimal loss; document both.
- **MNAR => pre-specified sensitivity.** If MNAR is plausible, the sensitivity plan is
  part of the deliverable, not optional.
- **PENDING_LOCAL_DECISION, never a silent default.** Thresholds (% missing cutoff,
  M for mice, delta range for tipping-point, MMRM covariance structure) that the child
  protocol has not set are named PENDING_LOCAL_DECISION, not guessed.
- **Math by tool.** All counts, percentages, and test statistics are produced by R
  code; no arithmetic in model output.

## Output

Emit a focused missingness report (simple artifact per `../_shared/spec-artifact.md`):

- **R stack (typical):** one `analysis/missingness/<dataset>-missingness-report.md`
  covering the four sections above, plus a companion
  `analysis/missingness/<dataset>-missingness.R` (or `.qmd`) with the naniar profile
  code and mice setup skeleton. If the report grows beyond ~300 lines, split into
  `01-profile.md`, `02-mechanism.md`, `03-handling.md`, `04-sensitivity.md` with a
  README router.
- **Non-R stack:** the `.md` report only; no `.qmd`.
- Include a PENDING_LOCAL_DECISION register at the end of the report listing every
  open choice (threshold, M, delta range, covariance structure, departure assumption).
- After human resolution of all PENDING items, update the report status to LOCKED and
  proceed to the imputation code.

Runnable imputation code (the `mice()` call, the MMRM model, the `rbmi` sensitivity
run) is withheld until the mechanism reasoning and handling proposal are confirmed by
the analyst -- silence is not consent. An R skeleton (structure only, no pooled
output) may be shown earlier to illustrate the proposed approach.

## Pairs with (repo policy)

- `.claude/policies/analysis/missingness.md` (the authoritative rule).
- **Next-if longitudinal continuous endpoint with MAR dropout:** `analysis/longitudinal-data.md`
  and the MMRM path.
- **Next-if prediction model:** revisit deployment-time handling in
  `analysis/prediction-modelling.md` after this skill completes.
- **Prior-if:** `validate-data-contract` (schema + referential integrity) runs before
  this skill; a clean contract is a precondition for a meaningful missingness profile.