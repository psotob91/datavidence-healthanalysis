---
name: specify-sensitivity-plan
description: >-
  Pre-specifies sensitivity analyses that probe the assumptions behind the
  primary analysis -- alternative case/exposure definitions, window choices,
  unmeasured-confounding via E-value and quantitative bias analysis, missing-data
  MNAR, and model-form alternatives -- each tied to the assumption it probes.
  Reuses the primary pipeline; flags post-hoc analyses. Use when the user asks
  to specify or plan sensitivity analyses, run a robustness check, compute an
  E-value, assess how robust the results are, vary the assumptions, or consider
  alternative specifications. Operationalizes analysis/sensitivity-analysis.md.
  NOT for framing the primary estimand (use frame-study); NOT for outlier handling
  (use review-outliers); NOT for running the analyses (that follows sign-off).
---

# /datavidence-healthanalysis:specify-sensitivity-plan

> Operationalizes `.claude/policies/analysis/sensitivity-analysis.md`. Apply
> `../_shared/health-principles.md` (math-by-tool, claim-to-evidence,
> PENDING_LOCAL_DECISION, comprehension-before-code) and emit the artifact per
> `../_shared/spec-artifact.md` -- a **simple artifact** (single focused
> sensitivity plan, optionally split when large).

## When to use / when NOT to use

- **Use it when:** the user wants to pre-specify sensitivity analyses alongside
  the primary analysis -- alternative definitions, window choices, unmeasured-
  confounding methods (E-value, QBA), missing-data MNAR probes, or model-form
  variants that reuse the primary pipeline.
- **Do NOT use it when:** the goal is to frame or redefine the primary estimand
  -- use `frame-study`; the goal is to identify or handle outlying observations
  -- use `review-outliers`; the analyses are already complete (flag any
  post-hoc sensitivity analysis explicitly -- see Step 6 below).

## What it does: the specification sequence (in order)

### Step 1 -- Confirm the primary analysis contract

Read `analysis/sap/` (or ask the user to share the primary SAP artifact from
`frame-study`). Confirm the primary estimand, method, and pipeline entry point
before listing any sensitivity analyses. If the primary SAP is not yet signed
off, return `PENDING_LOCAL_DECISION: primary SAP must be locked before the
sensitivity plan is written`.

### Step 2 -- Classify the analysis goal

From the primary SAP, identify the goal class, because the sensitivity
dimensions differ by goal (see policy `analysis/sensitivity-analysis.md`):

| Goal class | Core sensitivity dimensions |
|---|---|
| **Causal** | Unmeasured confounding (QBA, E-value, negative controls); exposure / case definition variants; selection bias probe |
| **Prediction** | Definition variants; missing-data handling; modeling method; internal-external validation |
| **Descriptive** | Case / exposure definition variants; standardization / weighting choices; MNAR / tipping-point |

Record the goal class in the plan header. If the goal class is ambiguous, ask.

### Step 3 -- Enumerate pre-specified sensitivity analyses

For each sensitivity analysis, specify five fields:

| Field | Content |
|---|---|
| **Label** | Short slug (e.g., `SA-01`) |
| **Assumption probed** | The assumption in the primary analysis this analysis stresses (one sentence) |
| **Change from primary** | Exactly what differs (definition, window, method, imputation model) |
| **Method** | Analysis method; must reuse the primary pipeline where possible |
| **Expected direction** | Direction of deviation if the assumption is violated (optional; mark PENDING if unknown) |

Minimum required analyses by goal class (from policy):

**Causal:**
- Alternative exposure definition (narrow vs broad; washout window variant).
- Alternative outcome / case definition (e.g., stricter / looser code list;
  reference `phenotype-gate` artifact for the base definition).
- **E-value** at both the point estimate and the CI limit nearest the null
  (compute via R `EValue` package or equivalent -- never mentally). Annotate
  that the E-value is a screening device, not a verdict; it ignores non-
  confounding bias and carries no "large enough" threshold.
- **Tipping-point / E-value for unmeasured confounding (named confounders):**
  identify the specific unmeasured confounders plausible in the study domain
  (e.g., smoking status in a cardiovascular analysis; SES in an occupational
  study) -- do not write "residual confounding" in the abstract. For each named
  confounder, compute the E-value or derive the bias-factor threshold that
  would shift the point estimate to the null. This slot is SEPARATE from the
  MNAR / missing-data tipping-point below.
- **QBA** (probabilistic preferred over single-value, per Lash, Fox et al.
  2021) for unmeasured confounding and, when relevant, misclassification or
  selection bias.
- Negative controls (if domain knowledge supplies a credible negative control
  outcome or exposure; reference `SA-NC` slot; mark PENDING if none identified).
