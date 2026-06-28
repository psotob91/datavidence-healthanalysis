---
name: run-ida
description: >-
  Runs the STRATOS-structured Initial Data Analysis (IDA) before modeling: screens the data across
  five domains (metadata/data-cleaning, missingness, univariate distributions, multivariate
  associations, data-method-of-analysis consistency) without peaking at the explanatory-outcome
  association, flags issues as PENDING_LOCAL_DECISION, and emits a chaptered IDA report with
  graphics first (summarytools, naniar, ggplot2). A LONGITUDINAL MODE activates automatically
  when repeated-measures data are present: adds a domain-six scan covering participation profile,
  timing balance, dropout classification, and within-subject correlation (spaghetti/lasagna plots).
  Findings feed pre-specification; any change to the SAP is logged with justification.
  Use when the user asks for initial data analysis, IDA, EDA, data screening, screen the data
  before modeling, check the data is fit for purpose, or when the data involve a longitudinal,
  repeated-measures, or panel structure. Scope: STRATOS structured IDA BEFORE modeling. NOT model
  diagnostics or post-fit residual checks (use validate-assumptions for those); NOT informal
  exploratory hunting for findings. Distinct from EDA: IDA checks fitness-for-purpose, not discovery.
---

# /datavidence-healthanalysis:run-ida

> Operationalizes `.claude/policies/analysis/initial-data-analysis.md` and (repeated-measures branch)
> `.claude/policies/analysis/longitudinal-data.md`. Apply `../_shared/health-principles.md`
> (math-by-tool, claim-to-evidence, PENDING_LOCAL_DECISION, no invention) and emit the artifact per
> `../_shared/spec-artifact.md` (chaptered split-indexed dir + qmd render). IDA runs BEFORE any
> outcome-model; the no-peek invariant is enforced throughout.

## When to use / when NOT to use

- **Use** when the user asks to run IDA, screen the data before modeling, check data quality or
  fitness-for-purpose, perform data cleaning checks, inspect missingness, or review the
  longitudinal/repeated-measures structure before analysis.
- **Do NOT use** when the user wants post-fit residual checks, proportional-hazards tests, or
  goodness-of-fit diagnostics -- those are outcome-model checks; use `validate-assumptions`. Do NOT
  use for informal EDA that hunts for exposure-outcome signals: IDA enforces the no-peek rule and
  is separate from inference.

## What it does: the IDA procedure (in order, no skipping)

**Pre-check -- IDA plan.** Verify that a pre-specified IDA plan exists (aligned with the SAP)
before running any domain. If no IDA plan has been drafted, flag this as PENDING_LOCAL_DECISION
and recommend drafting one alongside frame-study before the IDA run begins.

Determine whether the dataset has a repeated-measures structure (multiple rows per subject, a
time/visit variable, or a panel identifier). If yes, activate LONGITUDINAL MODE: domain 6 is added.

### Domain 1 -- Metadata and data cleaning
1. Read `metadata/data_dictionary.csv` + `contracts/*.yml`. Verify all expected variables are
   present with the declared types and ranges.
2. Check encoding, date formats, factor levels, and ID consistency across tables/files.
3. Flag discrepancies as `<<PENDING_LOCAL_DECISION_D1_Qn>>` (e.g., conflicting date formats,
   undocumented codes). Never invent a cleaning rule.
4. Output: `ida/01-metadata-cleaning.md` -- table of issues, types, ranges, ID check.

### Domain 2 -- Missingness
1. Compute missingness counts and proportions per variable (delegate to R / naniar -- never count
   mentally). Visualize: `naniar::vis_miss()`, upset plot, shadow matrix.
2. Classify each variable by missingness rate: acceptable / moderate / high / critical
   (thresholds from the SAP or flag as PENDING_LOCAL_DECISION if unstated).
3. For repeated measures (LONGITUDINAL MODE): distinguish non-enrollment / intermittent /
   dropout / death; compare complete vs incomplete responders on baseline characteristics.
4. Flag imputation strategy choices as PENDING_LOCAL_DECISION; do not impute silently.
5. Output: `ida/02-missingness.md` + missingness figures.

### Domain 3 -- Univariate distributions
1. For all analysis variables (excluding the outcome-model association): run
   `summarytools::dfSummary()` or equivalent; produce histograms / bar charts / QQ plots.
2. For repeated measures (LONGITUDINAL MODE): summarize both baseline and time-varying variables
   at each wave; include per-wave n and range.
3. Flag distributional issues (extreme skew, implausible values, floor/ceiling effects) as
   PENDING_LOCAL_DECISION (transformation choice belongs to the SAP).
4. Output: `ida/03-univariate.md` + figures.

### Domain 4 -- Multivariate associations and subgroup adequacy
1. Examine associations AMONG explanatory + structural variables ONLY. Never examine
   explanatory-outcome associations. This is the no-peek line.
2. Assess collinearity (VIF / correlation matrix) among candidate predictors.
3. Screen for influential observations: leverage and Cook's distance (e.g. `car::outlierTest`,
   `influence.measures()`); flag influential points as PENDING_LOCAL_DECISION for the SAP.
