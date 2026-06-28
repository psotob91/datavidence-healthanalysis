# Spec artifact format (shared)

> Read by domain skills that emit a sizeable methodological spec (phenotype-gate, design-indicator,
> map-clinical-codes, frame-study, scaffold-reporting, ...). NOT a skill. Defines ONE output convention so a large spec
> stays navigable for humans AND useful as coding input. The render scaffold lives in the child, not here.

## When to split
Measure the draft spec against the child doc-hygiene limits (reference 300 / doc 400 lines).
- Small (<= ~300 lines): keep ONE file `<spec-dir>/<name>-spec.md` and (R stack) an `index.qmd` that includes it.
- Large (> limit): split into the indexed directory below. Never truncate -- split.
- **Simple artifacts** (e.g. a code-set manifest, a short report) need not use `<spec-dir>/` at all -- a single
  `metadata/<name>-manifest.md` (+ optional small render) is the artifact; the provenance + PENDING-register +
  optional themed-render principles still apply.

## Canonical layout (large spec)
```
<spec-dir>/                         e.g. analysis/phenotypes/<name>/
  index.qmd                         # chapters + tabsets (copied from the child scaffold)
  spec-theme.scss                   # copied sibling (academic + executive theme)
  README.md                         # index-as-router: one row per section file (human + agent nav)
  variable-catalog.yaml             # MACHINE contract for the coding step (schema below)
  comprehension/
    01-restatement.md               # narrative restatement + language traps
    02-worked-examples.md
    03-counter-examples.md
    04-decision-diagram.md          # ASCII decision   (name matches routing.yml *decision*)
    05-timelines.md                 # ASCII temporal   (name matches routing.yml *timeline*)
    06-granularity-states.md
  build/                            # "hacia el codigo"
    variables.md                    # rendered catalog table (from variable-catalog.yaml)
    pseudocode.md                   # IMPLEMENTABLE pseudocode (language-agnostic; see below)
    pending-decisions.md            # PENDING_LOCAL_DECISION register -- the coding-ready blockers
  validation/
    validation-plan.md
  (after sign-off) code/, tests/fixtures.md
```
The `comprehension/` dir + `04-decision-diagram.md` + `05-timelines.md` names satisfy the child
`routing.yml` `phenotype-timeline-gate` (`requires_first: *timeline* / *decision* / *comprehension*`):
the split itself unlocks the code-write gate. Do not rename them away from those stems.

## The render (human view): academic + executive
- The child ships the scaffold at `analysis/_spec-template.qmd` + `analysis/_assets/spec-theme.scss`
  (only when `analysis_stack == r`). COPY both into `<spec-dir>/` (as `index.qmd`, `spec-theme.scss`),
  fill the `__PLACEHOLDERS__`, then `quarto render index.qmd`.
- Structure: an always-visible EXECUTIVE SUMMARY callout (status badge, one-paragraph restatement, the
  decision diagram, the open PENDING checklist) ABOVE chapters: `## Comprension` and `## Hacia el codigo`
  (each a `::: {.panel-tabset}`) and `## Validacion`. `embed-resources: true` => standalone HTML.
- **Heading rule (avoids the tabset collision):** `index.qmd` owns the structure -- `##` = chapter,
  `###` = a SHORT tab name. Every INCLUDED section file uses `####`+ ONLY (never #/##/###); its long
  descriptive title is a `####` line in its own body. A `##`/`###` inside an include becomes a stray
  extra tab -- this is the bug that made early renders look crowded.
- No Quarto (non-R stack): skip the qmd; ship the indexed `.md` set + README router only.

## Variable catalog (`variable-catalog.yaml` + `build/variables.md`)
The bridge from the spec to code. One entry per variable the algorithm reads or builds. Reuse the tsukuba
schema (do not invent a parallel one); it is the seed of the future `variable-catalog-gate` hook.
```yaml
- variable_id:   has_dialysis_code
  analytic_role: input            # input | derived | uncertain
  source:        claims.procedimientos.cpt   # table.column when it EXISTS in the data dictionary
  grain:         claim-line
  derivation:    null             # for derived: the recipe (which vars + how combined)
  qc:            "range/dup check before use"
  status:        confirmed        # confirmed | unknown | validated
  provenance:    "metadata/data_dictionary.csv (2026-06)"
```
- READ the child metadata first: `metadata/data_dictionary.csv` (cols variable/label/type/derivation/source)
  and `contracts/*.yml`. A variable found there -> `status: confirmed`, `source: table.column`.
- A variable that must be BUILT from others -> `analytic_role: derived`, fill `derivation:` (the recipe).
- A variable you are NOT sure exists / cannot confirm -> `analytic_role: uncertain`, `status: unknown`,
  and mark it `<<PENDING_CONFIRMATION_Qn>>`: it becomes an EXPLORATION target (and would be blocked by
  `variable-catalog-gate`). Never invent a column.
- `build/variables.md` renders the catalog as a table; tag the status cell with
  `[confirmed]{.var-status .confirmed}` / `.derived` / `.unknown` for the themed badge.
- Self-contained per spec; promotable to a project `analysis-plan/shared/variables.yaml`.

## Implementable pseudocode (`build/pseudocode.md`)
Per `analysis/pseudocode-first.md`: a language-agnostic, code-like plan -- looks like code but binds to no
language (FOR each patient / FILTER / COUNT / IF span > 30 THEN INCLUDE ...). It references
`variable-catalog.yaml` names, so it stays consistent with the data contract. It is the DESIGN, reviewable
pre-sign-off; the runnable language-bound code (R/SQL) is what stays withheld until sign-off (then it lands
in `code/` + `tests/`). Keep it distinct from the narrative `01-restatement.md`.

## The README router
A short table, one row per section file (mirror `docs/health/README.md`): `| File | Use it for |`.
Humans scan one row and open one file; agents do the same (lazy-load, no preload).

## Invariants
- The spec IS the artifact; runnable code stays withheld until sign-off (then status -> LOCKED).
- Every PENDING_LOCAL_DECISION appears in `build/pending-decisions.md` AND the exec checklist; every
  uncertain variable appears in `variable-catalog.yaml` as `status: unknown`.
- Keep each section file under the doc limit and at `####`+ headings; split further + add a README row if one grows.
