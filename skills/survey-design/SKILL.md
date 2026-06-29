---
name: survey-design
description: >-
  Declares and builds a complex-survey design object (weights, strata, PSU/clusters,
  FPC) with `survey::svydesign` or `srvyr::as_survey_design`, applies design-based
  estimators (svymean, svyby, svyglm, svyciprop), handles subpopulation estimation
  via subset() of the design object, and reports the design effect (DEFF). Use when
  the user mentions survey weights, complex survey, sampling weights, svydesign,
  strata, PSU, clusters, design effect, post-stratification, ENDES, DHS, ENAHO, or
  any nationally representative household survey. Operationalizes design-based
  inference for weighted/stratified/clustered samples; NOT for cohort or claims data
  where observations are i.i.d. or near-i.i.d. (use specify-regression for those).
  The boundary: if svydesign or srvyr is the right object, this skill owns it;
  otherwise it does not.
---

# /datavidence-healthanalysis:survey-design

> Operationalizes design-based inference for complex-survey data. Apply
> `../_shared/health-principles.md` (math-by-tool, claim-to-evidence,
> PENDING_LOCAL_DECISION, comprehension-before-code) throughout. For sizeable
> design specs emit the artifact per `../_shared/spec-artifact.md` (simple
> artifact: a single survey-design-spec document + optional stub). This gate runs
> BEFORE any estimates are computed; runnable analysis code is withheld until
> sign-off.

## When to use / when NOT to use

- **Use it when:** the data come from a complex sample (stratified + clustered +
  probability weights) and inference must be design-based -- ENDES, DHS, ENAHO,
  STEP, any national household or health survey that ships a sampling manual.
- **Do NOT use it when:** the analysis assumes i.i.d. observations (cohort,
  registry, RCT, administrative claims without a survey design) -- use
  `specify-regression` or `frame-study` for those. Also do not use for
  simple weighted means where no design-based variance is needed (unusual).

## What it does: the design protocol (in order, no skipping)

### Step 1 -- Identify design elements

Collect the four required elements from the survey documentation or data
dictionary. Mark any unconfirmed element `<<PENDING_CONFIRMATION>>`:

| Element | Typical variable name | Note |
|---|---|---|
| Sampling (analysis) weight | `factor_pond`, `wt`, `pwt` | Final post-stratified weight; confirm if multiple weight columns exist |
| Stratum identifier | `estrato`, `stratum`, `strata` | Sampling stratum -- NOT a substantive grouping variable |
| PSU / cluster identifier | `conglome`, `psu`, `cluster_id` | Primary sampling unit; needed for Taylor linearization variance |
| FPC (finite-population correction) | Survey manual | Optional; omit when sampling fraction << 5%; <<PENDING_CONFIRMATION>> if unclear |

If the survey provides replicate weights (bootstrap, BRR, Jackknife) instead of
PSU+stratum, note that `survey::svrepdesign` is the correct constructor --
<<PENDING_CONFIRMATION>> on which variance method the survey manual specifies.

### Step 2 -- Distinguish analysis weights from sampling weights

Confirm that the weight variable is the **final analysis weight** (post-
stratified, calibrated), not a raw sampling weight. If only a raw sampling weight
exists and calibration targets are available, flag the calibration gap as
`PENDING_LOCAL_DECISION`. Never silently use raw sampling weights as final
analysis weights.

### Step 3 -- Declare the design object

Produce pseudocode (language-agnostic) for the design declaration. Runnable R
code is withheld until sign-off:

```
# Pseudocode -- not runnable until sign-off
LOAD survey data as df
CONFIRM df has columns: <weight_var>, <strata_var>, <psu_var>
DECLARE design = svydesign(
  ids     = ~<psu_var>,         # PSU; ~1 if no clustering <<PENDING_CONFIRMATION>>
  strata  = ~<strata_var>,      # NULL if unstratified <<PENDING_CONFIRMATION>>
  weights = ~<weight_var>,
  data    = df,
  nest    = TRUE                # PSUs nested within strata (standard for ENDES/DHS)
)
# srvyr wrapper for tidy-style syntax (same design object, optional):
DECLARE svy = df |> as_survey_design(
  ids = <psu_var>, strata = <strata_var>, weights = <weight_var>, nest = TRUE
)
```

Confirm `nest = TRUE` only when PSU IDs are reused across strata (DHS/ENDES
convention). If PSU IDs are globally unique, `nest = FALSE` is correct --
<<PENDING_CONFIRMATION>>.

### Step 4 -- Verify design integrity

Before any estimates, specify the integrity checks (code withheld; describe them
here):

1. `summary(design)` -- confirm strata count, PSU count, and weight distribution.
2. Check for singleton PSUs (one PSU per stratum): these make Taylor-linearization
   variance undefined; apply `options(survey.lonely.psu = "adjust")` or `"remove"`
   -- `PENDING_LOCAL_DECISION` on which option is appropriate.
3. Compare total weighted N to a known population target (census or survey report).
   A large discrepancy signals a weight-normalization issue.
4. Report effective sample size: n_eff = (sum(weights))^2 / sum(weights^2).

### Step 5 -- Apply design-based estimators

Design-based estimators operate on the design object, never on the raw data frame:

| Task | Correct function | Common mistake to avoid |
|---|---|---|
| Weighted mean / proportion | `svymean()`, `svyciprop()` | `mean(df$x * df$wt)` (ignores clustering) |
| Domain / subgroup mean | `svyby(~x, ~domain, design, svymean)` | Filtering df before svydesign |
| Tabulation | `svytable()` | `table()` on unweighted data |
| Regression | `svyglm(y ~ x, design)` | `glm(y ~ x, data=df, weights=wt)` (underestimates SE) |
| Quantiles | `svyquantile()` | `quantile()` on weighted data |

