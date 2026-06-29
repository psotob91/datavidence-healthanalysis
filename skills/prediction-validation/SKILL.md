---
name: prediction-validation
description: >-
  Guides development and/or validation of a clinical prediction model (prognostic or
  diagnostic) following TRIPOD+AI (2024) and PROBAST+AI (2025): checks sample size via
  `pmsampsize`, forbids predictor dichotomization, requires internal validation by
  bootstrap optimism correction, demands BOTH calibration (calibration plot + slope /
  intercept) AND discrimination (C-statistic / AUC), adds clinical utility via decision
  curve analysis (`dcurves`), and pre-specifies external / temporal validation. Use when
  the user mentions: prediction model, risk score, clinical prediction model, prognostic
  model, diagnostic model, calibration, discrimination, AUC, C-statistic, TRIPOD,
  TRIPOD+AI, external validation, sample size for a model, predictive performance, or
  `pmsampsize`. Operationalizes `template/docs/analysis/modules/prediction.md`.
  NOT for etiologic / causal regression where coefficients are interpreted as effects
  (use specify-regression / dag-causal instead -- coefficients in a prediction model are
  not causal estimates).
---

# /datavidence-healthanalysis:prediction-validation

> Operationalizes `template/docs/analysis/modules/prediction.md`. Apply
> `../_shared/health-principles.md` (math-by-tool, claim-to-evidence,
> PENDING_LOCAL_DECISION, comprehension-before-code) and emit any sizeable spec
> artifact per `../_shared/spec-artifact.md`. TRIPOD+AI (2024) is the reporting
> standard; PROBAST+AI (2025) is the bias appraisal tool.

## When to use / when NOT to use

- **Use it when:** the user wants to develop, validate, or appraise a clinical
  prediction model (prognostic or diagnostic) -- including risk scores, nomograms,
  and ML classifiers framed as risk estimation. Key triggers: calibration, AUC /
  C-statistic, discrimination, external / temporal validation, `pmsampsize`, TRIPOD.
- **Do NOT use it when:** the goal is to estimate a causal effect or interpret
  coefficients as causal (use specify-regression + dag-causal); describing an
  association without a prediction framing; assembling a code set (use
  map-clinical-codes); computing an epidemiologic indicator (use design-indicator).

## Procedure (in order, no skipping)

1. **Clarify objective and design.** Confirm: development only, validation only, or
   both? Outcome(s), predictor candidate set, candidate population, intended use
   setting, and time horizon (survival / binary / ordinal). Mark unresolved choices
   `PENDING_LOCAL_DECISION`. Do not proceed to sample size until the outcome and
   candidate predictors are stated.

2. **Sample size via `pmsampsize`.** Never use crude events-per-variable (EPV) rules
   -- EPV is deprecated for prediction. Call `pmsampsize::pmsampsize()` with the
   relevant parameters (binary outcome: `type = "b"`, expected outcome prevalence,
   number of parameters, anticipated C-statistic; survival: `type = "s"`). Report
   the shrinkage factor and sample size requirement. If the dataset is smaller,
   flag as PENDING and document implications.

3. **No dichotomizing continuous predictors.** Continuous predictors must enter the
   model as restricted cubic splines (use `rms::rcs()`) or other smooth functions.
   Dichotomizing inflates apparent performance, discards information, and is a PROBAST
   high-bias item. If the user requests a cut-point, explain the problem and return
   `PENDING_LOCAL_DECISION` pending justification from the SAP.

4. **Model development.** Use `rms` (`lrm` for binary, `cph` for survival). Set
   `x = TRUE, y = TRUE` for bootstrap-based validation. Apply shrinkage / penalisation
   if the sample size is borderline (ridge / lasso via `glmnet` or `rms::pentrace`).
   Pre-specify the model formula and any transformations in the analysis plan before
   seeing the data. Alternative path: `tidymodels` + `probably` (for calibration
   utilities and `cal_plot_*()`) provides a tidy-style equivalent; use it when the
   project stack already relies on `tidymodels` -- the same methodological rules
   (no dichotomisation, bootstrap >= 200, calibration plot mandatory) apply.

5. **Internal validation -- bootstrap optimism correction.** Apparent (in-sample)
   performance alone is deprecated. Use `rms::validate()` with `B >= 200` bootstrap
   resamples to estimate optimism-corrected C-statistic and calibration slope. Report
   BOTH the apparent AND the corrected statistics. Cross-validation is acceptable for
   large N; leave-one-out is not recommended.

6. **Discrimination.** Report C-statistic (equivalent to AUC for binary outcomes)
   with 95% CI. For survival models report the Harrell C or time-dependent AUC.
   Use `pROC::roc()` or `rms::validate()` output; math by tool, not by hand.

