---
name: specify-regression
description: >-
  Specifies a regression model UP FRONT -- selects the model family and link
  function, pre-specifies predictors and confounders from the DAG or subject
  knowledge, models continuous variables with restricted cubic splines, detects
  sparse-data bias and separation, applies penalization when indicated, and
  emits a signed-off model spec before any fitting. Use when the user asks to
  specify a regression, model the outcome, adjust for confounders, which
  covariates to include, build the regression model, or perform variable
  selection. Operationalizes analysis/regression-modeling.md and
  analysis/collinearity.md. NOT for post-fit diagnostics (use
  validate-assumptions); NOT for estimand framing or SAP authoring (use
  frame-study).
---

# /datavidence-healthanalysis:specify-regression

> Operationalizes `.claude/policies/analysis/regression-modeling.md` and
> `.claude/policies/analysis/collinearity.md`. Apply
> `../_shared/health-principles.md` (math-by-tool, claim-to-evidence,
> PENDING_LOCAL_DECISION, comprehension-before-code) and emit the artifact
> per `../_shared/spec-artifact.md` (simple artifact: single model-spec
> document + optional stub). This gate runs BEFORE any model is fit; runnable
> fitting code is withheld until sign-off.

## When to use / when NOT to use

- **Use it when:** the user wants to pre-specify a regression model -- choosing
  the family, link function, covariates, functional forms for continuous
  predictors, confounder adjustment strategy, and remedies for sparse data --
  before any fitting is done.
- **Do NOT use it when:** a model has already been fit and diagnostics are
  needed -- use `validate-assumptions`; the goal is defining the estimand,
  population, or SAP skeleton -- use `frame-study`. This skill specifies the
  fit; those skills frame or diagnose it.

## What it does: the specification protocol (in order, no skipping)

### Step 1 -- Confirm prerequisites

Verify that `frame-study` has been completed and the estimand is LOCKED. If
not, pause and direct the user there first -- a model cannot be pre-specified
without a defined estimand. Check that IDA (`run-ida`) has been completed;
IDA informs functional-form and sample-size decisions.

### Step 2 -- Select model family and link function

Identify the outcome type and select the appropriate family:

| Outcome type | Default family / link | Notes |
|---|---|---|
| Continuous, approx. normal | Gaussian / identity (OLS) | Check IDA for skew; consider log-link or transform |
| Binary | Binomial / logit (logistic) | Separation risk when outcome is rare or predictors are strong |
| Count (Poisson) | Poisson / log; quasi-Poisson if overdispersed | Check dispersion in IDA |
| Count (overdispersed) | Negative-binomial (`glmmTMB`, MASS) | Prefer over quasi for AIC / formal tests |
| Time-to-event | Cox PH; parametric (`survreg`) if PH unwarranted | PH assumption check deferred to validate-assumptions |
| Clustered / repeated | GLMM (`lme4`, `glmmTMB`) or GEE | Declare random-effects structure |
| Ordinal | Proportional-odds (`MASS::polr`, `rms::lrm`) | Check proportionality assumption post-fit |

Mark any undecided choice `PENDING_LOCAL_DECISION`. State the rationale for
the chosen family in the spec.

### Step 3 -- Pre-specify predictors and confounders

Covariates MUST be pre-specified from the DAG or subject-matter knowledge, NOT
selected from the data. Enumerate every variable that will enter the model:

- **Exposure / treatment**: the primary estimand variable.
- **Confounders**: variables required by the DAG to block backdoor paths; list
  each with the DAG path it blocks. Do not drop a confounder to simplify the
  model or lower a VIF -- that re-introduces confounding.
- **Precision variables**: non-confounders that reduce residual variance (e.g.,
  strong prognostic covariates); flag if inclusion is debated.
- **Forced exclusions**: variables excluded on subject-matter grounds (e.g.,
  mediators, colliders); state the reason for each.
- **Not allowed**: stepwise / automated selection for causal or
  prognostic-factor tasks. If a penalized-selection approach (LASSO / elastic
  net, CV-tuned) is needed for an exploratory task, declare it as exploratory
  and record it in `build/pending-decisions.md`; do not mix with a
  pre-specified confirmatory model.

Mark any covariate whose inclusion is unresolved `PENDING_LOCAL_DECISION`.

### Step 4 -- Specify functional forms for continuous predictors

Do NOT dichotomize or coarsely categorize continuous predictors. For each
continuous variable (predictors AND continuous confounders):

- **Default**: restricted cubic splines (RCS), pre-specifying the number of
  knots (3-5) and knot placement (default: Harrell quantiles). Use `rms::rcs`
  (R) or equivalent.
- **Alternative**: fractional polynomials (`mfp` package, FP2 default), if
  pre-specified before data inspection.
- **Assumed linear**: state the subject-matter justification; linearity is not
  a default.
- For confounders: flexible functional form is required to avoid residual
  confounding even when the shape is uninteresting (Groenwold et al., CMAJ
  2013; Becher, Stat Med 1992).

Record knot count and placement for each continuous variable in the spec.

### Step 5 -- Assess sample size and events-per-variable

Compute or request the available events (or observations for continuous
outcomes) and the number of parameters to be estimated:

- **Binary / survival**: events-per-variable (EPV). The 10 EPV rule is
  outdated; use `pmsampsize` (Riley et al. 2019) for prediction models. For
  causal / etiologic models, flag EPV < 10 as a sparse-data risk.