All numeric results come from R output, never from mental arithmetic (see
`../_shared/health-principles.md` Section 1).

### Step 6 -- Subpopulation (domain) estimation -- critical rule

**Never filter the data frame before passing it to `svydesign`.**
Subpopulation estimates must use `subset()` applied to the design object after
construction:

```
# CORRECT
sub_design = subset(design, region == "Lima")
svymean(~hb, sub_design)

# WRONG -- breaks variance estimation (removes PSUs from other strata)
df_lima = df[df$region == "Lima", ]
design_wrong = svydesign(..., data = df_lima)
```

State this rule explicitly in any analysis plan that involves subgroups.

> **`svyby()` vs `subset()` -- distinct uses:** `svyby(~x, ~domain, design, svymean)`
> produces by-group summaries across the whole design (reporting by groups);
> `subset(design, domain == "Lima")` targets a specific subpopulation for inference
> (the target IS a subgroup, not a presentation breakdown). Use `subset` when the
> estimand is defined only for that subpopulation.

### Step 7 -- Report design effect (DEFF)

For every primary estimate report the design effect:
DEFF = Var_design(estimate) / Var_SRS(estimate).

In R: pass `deff = TRUE` to `svymean()` to return DEFF alongside the estimate.
Flag DEFF > 2 as a note in the spec (substantial clustering or stratification
impact on precision). DEFF is a diagnostic, not a disqualifier.

### Step 8 -- Post-stratification (if applicable)

If the analysis plan requires post-stratification to external control totals
(census marginals), describe the approach in pseudocode:

```
# Pseudocode
ps_design = postStratify(design, strata = ~sex + age_group, population = <pop_totals>)
# or raking (iterative proportional fitting):
rk_design = rake(design,
                 sample.margins = list(~sex, ~age_group),
                 population.margins = list(<sex_totals>, <age_totals>))
```

Confirm population control totals are available and cite the source
(<<PENDING_CONFIRMATION>> if unknown). `PENDING_LOCAL_DECISION` on whether full
post-stratification or raking is required.

### Step 9 -- Human sign-off

Present the complete design spec: weight variable confirmed, strata and PSU
variables identified, `nest` flag rationale, singleton-PSU option chosen,
FPC decision, and all PENDING items. Request explicit confirmation. Silence is
not consent. Estimation and fitting code are withheld until sign-off.

### Step 10 -- After sign-off

Flip the spec status badge to `LOCKED`. Emit the R design stub (declaration +
integrity checks) for use in the analysis pipeline. Any subsequent change to
design elements must be documented as a dated amendment.

## Pairs with (repo policy)

- `.claude/policies/analysis/survey-inference.md` -- binding rule if present in
  the child project (states the no-filter, subset-only, DEFF-reporting rules).
- Prerequisites: data contract confirmed (`validate-data-contract`); weight
  variable identified in the data dictionary (`onboard-data`).
- Next: `specify-regression` if a `svyglm` model is needed post-declaration;
  `design-indicator` for deriving new indicators from the survey variables.

## Rules / invariants

- **Never filter before declaring the design**: subpopulation estimates must use
  `subset(design, ...)`, not `data[condition, ]` piped into `svydesign`.
- **Design-based estimators only**: use `svymean`, `svyby`, `svyglm`, etc. --
  never pass a `weights=` argument to `lm`/`glm` on complex-survey data and
  report those SEs (they underestimate variance under clustering).
- **Distinguish analysis weights from sampling weights**: confirm the weight
  variable is the final post-stratified weight; flag calibration gaps as
  `PENDING_LOCAL_DECISION`.
- **Report DEFF**: always include the design effect for primary estimates.
- **Math by tool**: all weighted counts, means, proportions, and SEs come from
  R + `survey`/`srvyr` output, never from mental arithmetic.
- **PENDING_CONFIRMATION for every unconfirmed design element**: PSU ID,
  stratum ID, `nest` flag, FPC, replicate-weight vs. PSU+stratum -- if the
  survey manual has not confirmed it, mark it.
- **Singleton PSU requires an explicit decision**: `options(survey.lonely.psu)`
  must be set explicitly; leave as `PENDING_LOCAL_DECISION` if the choice is
  unresolved.

## Output

Per `../_shared/spec-artifact.md` **simple artifact** convention:

```
analysis/survey-design/<survey-slug>-design-spec.md   # declared design + decisions
analysis/survey-design/<survey-slug>-design-stub.R    # R pseudocode stub (after sign-off)
build/pending-decisions.md                            # PENDING register
```

The spec document contains, in order:

1. **Design header** -- survey name, reference year, sampling manual citation,
   status badge (DRAFT / LOCKED).
2. **Design element table** -- weight variable, strata variable, PSU variable,
   FPC decision, `nest` flag -- each with source and status
   (confirmed / <<PENDING_CONFIRMATION>>).
3. **Integrity check plan** -- `summary()` targets, effective N formula,
   weighted N vs. population target check.
4. **Singleton PSU decision** -- option chosen and rationale.
5. **Post-stratification plan** -- control totals source, method (full PS or
   raking), `PENDING_LOCAL_DECISION` if unresolved.
6. **DEFF report plan** -- which primary estimates will include DEFF.
7. **PENDING register** -- one entry per unresolved design element or decision.