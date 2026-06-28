---
name: phenotype-gate
description: >-
  Runs the mandatory comprehension gate before ANY computable-phenotype or case-definition code:
  restates the algorithm in plain words, names the language traps, builds two-or-more worked examples
  and two-or-more boundary counter-examples, draws the ASCII decision and temporal diagrams, confirms
  data granularity and time-varying states, catalogs the input/derived/uncertain variables, writes
  language-agnostic implementable pseudocode, and withholds runnable code until explicit human sign-off.
  Use when the user asks to define cases, build a computable phenotype, identify patients by an algorithm,
  classify a condition from codes/labs/meds/time, or operationalize a published case definition.
  Operationalizes health/phenotyping.md. NOT for assembling a code set (use map-clinical-codes) nor for
  denominators, person-time, or incidence/prevalence (use design-indicator).
---

# /datavidence-healthanalysis:phenotype-gate

> Operationalizes `.claude/policies/health/phenotyping.md`. Apply `../_shared/health-principles.md`
> (math-by-tool, claim-to-evidence, PENDING_LOCAL_DECISION, comprehension-before-code) and emit the
> artifact per `../_shared/spec-artifact.md` (chapters + tabs, variable catalog, implementable
> pseudocode). This gate runs BEFORE `analysis/pseudocode-first.md`; runnable code is withheld until sign-off.

## When to use / when NOT to use
- Use it when: the user wants to turn codes/labs/meds/time into a yes/no (or state) label -- "define
  cases", "computable phenotype", "identify patients with X", "case definition", "algorithm to find".
- Do NOT use it when: assembling or validating the code set itself, use map-clinical-codes; building a
  denominator, person-time, or an incidence/prevalence indicator, use design-indicator. A phenotype
  consumes a code set and feeds an indicator; stay in lane.

## What it does: the comprehension gate (in order, no skipping)
Produce the phenotype-spec sections (see Output for the layout), then STOP for sign-off:
1. Restate inclusion + exclusion + time logic in plain words. Name the language traps: floors vs exact
   counts (at-least-3 is not exactly-3), span(last-minus-first) vs gap-between-events, anchor windows
   vs persistence.
2. Two-or-more worked examples (>=1 clear positive, >=1 clear negative), walked criterion-by-criterion.
3. Two-or-more counter-examples, each on a DIFFERENT boundary (one count threshold, one time window,
   one OR-criterion rescue); state the sensitivity/specificity trade-off each one exposes.
4. ASCII decision diagram: every branch and terminal outcome explicit (notation:
   `docs/health/ascii-timelines.md`, form 3).
5. ASCII temporal diagram: one per time-based criterion (forms 1, 2, 4). If the phenotype genuinely
   has no time logic (pure single-code ever-definition), state that instead of drawing an empty timeline.
6. Data granularity: confirm exact event day is available before any day-level rule; if month-only
   (masked extracts), specify a monthly state machine, not a day-level span.
7. Time-varying states: declare how recurrence, transplant then graft-failure then re-dialysis, death,
   and transfer start or end episodes; segment at declared gaps (never let max-minus-min merge episodes).
8. Validation plan: PPV (primary) + sensitivity/specificity via chart review (>=2 reviewers, random +
   stratified) and/or OHDSI PheValuator or CohortDiagnostics; portability; report per Wei et al. 2024.
9. Variable catalog (`variable-catalog.yaml`): one entry per variable the algorithm reads or builds.
   READ `metadata/data_dictionary.csv` + `contracts/*.yml` first -- a variable found there is
   `status: confirmed` with `source: table.column`; one built from others is `analytic_role: derived`
   with a `derivation:` recipe; one you cannot confirm is `analytic_role: uncertain`, `status: unknown`,
   marked `<<PENDING_CONFIRMATION_Qn>>` (an exploration target). Never invent a column.
10. Implementable pseudocode (`build/pseudocode.md`): a language-agnostic, code-like plan (FOR / FILTER /
    COUNT / IF span > 30 THEN INCLUDE ...) referencing the catalog variable names. Distinct from the
    narrative restatement; it is the reviewable DESIGN.
11. Human sign-off: an explicit affirmative that the restatement + diagrams + catalog + pseudocode match
    intent. Silence is not consent. Iterate until aligned. WITHHOLD runnable code until this is given.
12. Then the runnable code (R/SQL) + unit tests, each example and counter-example becoming an
    expected-classification fixture; flip the spec status to LOCKED.

Run the agent-runnable gate in `docs/health/checklists.md` (Phenotype comprehension gate); any "no" or
"unknown" is a stop. A full worked pass (maintenance dialysis) lives in `docs/health/phenotyping-examples.md`.

## Pairs with (repo policy)
- `.claude/policies/health/phenotyping.md` (the rule); prerequisite `health/code-mapping.md` (codes feed
  phenotypes); next-if time windows build indicators, go to `health/routinely-collected-data.md`.

## Rules / invariants
- Data granularity dictates the algorithm: never a day-level rule on month-only data.
- Borrowed is not validated: an external phenotype needs a transportability check; mark thresholds and
  codes PENDING_LOCAL_DECISION until the local protocol fixes them.
- Never reify the phenotype as a true biological subgroup: it is an operational definition with
  measurement error; carry that error into `analysis/sensitivity-analysis.md`.
- LLM may draft, never self-certify: this gate is the human-verification step (SHREC/PHEONA risk).
- Math by tool; anchor every code, threshold, and variable to the code set / data dictionary / protocol
  (no invention -- uncertain variables become `status: unknown`, not guesses).

## Output
Emit a spec artifact per `../_shared/spec-artifact.md`:
- Small phenotype (<= ~300 lines): one `<spec-dir>/phenotype-spec.md` plus an `index.qmd` that includes it.
- Large (the usual case): SPLIT into the indexed `<spec-dir>/` -- `comprehension/01..06`, `build/`
  (`variables.md`, `pseudocode.md`, `pending-decisions.md`), `validation/validation-plan.md`,
  `variable-catalog.yaml`, a `README.md` router, and `index.qmd` + `spec-theme.scss` copied from the child
  scaffold (`analysis/_spec-template.qmd`, R stack). `quarto render index.qmd` -> a chaptered, tabbed,
  academic + executive HTML (executive summary on top; section files use `####`+ headings only so tabs
  stay clean). The `comprehension/04-decision-diagram.md` + `05-timelines.md` names satisfy the
  `phenotype-timeline-gate`.
- No Quarto (non-R stack): ship the indexed `.md` set + README only.
- After sign-off: append `code/` + `tests/` (seeded from the examples/counter-examples) and flip the
  status badge to LOCKED. Runnable code stays withheld until then; the language-agnostic pseudocode does not.