- **Sparse data and separation**: when EPV is low, when outcome is rare, or
  when a predictor strongly separates the outcome, ML estimates are biased away
  from the null (Greenland et al., BMJ 2016). Detect via: implausibly large
  ratios, instability on covariate addition/removal, zero cells. Remedy:
  - **Firth penalized likelihood** (`logistf`, `brglm2`) for binary outcomes
    with separation or very low EPV; use profile penalized-likelihood CIs /
    penalized LR tests, NOT Wald.
  - **Log-F(1,1) / weakly-informative priors** for effect-estimation bias
    correction; do not penalize the intercept.
  - **Ridge / elastic net** for prediction tasks with many parameters.
  - Plan a sensitivity analysis over penalty strength.

Mark any sparse-data or separation concern with its proposed remedy in the
spec; leave it `PENDING_LOCAL_DECISION` if the remedy is unresolved.

### Step 6 -- Address collinearity by estimand goal

Collinearity is not a universal problem; judge it by the estimand (see
`collinearity.md`):

- **Causal / etiologic**: collinearity among confounders does NOT bias the
  exposure effect -- NEVER drop a confounder to lower a VIF. If a confounder
  is highly collinear with the exposure, flag it as a positivity / overlap
  concern and inspect overlap; do not delete the covariate.
- **Prognostic factor**: assess VIF only for the focal predictor and its
  adjusters; collinearity among other adjusters is irrelevant to the focal
  estimate.
- **Prediction (fixed predictor set)**: collinearity does not harm
  discrimination or calibration; do not remove predictors to reduce VIF.
- **VIF is a flag, not a verdict**: a high VIF triggers investigation (check n,
  CI width, condition index / variance-decomposition proportions), never
  automatic deletion. Structural collinearity (spline terms, interactions of
  the same variable) is benign -- center and test jointly.

### Step 7 -- Specify interactions

Pre-specify any interaction terms from subject-matter or DAG rationale.
Exploratory interactions must be labeled exploratory. Record degrees of freedom
consumed by interactions in the EPV count (Step 5).

### Step 8 -- Human sign-off

Present the complete model spec: family + link, covariate list with roles,
functional forms with knot specs, EPV assessment, penalization plan (if any),
collinearity judgments, and interaction terms. Request explicit confirmation
that the spec matches the analytic intent. Silence is not consent. Iterate
until aligned. Fitting code is withheld until sign-off.

### Step 9 -- After sign-off

Flip the spec status badge to `LOCKED`. Emit the model formula stub
(language-agnostic R pseudocode) for review. Any subsequent change to the
covariate set, functional form, or penalty must be documented as a dated
amendment in `build/pending-decisions.md`.

## Pairs with (repo policy)

- `.claude/policies/analysis/regression-modeling.md` -- binding rule (no
  dichotomization, RCS, no stepwise, sparse-data penalization, EPV respect).
- `.claude/policies/analysis/collinearity.md` -- VIF-as-flag, goal-directed
  collinearity judgment, never drop a confounder for a high VIF.
- Prerequisites: `frame-study` (estimand LOCKED before spec); `run-ida` (IDA
  informs functional forms and sample-size decisions).
- Next: `validate-assumptions` (post-fit diagnostics after the model is fit).

## Rules / invariants

- **No dichotomization**: never cut a continuous variable at a threshold; model
  the shape with restricted cubic splines or fractional polynomials.
- **No stepwise / automated selection**: pre-specify covariates from the DAG or
  subject knowledge. Penalized selection (LASSO / elastic net) is permitted for
  exploratory tasks only and must be labeled as such. (If backward elimination
  is truly unavoidable in a pre-specified protocol, use alpha ~ 0.157, the
  AIC-equivalent threshold -- never 0.05; this must be declared in the SAP
  before data access, not chosen post-hoc.)
- **Confounders are not a collinearity problem**: never drop a real confounder
  to lower a VIF -- that re-introduces confounding.
- **Sparse data and separation require penalization**: Firth / log-F(1,1) for
  binary outcomes; ridge for high-dimensional prediction. ML estimates under
  sparse data are biased away from the null and must not be reported without a
  remedy.
- **VIF is a flag, not a verdict**: investigate high VIF with n, CI, and
  condition index; the response depends on the estimand goal.
- **PENDING_LOCAL_DECISION for any unmade modeling choice**: unresolved choices
  are stop-signals, not silent defaults.
- **Math by tool**: EPV, knot placement, and penalty tuning come from code or
  `pmsampsize`, not model reasoning.

## Output

Per `../_shared/spec-artifact.md` **simple artifact** convention:

```
analysis/model-spec/<model-slug>-spec.md     # the pre-specified model document
analysis/model-spec/<model-slug>-formula.R   # language-agnostic formula stub (after sign-off)
build/pending-decisions.md                   # PENDING_LOCAL_DECISION register
```

The spec document contains, in order:
1. **Model header** -- outcome, family, link, estimand pointer, status badge.
2. **Covariate table** -- one row per variable: name, role, DAG justification,
   functional form with knot spec for continuous variables, source (data
   dictionary or contract), status (confirmed / uncertain / PENDING).
3. **EPV assessment** -- events, parameters, EPV, sparse-data / separation
   risk, penalization plan.
4. **Collinearity judgment** -- estimand goal, any high-VIF flags and their
   resolution, positivity / overlap flags.
5. **Interaction register** -- pre-specified interactions with rationale;
   exploratory interactions labeled.
6. **PENDING_LOCAL_DECISION register** -- one entry per unresolved choice.