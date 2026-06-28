---
name: frame-study
description: >-
  Frames the analysis plan UP FRONT -- pre-specifies the estimand, classifies the
  analytic task, selects the EQUATOR reporting guideline, and emits a SAP skeleton
  -- before any results are examined. Use when the user asks to write an analysis
  plan, draft a SAP, write a statistical analysis plan, pre-specify the estimand,
  define the outcome before results, choose a reporting guideline, or turn a study
  protocol into an analysis plan. Operationalizes analysis/pre-specification.md,
  analysis/statistical-reporting.md, and health/reporting-standards.md. NOT for
  running the analysis (that follows sign-off); NOT for model diagnostics
  (use validate-assumptions); NOT for case labeling (use phenotype-gate).
---

# /datavidence-healthanalysis:frame-study

> Operationalizes `.claude/policies/analysis/pre-specification.md`,
> `analysis/statistical-reporting.md`, and `health/reporting-standards.md`.
> Apply `../_shared/health-principles.md` (math-by-tool, claim-to-evidence,
> PENDING_LOCAL_DECISION) and emit the artifact per `../_shared/spec-artifact.md`
> (chaptered split-indexed directory + `index.qmd` render, with the variable
> catalog). Pre-specification runs BEFORE any outcome-exposure association is
> examined; the SAP is LOCKED before analysis begins.

## When to use / when NOT to use

- **Use it when:** the user wants to write an analysis plan or SAP, pre-specify
  the estimand or outcome, choose a reporting guideline, map a protocol to a
  statistical method, or frame what the study will estimate and how.
- **Do NOT use it when:** the analysis is already running or results are in hand
  (frame-study is pre-analysis only); model fit or assumption checking is the goal
  (use validate-assumptions); case or phenotype identification is the goal
  (use phenotype-gate).

## What it does: the framing sequence (in order, no skipping)

Produce the SAP-skeleton sections (see Output for layout), then STOP for sign-off:

1. **Estimand** -- state, in one block, the five ICH E9(R1) components:
   - **Population** (eligibility criteria, index date, exclusion rules).
   - **Treatment/Exposure** (strategies or levels being compared).
   - **Outcome** (primary + key secondary; pointer to the phenotype-gate artifact
     when a computable definition is needed).
   - **Contrast** (risk difference, odds ratio, hazard ratio, mean difference --
     one per outcome; PENDING_LOCAL_DECISION if not decided).
   - **Intercurrent-event strategy** (per ICH E9(R1): hypothetical, composite,
     while-on-treatment, principal stratum, or treatment-policy -- name it;
     "ITT vs per-protocol" alone is not enough).
   Mark any component not resolved by the protocol as `PENDING_LOCAL_DECISION`.
   Mark any fact that cannot be anchored to the protocol or data dictionary as
   `<<PENDING_CONFIRMATION_Qn>>`. Never invent a threshold or code.

2. **Study type + analytic task** -- identify which STRATOS / SAMBR task applies:
   - Descriptive (occurrence / fundamental prognosis) -- no causal claim; PROGRESS-1 path.
   - Descriptive (prognostic factor / biomarker association) -- PROGRESS-2 + REMARK path.
   - Causal / etiologic -- target-trial emulation + DAGs required.
   - Prediction model (development / validation) -- PROGRESS-3 methodological framework
     (NOT a reporting guideline) + TRIPOD+AI (2024) as the reporting guideline.
   - Diagnostic accuracy -- STARD path.
   - Evidence synthesis -- PRISMA path (module `synthesis`).
   State the task in one sentence; flag task mismatch if the stated objective does
   not match the stated method. Record task label in the SAP header.

3. **EQUATOR guideline selection** -- pick ONE primary guideline per the task map
   in `health/reporting-standards.md`; note extensions that apply:
   - Observational -> STROBE; routinely-collected / secondary data -> add RECORD
     (pharmacoepidemiology -> RECORD-PE).
   - Causal from observational -> TARGET on top of STROBE/RECORD; state the
     identifying assumptions.
   - RCT -> CONSORT 2025 (protocol: SPIRIT 2013); routinely-collected data -> CONSORT-ROUTINE.
   - Prediction model -> TRIPOD+AI (2024).
   - Prognostic factor -> REMARK.
   - Diagnostic accuracy -> STARD (+ STARD-AI for AI-based tests).
   - Synthesis -> PRISMA (module `synthesis`).
   Record the selected guideline + extensions in the SAP header and name the
   checklist file path (`docs/analysis/reporting-checklist.md`). Do not copy
   copyrighted checklist text; reference item numbers only.

4. **Analytic method map** -- for each outcome and each secondary analysis, list:
   - The chosen method (e.g., Cox PH, logistic, linear, G-computation, IPW,
     LASSO) and the rationale tying it to design + objective (SAMBR Part B).
   - Whether it is pre-specified or exploratory; exploratory analyses must be
     labeled as such. No HARKing.
   - Confounding / variable-selection strategy, tied to the task: DAG for causal;
     domain knowledge for prognostic factor; penalized regression (LASSO /
     elastic net, CV) for exploratory (STRATOS / Heinze et al., Biom J 2018).
   - Effect-size metric + confidence interval + software + version (SAMBR / SAMPL:
     exact p-values when used; CIs are mandatory).
   Mark undecided method choices PENDING_LOCAL_DECISION.