- MNAR / tipping-point for missing data (reference `assess-missingness`
  artifact; mark PENDING if missingness assessment has not been run).

**Prediction:**
- Alternative predictor / outcome definitions.
- Alternative missing-data handling (vary imputation method or number of
  imputations; LOCF/BOCF are deprecated -- see policy).
- Bootstrap-corrected optimism vs alternative modeling method.
- Subgroup / calibration robustness.

**Descriptive:**
- Alternative case / exposure definition.
- Alternative standard population or weighting scheme.
- MNAR / tipping-point (same slot as causal).

For any analysis where a required choice is not yet made (window length,
code list version, bias-model parameters), record `PENDING_LOCAL_DECISION`
with the choice name. Do not invent a default.

### Step 4 -- Reuse gate

For each SA, confirm that it can run by modifying a parameter in the primary
pipeline (a flag, a filter argument, an imputation-model variant) rather than
forking code. If it cannot, note the deviation and explain the minimum change
required. Forks that duplicate code rather than parameterize it violate the
policy rule "reuse the pipeline".

### Step 5 -- Reporting plan

State that each sensitivity analysis will be reported alongside the primary
result: point estimate + CI on the same scale as the primary. Agreement
strengthens the primary; divergence is disclosed and interpreted, never buried.
Note where results tables will live (`analysis/results/sensitivity/`).

### Step 6 -- Post-hoc flag register

Any sensitivity analysis the user describes AFTER the primary results have
been examined must be recorded in the plan as `POST_HOC_ANALYSIS` with the
date flagged. Do not reclassify a post-hoc analysis as pre-specified.

### Step 7 -- Human sign-off

Present the sensitivity plan table; ask for explicit confirmation that every
pre-specified SA maps to a real assumption worth probing. Silence is not
consent. Mark the plan `LOCKED` with a date after sign-off.

## Output

Per `../_shared/spec-artifact.md` **simple artifact** convention:

``
analysis/sensitivity-plan/sensitivity-plan.md   # the pre-specified plan
analysis/sensitivity-plan/pending-decisions.md  # PENDING_LOCAL_DECISION register
``

`sensitivity-plan.md` contains, in order:

1. **Header** -- primary SAP reference path, goal class, plan status
   (DRAFT / LOCKED), lock date.
2. **Sensitivity analysis table** -- one row per SA, five columns per Step 3.
3. **Reuse confirmation** -- one paragraph per SA noting the pipeline
   modification required (parameter name or flag where known).
4. **Reporting plan** -- one sentence stating where results land.
5. **Post-hoc register** -- empty at draft time; populated if Step 6 fires.

If the plan exceeds ~300 lines (many SAs or large QBA design notes), split
into `sensitivity-plan/` directory with a `README.md` router per
`../_shared/spec-artifact.md`.

## Pairs with (repo policy)

- `.claude/policies/analysis/sensitivity-analysis.md` -- the binding rule.
- Prerequisite: `frame-study` (primary SAP must exist and be signed off).
- Prerequisite: `assess-missingness` (MNAR / tipping-point SAs require the
  missingness profile).
- Prerequisite: `phenotype-gate` (case / exposure definition variants
  reference the base phenotype artifact).
- Next: running the sensitivity analyses reuses the primary pipeline after
  the sensitivity plan is LOCKED.

## Boundary notes

- **vs frame-study:** `frame-study` defines the primary estimand and locks
  the SAP; `specify-sensitivity-plan` adds the pre-specified sensitivity
  analyses that run *alongside* the primary. Do not conflate them -- the
  primary estimand is never redefined here.
- **vs review-outliers:** outlier detection and handling is a data-quality
  step, not a sensitivity analysis. Route it to `review-outliers`.

## Rules / invariants

- **Pre-specified, not post-hoc.** Sensitivity analyses must be listed before
  results are examined; flag any post-hoc addition explicitly.
- **Reuse the pipeline.** Every SA runs via a parameterized variant of the
  primary pipeline; no code forks.
- **E-value at both anchors.** Always compute E-value at the point estimate
  AND at the CI limit nearest the null; annotate its limitations every time.
- **QBA over single-value.** Probabilistic QBA is preferred for unmeasured
  confounding; single-value bias analysis is acceptable only as a supplement.
- **Report alongside primary.** Divergence is disclosed, not buried.
- **PENDING_LOCAL_DECISION, never a silent default.** Unresolved window, code
  list, or bias-model choices are stop-signals, not defaults.
- **Math by tool.** E-values and QBA parameters come from code output
  (`EValue` package or equivalent), not model reasoning.