4. Check subgroup and stratum sizes against the SAP's minimum-n requirements; flag cells below
   threshold as PENDING_LOCAL_DECISION.
5. For repeated measures (LONGITUDINAL MODE): visualize associations stratified by structural
   variables (e.g. sex, centre); state which variables are time-varying vs time-fixed.
6. Output: `ida/04-multivariate.md` + figures.

### Domain 5 -- Data-method-of-analysis consistency
1. Verify the data structure supports the planned model family: correct grain, time scale,
   event/censoring encoding (survival), outcome distribution.
2. For survival data: check for tied event times, administrative censoring, and left-truncation.
3. For repeated measures (LONGITUDINAL MODE): verify the long-format structure, the time variable,
   wave balance, and whether the correlation structure assumption in the SAP is plausible.
4. Flag any mismatch between data structure and planned method as PENDING_LOCAL_DECISION.
5. Output: `ida/05-consistency.md`.

### Domain 6 -- Longitudinal structure scan (LONGITUDINAL MODE only)
Activated when repeated-measures data detected. Based on STRATOS TG3 (Lusa et al., PLOS ONE 2024,
`pone.0295726`).
1. **Participation profile**: n subjects, measurements per subject (min/median/max), planned vs
   actual timing. Display as a profile plot or lasagna plot.
2. **Timing and balance**: histogram of inter-visit gaps; flag irregular spacing for PENDING.
3. **Dropout classification**: distinguish informative (death, worsening) vs administrative vs
   random dropout. Tabulate by wave. Assess predictors of dropout vs. completers.
4. **Within-subject correlation**: compute intraclass correlation (ICC) and lag-1 autocorrelation;
   plot spaghetti plots (a random sample of trajectories) and mean-profile plots.
5. Output: `ida/06-longitudinal.md` + spaghetti/lasagna/profile figures.

### IDA report and SAP feedback
After all domains: summarize findings that feed pre-specification. For each issue requiring an
SAP update, state: (a) the finding, (b) the proposed SAP change, (c) justification. Present as
a PENDING register. Do not modify the SAP directly; surface the list for human decision.

## Pairs with (repo policy)

- `.claude/policies/analysis/initial-data-analysis.md` (the IDA rule; 5-domain STRATOS structure)
- `.claude/policies/analysis/longitudinal-data.md` (longitudinal mode; 5+1 domain list; reference
  Lusa et al. 2024 `pone.0295726`)
- Prerequisite: `analysis/data-contracts.md` -- data must pass contracts before IDA.
- Next-if: repeated measures -> proceed to `analysis/longitudinal-data.md` (method selection);
  ready for modeling -> `analysis/regression-modeling.md` then `analysis/model-assumptions.md`.

## Boundary vs assess-missingness

run-ida's Domain 2 is a scoped missingness screen (counts, patterns, classification) that
feeds the IDA PENDING register. A full standalone missingness analysis -- mechanism reasoning
(MCAR/MAR/MNAR), imputation strategy, MNAR sensitivity plan -- is `assess-missingness`.

## Rules / invariants

- **No-peek invariant**: domain 4 covers associations AMONG explanatory + structural variables
  only. Any exploratory look at the explanatory-outcome association during IDA is a protocol
  violation. If such an association appears incidentally, stop and flag it; do not include it
  in the IDA report.
- **Math by tool**: all counts, percentages, ICCs, VIFs, and distributional summaries go to R
  (summarytools, naniar, ggplot2, car, psych). Never compute mentally.
- **PENDING_LOCAL_DECISION**: any choice not fixed in the SAP (missingness threshold, imputation
  method, transformation, subgroup minimum n, correlation structure) is flagged, never invented.
- **Claim to evidence**: every finding cites the function + output line that produced it; no
  assertion from memory.
- **IDA != EDA**: IDA checks fitness-for-purpose against a pre-specified plan; it does not hunt
  for associations. Enforce the distinction explicitly in the report header.

## Output

Emit an IDA report per `../_shared/spec-artifact.md`:

- **Small dataset / simple design** (<= ~300 lines total): a single `ida/ida-report.md` + an
  `index.qmd` that includes it (R stack). Rare; most real analyses exceed this.
- **Standard case (split-indexed directory)**:
  ```
  ida/
    index.qmd                  # chaptered + tabbed academic + executive HTML
    spec-theme.scss            # copied from child scaffold
    README.md                  # router: one row per section file
    01-metadata-cleaning.md
    02-missingness.md          # + figures/
    03-univariate.md           # + figures/
    04-multivariate.md         # + figures/
    05-consistency.md
    06-longitudinal.md         # LONGITUDINAL MODE only; + figures/
    pending-decisions.md       # PENDING_LOCAL_DECISION register (SAP feedback list)
  ```
  Section files use `####`+ headings only (never `#`/`##`/`###` inside includes -- Quarto tabs).
  `quarto render index.qmd` -> standalone HTML; executive summary on top with open-PENDING
  checklist and status badge; chapters per domain.
- **No Quarto (non-R stack)**: ship the indexed `.md` set + README router only.
- Graphics are embedded per domain section (not in a separate appendix); generated by R, never
  hand-drawn or described in prose without the underlying code.