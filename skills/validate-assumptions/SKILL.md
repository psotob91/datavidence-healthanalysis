---
name: validate-assumptions
description: >-
  Runs post-fit model diagnostics for the model family in hand: selects the
  correct residual type, produces graphics-first assumption checks, interprets
  every plot, distinguishes violations that matter from ones that do not, and
  proposes remedies for each family (OLS, GLM/quasi, Cox, mixed, Bayesian MCMC,
  Bayesian INLA). Use when the user asks to check model assumptions, run residual
  diagnostics, run model diagnostics, check proportional hazards, check whether
  a model is valid, check linearity, check normality, check homoscedasticity, or inspect post-fit influence
  diagnostics (Cook's distance, leverage, DFBETA, influential observations).
  Operationalizes analysis/model-assumptions.md. NOT for pre-fit data screening
  (use run-ida) and NOT for model specification choices (use specify-regression).
---

# /datavidence-healthanalysis:validate-assumptions

> Operationalizes `.claude/policies/analysis/model-assumptions.md`. Apply
> `../_shared/health-principles.md` (math-by-tool, claim-to-evidence,
> PENDING_LOCAL_DECISION, comprehension-before-code) and emit the artifact per
> `../_shared/spec-artifact.md` -- a **simple artifact** (single focused
> diagnostics report + optional small render).

## When to use / when NOT to use

- **Use it when:** a model has already been fit and the user wants to check
  whether its assumptions hold -- residual plots, Schoenfeld residuals, DHARMa
  simulations, posterior predictive checks, convergence diagnostics, etc.
- **Do NOT use it when:** the goal is pre-fit data exploration or screening --
  use `run-ida`; the goal is choosing or specifying a model family or link
  function -- use `specify-regression`. This skill diagnoses an existing fit;
  those skills prepare for or specify the fit.

## What it does: the diagnostics protocol (in order)

### Step 1 -- Identify the model family

Confirm which model class was fit from context or by asking. One of:

- **OLS** (ordinary linear regression, `lm`)
- **GLM / quasi** (logistic, Poisson, negative-binomial, quasi-*, `glm`/`glmmTMB`)
- **GAM / GAMLSS** (smoothed terms, `mgcv`/`gamlss`)
- **Cox / parametric survival** (`coxph`, `survreg`)
- **Mixed / multilevel** (GLMM, `lme4`, `glmmTMB`, `nlme`)
- **Bayesian MCMC** (Stan / `brms` / JAGS)
- **Bayesian INLA** (`INLA` package)

If the model family is not clear from context, ask before proceeding.
Mark any unresolved modeling choice `PENDING_LOCAL_DECISION`.

### Step 2 -- Select the correct residual / diagnostic tool

| Family | Primary residual / tool | Package |
|---|---|---|
| OLS | Raw, Pearson, studentized; residuals-vs-fitted, scale-location, QQ | base R, `car` |
| GLM / quasi | **Randomized quantile residuals** (Dunn-Smyth) | `statmod::qresid` |
| GAM | Randomized quantile residuals; `mgcv::gam.check` | `mgcv`, `statmod` |
| Cox | **Schoenfeld residuals** + `survival::cox.zph` for PH; martingale for linearity | `survival` |
| Mixed | Simulation-based scaled residuals | `DHARMa` |
| Bayesian MCMC (brms/Stan) | Trace plots, R-hat, ESS, divergences, `pp_check`, LOO/Pareto-k | `bayesplot`, `loo` |
| Bayesian INLA | PIT histogram, CPO/failure flags, KLD, prior sensitivity | `INLA` |

Never use raw or Pearson residuals for GLMs or mixed models -- they mislead for
discrete or non-normal responses.

### Step 3 -- Produce graphics-first diagnostics

For every model family, generate the correct diagnostic plots first. Formal
tests are secondary and must always carry a sample-size caveat: small samples
pass almost anything; large samples flag trivial deviations. Significance does
not equal relevance.

**OLS:** residuals-vs-fitted (linearity, homoscedasticity), scale-location
(heteroscedasticity), QQ (normality), residuals-vs-leverage + Cook distance
(influence). Use `car::residualPlots`, `car::qqPlot`, `car::influencePlot`.
`performance::check_model` provides a single-call panel.

**GLM / quasi / GAM:** QQ and residuals-vs-fitted of randomized quantile
residuals (`statmod::qresid`). `DHARMa` is the recommended alternative for
GLMMs and complex GLMs -- simulates scaled residuals that behave like normal
residuals regardless of family. Supplement with `car::residualPlots` for
Pearson (structural check, not distributional).

**Cox:** `survival::cox.zph` tests and plots Schoenfeld residuals against time --
a non-flat (sloped or non-random) pattern signals PH violation. Martingale
residuals against continuous covariates reveal non-linearity; deviance residuals
identify outlying observations. If PH is violated, the remedy is a time-varying
coefficient, a stratified Cox, or a landmark analysis -- not ignoring the pattern.

**Mixed:** `DHARMa::simulateResiduals` + `plotSimulatedResiduals`. Check
dispersion, outliers, zero-inflation, and spatial/temporal autocorrelation with
the `DHARMa` test suite. QQ plots of random effects (BLUP normality) are
informative but secondary.

**Bayesian MCMC (brms / Stan / JAGS):** convergence is a prerequisite, not a
robustifiable assumption. Require R-hat < 1.01 (>= 4 chains), bulk-ESS and
tail-ESS >= 400, clean trace plots. For Stan/NUTS additionally: investigate and
ideally eliminate divergent transitions (raise `adapt_delta`, reparameterize,
or revise the model) -- never report a posterior with unresolved divergences;
check E-BFMI and treedepth. Then: `bayesplot::pp_check` (posterior predictive
check), prior sensitivity (refit with overdispersed/alternative priors and
overlay posteriors), LOO with Pareto-k flags (`loo` package; Pareto-k > 0.7
signals high-influence observations requiring more attention).

**Bayesian INLA:** check PIT histogram (approximately uniform is the target -- a
U-shape signals overdispersion, an inverse-U underdispersion); CPO values and
`inla.cpo` failure flags (low CPO = surprising observations; failures = numerical
instability); KLD column (Laplace-approximation validity -- large KLD suggests
switching strategy or using MCMC). Use PC priors as the principled default. Run
prior sensitivity: refit with at least one alternative prior and overlay marginals.

### Step 4 -- Interpret every plot; frame violation does not equal invalid

For each diagnostic produced:

1. Describe what the pattern shows (e.g., fan-shaped spread, heavy tails,
   non-flat Schoenfeld slope, PIT U-shape).
2. Assess impact: Is the deviation large enough to affect inference? Many models
   are robust to moderate assumption violations -- say so explicitly when true,
   with a one-sentence explanation of why.
3. Name the remedy when impact is real (see Step 5).
4. Always educate the user on the why -- never assume prior knowledge of why
   a plot looks the way it does.

Distinguish:
- **Robustness patches** (sandwich/robust SE, cluster-robust) -- make patched
  inference valid without changing the fit; residuals of the original model will
  still look off. State this limitation explicitly.
- **Fit corrections** (WLS for heteroscedasticity, better link/family/transform)
  -- change the fit itself. Verify success with the appropriate residual after
  the correction.

### Step 5 -- Propose remedies

| Violation | Candidate remedies |
|---|---|
| Non-linearity | Restricted cubic splines (`rcs`/`Hmisc`), fractional polynomials. Never dichotomize. |
| Heteroscedasticity | WLS, robust/sandwich SE (flag: inference patch, not fit fix), GAMLSS for variance modeling |
| Non-normality of residuals | GLM with appropriate family, Box-Cox transform, or quantile regression |
| GLM overdispersion | Quasi-Poisson / negative-binomial / `glmmTMB` |
| Cox PH violation | Time-varying coefficient, stratified Cox, landmark analysis |
| Mixed model mis-specification | DHARMa-guided: add zero-inflation term, adjust random structure |
| MCMC non-convergence | Non-centered parameterization, better priors, more iterations, higher `adapt_delta` |
| INLA approximation failure | Change `strategy` argument, switch to MCMC |
| Influential observations | Sensitivity analysis with/without; report Cook distance; never silently delete |

Mark any remedy requiring an unmade modeling decision as `PENDING_LOCAL_DECISION`.

### Step 6 -- Check linearity of continuous predictors and influential points

Always, regardless of family: plot each continuous predictor against the
appropriate residual (or use component-plus-residual / partial-residual plots);
flag non-linearity for spline modeling. Report influential observations via
Cook distance and dfbeta. Document any high-leverage point in the report.

## Output

Per `../_shared/spec-artifact.md` **simple artifact** convention -- a single
focused report plus an optional small render:

```
analysis/model-checks/<model-name>-diagnostics.md    # the diagnostics report
analysis/model-checks/<model-name>-diagnostics.qmd   # optional (R stack only)
```

The report contains, in order:
1. **Model summary** -- family, formula, dataset, N (from context or code output).
2. **Diagnostic plots** -- one subsection per plot, with the R snippet to
   reproduce it, the plot (inline or path), and the interpretation paragraph.
3. **Assumption verdict table** -- one row per assumption, columns:
   Assumption | Status (OK / Warning / Violated) | Impact | Remedy.
4. **PENDING_LOCAL_DECISION register** -- any unresolved choice that blocks a
   remedy decision.
5. **R session info** -- `sessionInfo()` or `sessioninfo::session_info()` output
   (math-by-tool: the model environment is the evidence anchor).

Keep the report under 300 lines. If it grows beyond that (e.g., multiple model
families in one pass), split into one file per family with a README router.

## Pairs with (repo policy)

- `.claude/policies/analysis/model-assumptions.md` (the rule; prerequisite
  `analysis/regression-modeling.md` -- diagnose the fit obtained there).
- Boundary skills: `run-ida` (pre-fit data screening); `specify-regression`
  (model specification choices).

## Rules / invariants

- Graphics over tests: produce plots first; report tests only as supplementary,
  always with the sample-size caveat.
- Correct residual per family: randomized quantile residuals for GLMs, DHARMa
  for mixed, Schoenfeld for Cox, PIT/CPO for INLA -- never raw residuals where
  they mislead.
- Bayesian convergence is a prerequisite, not a robustifiable assumption: a
  non-converged chain or invalid approximation cannot be patched -- fix the model.
- Violation does not equal invalid: assess impact every time; educate the user.
- Math by tool: all numeric diagnostics come from code output, not model reasoning.
- PENDING_LOCAL_DECISION for any unmade remedy choice; never invent a default.