7. **Calibration -- plot + slope + intercept.** Plot the calibration curve
   (`rms::calibrate()` or `probably::cal_plot_*()`). Report calibration slope and
   calibration-in-the-large (intercept). Do NOT use Hosmer-Lemeshow: it is
   underpowered in small samples, overpowered in large samples, and is deprecated in
   TRIPOD+AI / PROBAST+AI. If the user requests it, explain and return
   `PENDING_LOCAL_DECISION`.

8. **Clinical utility -- decision curve analysis.** Compute net benefit across a
   clinically plausible threshold range using `dcurves::dca()`. Plot alongside the
   "treat all" and "treat none" lines. Summarise the threshold range over which the
   model adds utility. This is a TRIPOD+AI-required item for the intended-use claim.

9. **External / temporal validation (pre-specification).** Specify the validation
   plan before seeing the validation data: source population, time window, whether
   recalibration is permitted (and which type: intercept-only vs. slope+intercept vs.
   full refit), and the minimum sample size (again via `pmsampsize` with
   `type = "cv"`). If external data are not yet available, mark as PENDING and draft
   the pre-specified protocol.

10. **PROBAST+AI appraisal.** Appraise the model across the four PROBAST domains:
    participants, predictors, outcome, analysis. Flag any high-risk-of-bias items
    (common: no sample-size calculation, EPV-only, dichotomisation, Hosmer-Lemeshow,
    apparent-only performance, no calibration plot). Summarise the overall ROB
    judgement. High-ROB items that cannot be fixed become explicit PENDING items.

11. **TRIPOD+AI reporting checklist.** Walk through the applicable TRIPOD+AI items
    (development / validation / both). Confirm each is addressed in the output or
    mark it PENDING. The checklist is an output artefact, not a silent background step.

12. **Human sign-off on the analysis plan** before any model is fit on real data.
    Silence is not consent. The pre-specified plan (predictors, transformations, sample
    size calculation, validation approach) must be approved and locked first.

## Pairs with

- `template/docs/analysis/modules/prediction.md` -- the module policy (packages,
  framework references, pairing with `regression-modeling.md`).
- `specify-regression` -- for etiologic models where coefficients are causal targets
  (different estimand, different checklist).
- `dag-causal` -- causal DAG review before any regression; use to confirm the model
  is framed as prediction, not causal estimation.
- `../_shared/health-principles.md` -- cross-skill invariants (math-by-tool,
  no-invention, PENDING_LOCAL_DECISION, comprehension-before-code).
- `../_shared/spec-artifact.md` -- output layout when the spec exceeds ~300 lines.

## Rules / invariants

- **EPV is not enough:** sample size must come from `pmsampsize`, never from a
  crude events-per-variable rule. Flag any pre-existing EPV calculation.
- **Calibration is mandatory:** reporting only discrimination (AUC / C-statistic)
  is incomplete. Calibration plot + slope + intercept are non-negotiable per
  TRIPOD+AI / PROBAST+AI.
- **Hosmer-Lemeshow is banned:** return `PENDING_LOCAL_DECISION` if the user or
  protocol demands it; explain the deprecation.
- **No predictor dichotomisation:** splines or smooth functions only; cut-points
  require explicit SAP justification and remain PENDING until given.
- **Bootstrap >= 200:** fewer resamples underestimate optimism; flag if B < 200.
- **Prediction != causation:** coefficients in a prediction model cannot be
  interpreted as causal effects; redirect to specify-regression / dag-causal.
- **PENDING_LOCAL_DECISION, never a silent default:** any unresolved methodological
  choice (threshold range for DCA, recalibration strategy, penalisation method)
  surfaces as a named PENDING item.
- **Math by tool:** all numeric outputs (C-statistic, calibration slope, net
  benefit, sample size) come from R; never computed or approximated in the model.

## Output

Emit per `../_shared/spec-artifact.md`:

- **Small spec (<= ~300 lines):** one `<spec-dir>/prediction-spec.md` + optional
  `index.qmd` (R stack).
- **Large spec:** indexed `<spec-dir>/` with `comprehension/`, `build/`
  (`pseudocode.md`, `pending-decisions.md`), `validation/validation-plan.md`,
  `tripod-checklist.md`, `probast-appraisal.md`, `README.md` router, and
  (R stack) `index.qmd` + `spec-theme.scss`.
- After sign-off: `code/` (R scripts: `pmsampsize`, `lrm`/`cph`, `validate`,
  `calibrate`, `dca`) + `tests/`.
- Runnable code is withheld until the analysis plan is signed off; the pseudocode
  and PROBAST / TRIPOD checklists are not withheld.