5. **Post-hoc flag register** -- any analysis the user describes AFTER the
   outcome-exposure association has been seen must be flagged in
   `build/pending-decisions.md` as `POST_HOC_ANALYSIS` with the date flagged.
   Do not suppress or silently reclassify a post-hoc analysis as pre-specified.

6. **Variable catalog stub** -- for each variable named in the estimand or method
   map, create one entry in `variable-catalog.yaml` (schema from
   `../_shared/spec-artifact.md`). READ `metadata/data_dictionary.csv` and
   `contracts/*.yml` first: a variable found there is `status: confirmed`; one
   that must be built from others is `analytic_role: derived`; one that cannot be
   confirmed is `analytic_role: uncertain`, `status: unknown`, marked
   `<<PENDING_CONFIRMATION_Qn>>`. Never invent a column.

7. **Human sign-off** -- present the estimand block + task label + guideline
   selection + method map; ask for explicit confirmation that they match the
   research intent. Silence is not consent. Iterate until aligned. Analysis
   code is withheld until sign-off; the SAP skeleton is not.

8. **After sign-off** -- flip the SAP status badge to `LOCKED` and record the
   date. Any subsequent change to the estimand, primary outcome, or primary
   method must be documented as a dated amendment in `build/pending-decisions.md`
   with a pre-specified-vs-exploratory label.

## Boundary vs design-indicator

design-indicator builds the denominator / person-time object upstream (cohort
entry, index date, at-risk windows); frame-study consumes that object and frames
the SAP around it. If the denominator has not been defined, run design-indicator
first.

## Pairs with (repo policy)

- `.claude/policies/analysis/pre-specification.md` -- the binding pre-specification rule.
- `.claude/policies/analysis/statistical-reporting.md` -- task -> method + guideline map (SAMBR).
- `.claude/policies/health/reporting-standards.md` -- EQUATOR guideline selection by design.
- Prerequisite: phenotype-gate (primary outcome must be operationalized before the
  SAP is LOCKED; frame-study consumes the phenotype-gate artifact).
- Next: validate-assumptions (model diagnostics run after analysis, not during framing).

## Rules / invariants

- **Pre-specification templates for observational studies.** For analytic
  observational work, structured pre-specification via HARPER or STaRT-RWE is
  strongly recommended (note: trial-style prospective registration is contested
  for observational studies and is not mandatory; follow the child protocol or
  flag as PENDING_LOCAL_DECISION if unstated).
- **Estimand first.** The five ICH E9(R1) components are required before any
  method is specified. A study that names only ITT vs per-protocol has not named
  its intercurrent-event strategy; return PENDING_LOCAL_DECISION.
- **Task governs method and guideline.** Do not select a method or guideline before
  naming the task. A mismatch (e.g., causal language with a descriptive design)
  must be flagged, not silently resolved.
- **No HARKing.** Post-hoc analyses must be labeled. Pre-specified-vs-exploratory
  labeling is not cosmetic; it changes the inference interpretation.
- **Math by tool.** No power calculation, effect-size estimate, or sample-size
  computation in the model head; delegate to R code or WolframAlpha MCP.
- **Claim to evidence.** Every threshold, variable, and citation anchors to the
  protocol, data dictionary, or a canonical source (DOI). Mark unanchored facts
  `<<PENDING_CONFIRMATION_Qn>>`.
- **CHAMP self-appraisal.** For analytic observational studies and RCTs, apply the
  CHAMP checklist (Catalogue of Bias; scope: analytic observational + RCT) as a
  statistical self-appraisal lens on the method map. Scope excludes prediction
  models, diagnostic-accuracy studies, and purely descriptive analyses.
- **PENDING_LOCAL_DECISION, never a silent default.** An unresolved methodological
  choice (washout window, confounder set, sensitivity threshold) is a stop-signal,
  not a default to fill in quietly.

## Output

Emit a SAP-skeleton artifact per `../_shared/spec-artifact.md`:

- **Small plan (<= ~300 lines):** one `<spec-dir>/sap-skeleton.md` plus (R stack)
  an `index.qmd` that includes it.
- **Large (the usual case):** split into the indexed `<spec-dir>/` --
  - `framing/01-estimand.md` -- the five ICH E9(R1) components.
  - `framing/02-study-type.md` -- task label + STRATOS/SAMBR classification.
  - `framing/03-guideline.md` -- selected EQUATOR guideline + extensions + checklist path.
  - `framing/04-method-map.md` -- outcome x method x confounding strategy x software.
  - `build/variable-catalog.yaml` -- one entry per named variable (schema from `../_shared/spec-artifact.md`).
  - `build/variables.md` -- catalog rendered as a table with status badges.
  - `build/pending-decisions.md` -- PENDING_LOCAL_DECISION + POST_HOC_ANALYSIS register.
  - `README.md` -- one-row-per-file router (human + agent nav).
  - `index.qmd` + `spec-theme.scss` copied from child scaffold (`analysis/_spec-template.qmd`,
    R stack only). `quarto render index.qmd` -> chaptered, tabbed, standalone HTML:
    executive summary callout on top (status badge, estimand restatement, open PENDING
    checklist) above chapter tabs; section files use `####`+ headings only so tabs stay clean.
- **No Quarto (non-R stack):** ship the indexed `.md` set + README only.
- After sign-off: flip the status badge to `LOCKED`, record the date, and note
  that subsequent estimand or method changes must be dated amendments.